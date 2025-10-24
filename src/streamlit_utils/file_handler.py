"""
File Upload/Download Handler for Streamlit Application

Handles file validation, upload, and download operations.
Manages temporary file storage and cleanup.

Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - File Upload & Image Processing
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple
import io


# ============================================================================
# FILE CONSTRAINTS
# ============================================================================

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
ALLOWED_IMAGE_TYPES = {".tif", ".tiff", ".png", ".jpg", ".jpeg"}
ALLOWED_TIFF_TYPES = {".tif", ".tiff", ".qptiff"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_TIFF_TYPES

MIME_TYPES = {
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".qptiff": "image/tiff",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".csv": "text/csv",
    ".h5": "application/x-hdf",
}


# ============================================================================
# FILE VALIDATION
# ============================================================================

def validate_file(uploaded_file) -> Tuple[bool, str]:
    """
    Validate uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
        
    Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - Security
    """
    if uploaded_file is None:
        return False, "No file provided"
    
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        return False, f"File too large (>{MAX_FILE_SIZE / 1024 / 1024:.0f} MB)"
    
    # Check file extension
    file_ext = Path(uploaded_file.name).suffix.lower()
    if file_ext not in ALLOWED_TYPES:
        return False, f"Invalid file type: {file_ext}. Allowed: {ALLOWED_TYPES}"
    
    # Check file name
    if not uploaded_file.name or len(uploaded_file.name) > 255:
        return False, "Invalid file name"
    
    return True, ""


def validate_file_type(filepath: str, expected_type: str) -> Tuple[bool, str]:
    """
    Validate file type matches expected type.
    
    Args:
        filepath: Path to file
        expected_type: Expected file type (e.g., "tiff", "png")
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    file_ext = Path(filepath).suffix.lower()
    
    if expected_type == "tiff" and file_ext not in ALLOWED_TIFF_TYPES:
        return False, f"Expected TIFF file, got {file_ext}"
    
    if expected_type == "image" and file_ext not in ALLOWED_IMAGE_TYPES:
        return False, f"Expected image file, got {file_ext}"
    
    return True, ""


# ============================================================================
# FILE UPLOAD HANDLING
# ============================================================================

def save_uploaded_file(uploaded_file, temp_dir: Optional[str] = None) -> Optional[str]:
    """
    Save uploaded file to temporary directory.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        temp_dir: Optional temporary directory path
        
    Returns:
        str: Path to saved file, or None if error
        
    Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - File Upload
    """
    # Validate file
    is_valid, error_msg = validate_file(uploaded_file)
    if not is_valid:
        st.error(f"File validation failed: {error_msg}")
        return None
    
    try:
        # Create temp directory if not provided
        if temp_dir is None:
            temp_dir = tempfile.gettempdir()
        
        # Create subdirectory for this session
        session_dir = Path(temp_dir) / "streamlit_uploads"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        filepath = session_dir / uploaded_file.name
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return str(filepath)
    
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None


def load_file_as_bytes(filepath: str) -> Optional[bytes]:
    """
    Load file as bytes.
    
    Args:
        filepath: Path to file
        
    Returns:
        bytes: File contents, or None if error
    """
    try:
        with open(filepath, "rb") as f:
            return f.read()
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None


# ============================================================================
# FILE DOWNLOAD HANDLING
# ============================================================================

def create_download_button(
    label: str,
    data: bytes,
    filename: str,
    file_format: str = "csv"
) -> None:
    """
    Create download button for file.
    
    Args:
        label: Button label
        data: File data (bytes)
        filename: Filename for download
        file_format: File format (csv, png, h5, etc.)
        
    Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - Download Results
    """
    mime_type = MIME_TYPES.get(f".{file_format}", "application/octet-stream")
    
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime_type,
    )


def export_to_csv(data, filename: str = "results.csv") -> None:
    """
    Export data to CSV and create download button.
    
    Args:
        data: Pandas DataFrame or dict
        filename: Output filename
    """
    try:
        import pandas as pd
        
        if isinstance(data, dict):
            df = pd.DataFrame(data)
        else:
            df = data
        
        csv_data = df.to_csv(index=False).encode()
        create_download_button("📥 Download CSV", csv_data, filename, "csv")
    
    except Exception as e:
        st.error(f"Error exporting to CSV: {str(e)}")


def export_to_hdf5(data, filename: str = "results.h5") -> None:
    """
    Export data to HDF5 and create download button.
    
    Args:
        data: Data to export
        filename: Output filename
    """
    try:
        import h5py
        import io
        
        # Create in-memory HDF5 file
        buffer = io.BytesIO()
        with h5py.File(buffer, "w") as f:
            if isinstance(data, dict):
                for key, value in data.items():
                    f.create_dataset(key, data=value)
            else:
                f.create_dataset("data", data=data)
        
        buffer.seek(0)
        create_download_button("📥 Download HDF5", buffer.getvalue(), filename, "h5")
    
    except Exception as e:
        st.error(f"Error exporting to HDF5: {str(e)}")


# ============================================================================
# TEMPORARY FILE MANAGEMENT
# ============================================================================

def cleanup_temp_files(temp_dir: Optional[str] = None) -> None:
    """
    Clean up temporary files.
    
    Args:
        temp_dir: Temporary directory to clean
    """
    if temp_dir is None:
        temp_dir = Path(tempfile.gettempdir()) / "streamlit_uploads"
    
    try:
        import shutil
        if Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
    except Exception as e:
        st.warning(f"Error cleaning up temp files: {str(e)}")


def get_temp_file_size(temp_dir: Optional[str] = None) -> int:
    """
    Get total size of temporary files.
    
    Args:
        temp_dir: Temporary directory
        
    Returns:
        int: Total size in bytes
    """
    if temp_dir is None:
        temp_dir = Path(tempfile.gettempdir()) / "streamlit_uploads"
    
    total_size = 0
    try:
        for filepath in Path(temp_dir).rglob("*"):
            if filepath.is_file():
                total_size += filepath.stat().st_size
    except Exception:
        pass
    
    return total_size


# ============================================================================
# FILE UTILITIES
# ============================================================================

def get_file_info(filepath: str) -> dict:
    """
    Get file information.
    
    Args:
        filepath: Path to file
        
    Returns:
        dict: File information
    """
    try:
        path = Path(filepath)
        return {
            "name": path.name,
            "size": path.stat().st_size,
            "size_mb": path.stat().st_size / 1024 / 1024,
            "extension": path.suffix,
            "exists": path.exists(),
        }
    except Exception as e:
        return {"error": str(e)}


def format_file_size(size_bytes: int) -> str:
    """
    Format file size for display.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size (e.g., "10.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


"""
Reusable UI Components for Streamlit Application

Provides common UI components used across multiple pages.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - UI Components Library
"""

import streamlit as st
from typing import Optional, List, Any, Callable
import pandas as pd


# ============================================================================
# FILE UPLOAD COMPONENTS
# ============================================================================

def file_upload_widget(
    label: str = "Upload File",
    file_types: List[str] = None,
    accept_multiple: bool = False,
    help_text: str = ""
):
    """
    File upload widget with validation.
    
    Args:
        label: Widget label
        file_types: Allowed file types (e.g., ["tif", "tiff", "png"])
        accept_multiple: Allow multiple files
        help_text: Help text to display
        
    Returns:
        Uploaded file(s)
    """
    if file_types is None:
        file_types = ["tif", "tiff", "png", "jpg"]
    
    return st.file_uploader(
        label=label,
        type=file_types,
        accept_multiple_files=accept_multiple,
        help=help_text,
    )


# ============================================================================
# PARAMETER INPUT COMPONENTS
# ============================================================================

def parameter_slider(
    name: str,
    min_val: int = 0,
    max_val: int = 255,
    default: int = 100,
    step: int = 1,
    help_text: str = ""
) -> int:
    """
    Configurable slider with validation.
    
    Args:
        name: Parameter name
        min_val: Minimum value
        max_val: Maximum value
        default: Default value
        step: Step size
        help_text: Help text
        
    Returns:
        int: Selected value
    """
    return st.slider(
        label=name,
        min_value=min_val,
        max_value=max_val,
        value=default,
        step=step,
        help=help_text,
    )


def parameter_number_input(
    name: str,
    min_val: float = 0.0,
    max_val: float = 100.0,
    default: float = 50.0,
    step: float = 1.0,
    help_text: str = ""
) -> float:
    """
    Number input widget.
    
    Args:
        name: Parameter name
        min_val: Minimum value
        max_val: Maximum value
        default: Default value
        step: Step size
        help_text: Help text
        
    Returns:
        float: Entered value
    """
    return st.number_input(
        label=name,
        min_value=min_val,
        max_value=max_val,
        value=default,
        step=step,
        help=help_text,
    )


def parameter_selectbox(
    name: str,
    options: List[str],
    default: int = 0,
    help_text: str = ""
) -> str:
    """
    Dropdown selector widget.
    
    Args:
        name: Parameter name
        options: List of options
        default: Default index
        help_text: Help text
        
    Returns:
        str: Selected option
    """
    return st.selectbox(
        label=name,
        options=options,
        index=default,
        help=help_text,
    )


# ============================================================================
# PROGRESS TRACKING COMPONENTS
# ============================================================================

def progress_tracker(
    steps: List[str],
    current_step: int
) -> None:
    """
    Multi-step progress indicator.
    
    Args:
        steps: List of step names
        current_step: Current step index (0-based)
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        progress = (current_step + 1) / len(steps)
        st.progress(progress)
    
    with col2:
        st.metric("Step", f"{current_step + 1}/{len(steps)}")
    
    # Display step names
    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i == current_step:
                st.markdown(f"**→ {step}**")
            elif i < current_step:
                st.markdown(f"✓ {step}")
            else:
                st.markdown(f"○ {step}")


def status_indicator(
    status: str,
    message: str = ""
) -> None:
    """
    Status indicator with message.
    
    Args:
        status: Status type ("success", "error", "warning", "info")
        message: Status message
    """
    if status == "success":
        st.success(message or "✓ Success")
    elif status == "error":
        st.error(message or "✗ Error")
    elif status == "warning":
        st.warning(message or "⚠ Warning")
    else:
        st.info(message or "ℹ Info")


# ============================================================================
# IMAGE DISPLAY COMPONENTS
# ============================================================================

def image_viewer(
    image: Any,
    title: str = "Image",
    width: int = 400,
    caption: str = ""
) -> None:
    """
    Image display with caption.
    
    Args:
        image: Image array or file path
        title: Image title
        width: Display width
        caption: Image caption
    """
    st.markdown(f"**{title}**")
    st.image(image, caption=caption, width=width, use_column_width=False)


def side_by_side_images(
    image1: Any,
    image2: Any,
    title1: str = "Image 1",
    title2: str = "Image 2",
    caption1: str = "",
    caption2: str = ""
) -> None:
    """
    Display two images side by side.
    
    Args:
        image1: First image
        image2: Second image
        title1: First image title
        title2: Second image title
        caption1: First image caption
        caption2: Second image caption
    """
    col1, col2 = st.columns(2)
    
    with col1:
        image_viewer(image1, title1, caption=caption1)
    
    with col2:
        image_viewer(image2, title2, caption=caption2)


# ============================================================================
# DATA DISPLAY COMPONENTS
# ============================================================================

def results_table(
    data: pd.DataFrame,
    title: str = "Results",
    show_index: bool = False
) -> None:
    """
    Formatted results table.
    
    Args:
        data: Pandas DataFrame
        title: Table title
        show_index: Show index column
    """
    st.markdown(f"**{title}**")
    st.dataframe(data, use_container_width=True, hide_index=not show_index)


def metrics_row(
    metrics: dict,
    columns: int = 4
) -> None:
    """
    Display metrics in a row.
    
    Args:
        metrics: Dict of {name: value}
        columns: Number of columns
    """
    cols = st.columns(columns)
    for i, (name, value) in enumerate(metrics.items()):
        with cols[i % columns]:
            st.metric(name, value)


# ============================================================================
# DOWNLOAD COMPONENTS
# ============================================================================

def download_button(
    data: Any,
    filename: str,
    format: str = "csv",
    label: str = "📥 Download"
) -> None:
    """
    Download button with format options.
    
    Args:
        data: Data to download
        filename: Output filename
        format: File format (csv, png, h5)
        label: Button label
    """
    from streamlit_utils.file_handler import (
        export_to_csv,
        export_to_hdf5,
        create_download_button,
    )
    
    if format == "csv":
        export_to_csv(data, filename)
    elif format == "h5":
        export_to_hdf5(data, filename)
    else:
        st.warning(f"Unsupported format: {format}")


# ============================================================================
# FORM COMPONENTS
# ============================================================================

def parameter_form(
    parameters: dict,
    on_submit: Callable = None
) -> dict:
    """
    Create parameter input form.
    
    Args:
        parameters: Dict of {name: {type, min, max, default}}
        on_submit: Callback function on submit
        
    Returns:
        dict: Updated parameters
    """
    with st.form("parameter_form"):
        updated_params = {}
        
        for name, config in parameters.items():
            param_type = config.get("type", "slider")
            
            if param_type == "slider":
                updated_params[name] = parameter_slider(
                    name,
                    config.get("min", 0),
                    config.get("max", 255),
                    config.get("default", 100),
                )
            elif param_type == "number":
                updated_params[name] = parameter_number_input(
                    name,
                    config.get("min", 0.0),
                    config.get("max", 100.0),
                    config.get("default", 50.0),
                )
            elif param_type == "select":
                updated_params[name] = parameter_selectbox(
                    name,
                    config.get("options", []),
                )
        
        if st.form_submit_button("Apply Parameters"):
            if on_submit:
                on_submit(updated_params)
            return updated_params
    
    return {}


# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def section_header(title: str, icon: str = "📋") -> None:
    """
    Display section header.
    
    Args:
        title: Section title
        icon: Icon emoji
    """
    st.markdown(f"## {icon} {title}")
    st.markdown("---")


def info_box(title: str, content: str, icon: str = "ℹ") -> None:
    """
    Display info box.
    
    Args:
        title: Box title
        content: Box content
        icon: Icon emoji
    """
    st.info(f"**{icon} {title}**\n\n{content}")


def warning_box(title: str, content: str) -> None:
    """
    Display warning box.
    
    Args:
        title: Box title
        content: Box content
    """
    st.warning(f"**⚠ {title}**\n\n{content}")


def success_box(title: str, content: str) -> None:
    """
    Display success box.
    
    Args:
        title: Box title
        content: Box content
    """
    st.success(f"**✓ {title}**\n\n{content}")


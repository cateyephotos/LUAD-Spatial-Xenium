"""
Session State Management for Streamlit Application

Handles initialization, validation, and management of session state.
Ensures consistent state across page reruns.

Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - Session State Management
"""

import streamlit as st
from typing import Any, Dict, Optional


# ============================================================================
# STATE INITIALIZATION
# ============================================================================

def init_session_state() -> None:
    """
    Initialize all session state variables.
    
    Called once per session to set up default values.
    Safe to call multiple times - only initializes if key doesn't exist.
    
    Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Session State Structure
    """
    
    # Workflow state
    if "workflow_step" not in st.session_state:
        st.session_state.workflow_step = 0
    
    if "project_name" not in st.session_state:
        st.session_state.project_name = ""
    
    # Data state
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = {}
    
    if "data_sources" not in st.session_state:
        st.session_state.data_sources = []
    
    if "current_sample" not in st.session_state:
        st.session_state.current_sample = None
    
    # Processing state
    if "parameters" not in st.session_state:
        st.session_state.parameters = {}
    
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = {}
    
    if "generated_masks" not in st.session_state:
        st.session_state.generated_masks = {}
    
    if "processing_logs" not in st.session_state:
        st.session_state.processing_logs = []
    
    # Alignment state
    if "alignment_params" not in st.session_state:
        st.session_state.alignment_params = {}
    
    if "alignment_result" not in st.session_state:
        st.session_state.alignment_result = None
    
    if "aligned_masks" not in st.session_state:
        st.session_state.aligned_masks = {}
    
    # Analysis state
    if "correlation_matrix" not in st.session_state:
        st.session_state.correlation_matrix = None
    
    if "clustering_result" not in st.session_state:
        st.session_state.clustering_result = None
    
    if "roi_data" not in st.session_state:
        st.session_state.roi_data = None
    
    # Results state
    if "results_summary" not in st.session_state:
        st.session_state.results_summary = {}
    
    # UI state
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False


# ============================================================================
# STATE GETTERS
# ============================================================================

def get_workflow_step() -> int:
    """Get current workflow step (0-6)."""
    return st.session_state.get("workflow_step", 0)


def get_project_name() -> str:
    """Get current project name."""
    return st.session_state.get("project_name", "")


def get_uploaded_files() -> Dict[str, Any]:
    """Get dictionary of uploaded files."""
    return st.session_state.get("uploaded_files", {})


def get_current_sample() -> Optional[str]:
    """Get currently selected sample."""
    return st.session_state.get("current_sample", None)


def get_parameters() -> Dict[str, Any]:
    """Get current processing parameters."""
    return st.session_state.get("parameters", {})


def get_processing_status() -> Dict[str, str]:
    """Get processing status for each modality."""
    return st.session_state.get("processing_status", {})


def get_generated_masks() -> Dict[str, Any]:
    """Get generated mask arrays."""
    return st.session_state.get("generated_masks", {})


def get_alignment_result() -> Optional[Dict[str, Any]]:
    """Get alignment result (transformation matrix + fitness)."""
    return st.session_state.get("alignment_result", None)


def get_results_summary() -> Dict[str, Any]:
    """Get results summary."""
    return st.session_state.get("results_summary", {})


# ============================================================================
# STATE SETTERS
# ============================================================================

def set_workflow_step(step: int) -> None:
    """Set current workflow step."""
    if 0 <= step <= 6:
        st.session_state.workflow_step = step
    else:
        raise ValueError(f"Invalid workflow step: {step}. Must be 0-6.")


def set_project_name(name: str) -> None:
    """Set project name."""
    st.session_state.project_name = name


def set_current_sample(sample: Optional[str]) -> None:
    """Set currently selected sample."""
    st.session_state.current_sample = sample


def set_parameters(params: Dict[str, Any]) -> None:
    """Set processing parameters."""
    st.session_state.parameters = params


def add_uploaded_file(key: str, file_data: Any) -> None:
    """Add uploaded file to state."""
    st.session_state.uploaded_files[key] = file_data


def clear_uploaded_files() -> None:
    """Clear all uploaded files."""
    st.session_state.uploaded_files = {}


def add_processing_log(message: str) -> None:
    """Add message to processing logs."""
    st.session_state.processing_logs.append(message)


def clear_processing_logs() -> None:
    """Clear all processing logs."""
    st.session_state.processing_logs = []


# ============================================================================
# STATE VALIDATION
# ============================================================================

def validate_state() -> bool:
    """
    Validate current session state.
    
    Returns:
        bool: True if state is valid, False otherwise
    """
    try:
        # Check workflow step
        step = get_workflow_step()
        if not isinstance(step, int) or step < 0 or step > 6:
            return False
        
        # Check parameters
        params = get_parameters()
        if not isinstance(params, dict):
            return False
        
        # Check uploaded files
        files = get_uploaded_files()
        if not isinstance(files, dict):
            return False
        
        return True
    except Exception:
        return False


# ============================================================================
# STATE RESET
# ============================================================================

def reset_session_state() -> None:
    """Reset all session state to defaults."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


def reset_workflow() -> None:
    """Reset workflow to step 0."""
    st.session_state.workflow_step = 0
    st.session_state.uploaded_files = {}
    st.session_state.parameters = {}
    st.session_state.processing_status = {}
    st.session_state.generated_masks = {}
    st.session_state.alignment_result = None
    st.session_state.results_summary = {}


# ============================================================================
# STATE UTILITIES
# ============================================================================

def get_state_summary() -> Dict[str, Any]:
    """Get summary of current state."""
    return {
        "workflow_step": get_workflow_step(),
        "project_name": get_project_name(),
        "num_uploaded_files": len(get_uploaded_files()),
        "current_sample": get_current_sample(),
        "num_parameters": len(get_parameters()),
        "processing_status": get_processing_status(),
        "has_alignment_result": get_alignment_result() is not None,
    }


def is_workflow_complete() -> bool:
    """Check if workflow is complete (step 6)."""
    return get_workflow_step() == 6


def can_proceed_to_next_step() -> bool:
    """Check if user can proceed to next workflow step."""
    step = get_workflow_step()
    
    # Step 0 (Home) -> always can proceed
    if step == 0:
        return True
    
    # Step 1 (Load Data) -> need uploaded files
    if step == 1:
        return len(get_uploaded_files()) > 0
    
    # Step 2 (Configure) -> need parameters
    if step == 2:
        return len(get_parameters()) > 0
    
    # Step 3 (Process) -> need generated masks
    if step == 3:
        return len(get_generated_masks()) > 0
    
    # Step 4 (Align) -> need alignment result
    if step == 4:
        return get_alignment_result() is not None
    
    # Step 5 (Analyze) -> always can proceed
    if step == 5:
        return True
    
    return False


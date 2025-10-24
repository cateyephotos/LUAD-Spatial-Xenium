"""
LUAD Spatial Omics Integration - Streamlit Web Interface

Main entry point for the Streamlit application.
Handles page configuration, session state initialization, and navigation.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md
"""

import streamlit as st
from pathlib import Path
import sys

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from streamlit_utils.state_manager import init_session_state

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="LUAD Spatial Omics Integration",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# CUSTOM STYLING
# ============================================================================

st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

init_session_state()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    st.title("🔬 LUAD Spatial Omics")
    st.markdown("---")
    
    # Project info
    st.markdown("### Project Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Phase", "0 - GUI")
    with col2:
        st.metric("Status", "Development")
    
    st.markdown("---")
    
    # Navigation
    st.markdown("### Navigation")
    st.markdown("""
    Use the page selector above to navigate between:
    - **Home** - Overview and quick start
    - **Load Data** - Upload spatial data files
    - **Configure** - Set processing parameters
    - **Process** - Generate masks
    - **Align** - Align images
    - **Analyze** - Correlation and clustering
    - **Results** - View and export results
    """)
    
    st.markdown("---")
    
    # Workflow progress
    st.markdown("### Workflow Progress")
    workflow_step = st.session_state.get("workflow_step", 0)
    progress = (workflow_step + 1) / 7
    st.progress(progress, text=f"Step {workflow_step + 1}/7")
    
    st.markdown("---")
    
    # Help and documentation
    st.markdown("### Documentation")
    st.markdown("""
    📖 [Technical Guidelines](https://github.com/cateyephotos/LUAD-Spatial-Xenium)
    📋 [Implementation Plan](https://github.com/cateyephotos/LUAD-Spatial-Xenium)
    🔗 [GitHub Repository](https://github.com/cateyephotos/LUAD-Spatial-Xenium)
    """)

# ============================================================================
# MAIN CONTENT
# ============================================================================

st.title("🔬 LUAD Spatial Omics Integration")
st.markdown("""
    Align and integrate spatial omics data from multiple modalities:
    - **10x Xenium** - Subcellular spatial transcriptomics
    - **Visium** - Spatial transcriptomics
    - **PhenoCycler** - Multiplexed immunofluorescence
    - **Generic OME-TIFF** - Custom spatial data
""")

st.markdown("---")

# Welcome message
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Welcome to the Spatial Omics Integration Pipeline
    
    This application provides an interactive interface for:
    1. **Loading** spatial data from multiple modalities
    2. **Configuring** processing parameters
    3. **Generating** tissue masks
    4. **Aligning** images between modalities
    5. **Analyzing** correlations and clustering
    6. **Exporting** results in multiple formats
    
    **Get Started**: Navigate to the "Load Data" page to begin.
    """)

with col2:
    st.info("""
    **Phase 0 Status**
    
    ✅ App structure
    ✅ Pages created
    ✅ State management
    ⏳ Backend integration
    
    **Timeline**: Weeks 1-2
    """)

st.markdown("---")

# Quick stats
st.markdown("### Quick Stats")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Supported Modalities", "4+")

with col2:
    st.metric("Processing Steps", "7")

with col3:
    st.metric("Export Formats", "3+")

with col4:
    st.metric("Max File Size", "500 MB")

st.markdown("---")

# Features
st.markdown("### Key Features")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📁 File Management**
    - Drag-and-drop upload
    - Multi-file support
    - File validation
    - Progress tracking
    """)

with col2:
    st.markdown("""
    **⚙️ Configuration**
    - Real-time validation
    - Preset configurations
    - Parameter descriptions
    - Range constraints
    """)

with col3:
    st.markdown("""
    **📊 Visualization**
    - Image display
    - Interactive charts
    - Data tables
    - Results gallery
    """)

st.markdown("---")

# Footer
st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8rem; margin-top: 2rem;'>
    LUAD Spatial Omics Integration | Phase 0 - GUI Foundation | 2025-10-23
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# DEBUG INFO (Development only)
# ============================================================================

if st.session_state.get("debug_mode", False):
    with st.expander("🔧 Debug Info"):
        st.write("Session State:")
        st.json(dict(st.session_state))


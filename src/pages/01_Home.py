"""
Home Page - Welcome and Overview

Displays welcome message, project overview, and quick start guide.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 1: Home
"""

import streamlit as st
from pathlib import Path
import sys

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step
from ui.components import section_header, info_box, success_box

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Home - LUAD Spatial Omics",
    page_icon="🏠",
    layout="wide",
)

# ============================================================================
# PAGE CONTENT
# ============================================================================

st.title("🏠 Welcome to LUAD Spatial Omics Integration")

section_header("Project Overview", "📋")

st.markdown("""
This application provides an interactive pipeline for integrating spatial omics data 
from multiple modalities:

- **10x Xenium** - Subcellular spatial transcriptomics (~0.5 µm resolution)
- **Visium** - Spatial transcriptomics (~100 µm resolution)
- **PhenoCycler** - Multiplexed immunofluorescence (~0.3 µm resolution)
- **Generic OME-TIFF** - Custom spatial data formats

The pipeline enables alignment and integration of these modalities for comprehensive 
spatial analysis of lung adenocarcinoma (LUAD) tissue samples.
""")

section_header("Workflow Steps", "🔄")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 7-Step Workflow
    
    1. **Load Data** - Upload spatial data files from your modality
    2. **Configure** - Set processing parameters
    3. **Process** - Generate tissue masks
    4. **Align** - Align images between modalities
    5. **Analyze** - Correlation and clustering analysis
    6. **Results** - View and export results
    """)

with col2:
    st.info("""
    **Quick Start**
    
    1. Click "Load Data" →
    2. Upload your files
    3. Configure parameters
    4. Run pipeline
    5. View results
    """)

section_header("Key Features", "✨")

col1, col2, col3 = st.columns(3)

with col1:
    success_box(
        "📁 File Management",
        "Drag-and-drop upload, multi-file support, automatic validation"
    )

with col2:
    success_box(
        "⚙️ Configuration",
        "Real-time parameter validation, preset configurations, descriptions"
    )

with col3:
    success_box(
        "📊 Visualization",
        "Interactive charts, image display, results gallery"
    )

section_header("Supported Data Formats", "📦")

formats_data = {
    "Modality": ["Xenium", "Visium", "PhenoCycler", "Generic"],
    "Format": ["OME-TIFF", "PNG", "QPTIFF", "OME-TIFF"],
    "Resolution": ["0.5 µm", "100 µm", "0.3 µm", "Variable"],
    "Status": ["✓ Supported", "✓ Supported", "✓ Supported", "✓ Supported"],
}

import pandas as pd
df = pd.DataFrame(formats_data)
st.dataframe(df, use_container_width=True, hide_index=True)

section_header("Getting Started", "🚀")

st.markdown("""
### Step 1: Prepare Your Data
- Ensure your files are in supported format (TIFF, PNG, QPTIFF)
- File size limit: 500 MB per file
- Recommended: Organize files by modality

### Step 2: Load Data
- Navigate to "Load Data" page
- Select your data modality
- Upload your files
- Verify file preview

### Step 3: Configure Parameters
- Navigate to "Configure" page
- Review default parameters
- Adjust based on your data
- Save configuration

### Step 4: Process
- Navigate to "Process" page
- Generate tissue masks
- Monitor progress
- Review mask quality

### Step 5: Align
- Navigate to "Align" page
- Configure alignment parameters
- Run alignment
- Review alignment quality

### Step 6: Analyze
- Navigate to "Analyze" page
- View correlation analysis
- Explore clustering results
- Extract regions of interest

### Step 7: Export Results
- Navigate to "Results" page
- Review summary statistics
- Download results in desired format
- Export visualization gallery
""")

section_header("Documentation", "📖")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Technical Guidelines**
    - Caching strategies
    - Session state management
    - File upload handling
    - Performance optimization
    """)

with col2:
    st.markdown("""
    **Implementation Details**
    - App architecture
    - Page specifications
    - UI components
    - Testing approach
    """)

with col3:
    st.markdown("""
    **Project Resources**
    - GitHub repository
    - Issue tracker
    - Documentation
    - Community forum
    """)

section_header("Phase 0 Status", "📊")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Phase", "0 - GUI")

with col2:
    st.metric("Status", "Development")

with col3:
    st.metric("Pages", "7/7")

with col4:
    st.metric("Timeline", "Weeks 1-2")

section_header("Next Steps", "⏭️")

col1, col2 = st.columns(2)

with col1:
    if st.button("📂 Go to Load Data", use_container_width=True):
        set_workflow_step(1)
        st.switch_page("pages/02_Load_Data.py")

with col2:
    if st.button("⚙️ Go to Configure", use_container_width=True):
        set_workflow_step(2)
        st.switch_page("pages/03_Configure.py")

st.markdown("---")

st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8rem;'>
LUAD Spatial Omics Integration | Phase 0 - GUI Foundation | 2025-10-23
</div>
""", unsafe_allow_html=True)


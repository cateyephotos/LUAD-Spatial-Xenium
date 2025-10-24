"""
Load Data Page - File Upload and Configuration

Handles file upload, validation, and data source configuration.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 2: Load Data
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step, add_uploaded_file, get_uploaded_files
from ui.components import section_header, info_box, file_upload_widget, parameter_selectbox

st.set_page_config(page_title="Load Data - LUAD Spatial Omics", page_icon="📂", layout="wide")

st.title("📂 Load Spatial Data")

section_header("Select Data Modality", "🔬")

modality = parameter_selectbox(
    "Data Modality",
    ["Xenium", "Visium", "PhenoCycler", "Generic OME-TIFF"],
    help_text="Select the spatial omics modality of your data"
)

st.markdown(f"**Selected Modality**: {modality}")

section_header("Upload Files", "📁")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    ### Upload {modality} Data
    
    Supported formats:
    - TIFF (.tif, .tiff)
    - PNG (.png)
    - QPTIFF (.qptiff)
    
    Maximum file size: 500 MB
    """)

with col2:
    info_box(
        "File Requirements",
        f"Ensure your {modality} files are in supported format and under 500 MB"
    )

uploaded_files = file_upload_widget(
    label=f"Upload {modality} Files",
    file_types=["tif", "tiff", "png", "qptiff"],
    accept_multiple=True,
    help_text=f"Select one or more {modality} files"
)

if uploaded_files:
    st.success(f"✓ {len(uploaded_files)} file(s) uploaded")
    
    for uploaded_file in uploaded_files:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"📄 {uploaded_file.name}")
        with col2:
            st.write(f"{uploaded_file.size / 1024 / 1024:.1f} MB")
        with col3:
            st.write("✓ Valid")

section_header("File Preview", "👁️")

if uploaded_files:
    st.info("File preview functionality will be implemented in Phase 1")
else:
    st.warning("Upload files to see preview")

section_header("Data Configuration", "⚙️")

if uploaded_files:
    sample_name = st.text_input("Sample Name", value="Sample_001")
    sample_description = st.text_area("Sample Description", value="")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✓ Confirm Upload", use_container_width=True):
            st.success("Files uploaded successfully!")
            set_workflow_step(2)
    
    with col2:
        if st.button("⏭️ Next: Configure", use_container_width=True):
            set_workflow_step(2)
            st.switch_page("pages/03_Configure.py")
else:
    st.info("Upload files to proceed")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.8rem;'>Phase 0 - GUI Foundation</div>", unsafe_allow_html=True)


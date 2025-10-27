"""
Load Data Page - File Upload and Configuration

Handles file upload, validation, and data source configuration with backend integration.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 2: Load Data
"""

import streamlit as st
from pathlib import Path
import sys
import logging
import tempfile
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step, add_uploaded_file, get_uploaded_files
from ui.components import section_header, info_box, file_upload_widget, parameter_selectbox
from core.data_factory import create_spatial_data

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

section_header("Load Data", "⚙️")

if uploaded_files:
    if st.button("📥 Load Data", use_container_width=True):
        try:
            with st.spinner("Loading data..."):
                # Create temporary directory for uploaded files
                temp_dir = tempfile.mkdtemp()

                # Save uploaded files to temp directory
                file_paths = []
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    file_paths.append(file_path)

                # Load data using factory
                spatial_data = create_spatial_data(temp_dir)

                if spatial_data is None:
                    st.error("❌ Failed to load data. Please check file format and try again.")
                else:
                    # Store in session state
                    st.session_state.loaded_data = spatial_data
                    st.session_state.data_path = temp_dir
                    st.session_state.data_modality = modality

                    st.success("✓ Data loaded successfully!")

                    # Display data information
                    st.subheader("Data Information")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Modality", spatial_data.modality)
                    with col2:
                        st.metric("Resolution", f"{spatial_data.resolution:.4f} µm/px")
                    with col3:
                        st.metric("Channels", len(spatial_data.channel_names))

                    # Display channel names
                    st.write("**Channels:**")
                    st.write(", ".join(spatial_data.channel_names))

        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            logging.error(f"Data loading error: {e}", exc_info=True)

section_header("Load Second Dataset (Optional)", "🔄")

st.info("Load a second dataset for alignment (e.g., PhenoCycler to align with Xenium)")

uploaded_files_2 = file_upload_widget(
    label="Upload Second Dataset (Optional)",
    file_types=["tif", "tiff", "png", "qptiff"],
    accept_multiple=True,
    help_text="Select files for second dataset",
    key="second_dataset"
)

if uploaded_files_2:
    if st.button("📥 Load Second Dataset", use_container_width=True):
        try:
            with st.spinner("Loading second dataset..."):
                # Create temporary directory for uploaded files
                temp_dir_2 = tempfile.mkdtemp()

                # Save uploaded files to temp directory
                for uploaded_file in uploaded_files_2:
                    file_path = os.path.join(temp_dir_2, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                # Load data using factory
                spatial_data_2 = create_spatial_data(temp_dir_2)

                if spatial_data_2 is None:
                    st.error("❌ Failed to load second dataset. Please check file format and try again.")
                else:
                    # Store in session state
                    st.session_state.moving_data = spatial_data_2
                    st.session_state.moving_data_path = temp_dir_2

                    st.success("✓ Second dataset loaded successfully!")

                    # Display data information
                    st.subheader("Second Dataset Information")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Modality", spatial_data_2.modality)
                    with col2:
                        st.metric("Resolution", f"{spatial_data_2.resolution:.4f} µm/px")
                    with col3:
                        st.metric("Channels", len(spatial_data_2.channel_names))

        except Exception as e:
            st.error(f"❌ Error loading second dataset: {str(e)}")
            logging.error(f"Second dataset loading error: {e}", exc_info=True)

section_header("Workflow Actions", "🎬")

col1, col2 = st.columns(2)

with col1:
    if 'loaded_data' in st.session_state and st.session_state.loaded_data is not None:
        if st.button("⏭️ Next: Configure", use_container_width=True):
            set_workflow_step(2)
            st.switch_page("pages/03_Configure.py")
    else:
        st.button("⏭️ Next: Configure", use_container_width=True, disabled=True)

with col2:
    if st.button("🔄 Reload", use_container_width=True):
        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.8rem;'>Phase 0 - GUI Foundation</div>", unsafe_allow_html=True)


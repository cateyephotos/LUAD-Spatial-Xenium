"""
Configure Page - Parameter Configuration

Handles processing parameter configuration and presets.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 3: Configure
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step, set_parameters
from ui.components import section_header, parameter_slider, parameter_selectbox

st.set_page_config(page_title="Configure - LUAD Spatial Omics", page_icon="⚙️", layout="wide")

st.title("⚙️ Configure Processing Parameters")

section_header("Preset Configurations", "📋")

preset = parameter_selectbox(
    "Select Preset",
    ["Custom", "Xenium Default", "Visium Default", "PhenoCycler Default"],
    help_text="Choose a preset configuration or customize manually"
)

section_header("Binarization Parameters", "🎯")

with st.expander("Binarization Settings", expanded=True):
    threshold = parameter_slider(
        "Binary Threshold",
        min_val=0,
        max_val=255,
        default=160,
        help_text="Threshold for image binarization"
    )
    
    st.info(f"Current threshold: {threshold}")

section_header("Morphology Parameters", "🔧")

with st.expander("Morphology Settings", expanded=True):
    kernel_size = parameter_slider(
        "Kernel Size",
        min_val=1,
        max_val=10,
        default=2,
        help_text="Size of morphological kernel"
    )
    
    dilate_iter = parameter_slider(
        "Dilate Iterations",
        min_val=1,
        max_val=20,
        default=5,
        help_text="Number of dilation iterations"
    )
    
    erode_iter = parameter_slider(
        "Erode Iterations",
        min_val=1,
        max_val=20,
        default=10,
        help_text="Number of erosion iterations"
    )

section_header("Alignment Parameters", "🔄")

with st.expander("Alignment Settings", expanded=False):
    zoom_range = parameter_slider(
        "Zoom Range (%)",
        min_val=1,
        max_val=50,
        default=10,
        help_text="Zoom search range"
    )
    
    shift_range = parameter_slider(
        "Shift Range (pixels)",
        min_val=1,
        max_val=100,
        default=50,
        help_text="Shift search range"
    )
    
    rotation_range = parameter_slider(
        "Rotation Range (degrees)",
        min_val=1,
        max_val=90,
        default=15,
        help_text="Rotation search range"
    )

section_header("Advanced Parameters", "🔬")

with st.expander("Advanced Settings", expanded=False):
    st.info("Advanced parameters will be available in Phase 1")

section_header("Parameter Summary", "📊")

params = {
    "Threshold": threshold,
    "Kernel Size": kernel_size,
    "Dilate Iterations": dilate_iter,
    "Erode Iterations": erode_iter,
    "Zoom Range": f"{zoom_range}%",
    "Shift Range": f"{shift_range}px",
    "Rotation Range": f"{rotation_range}°",
}

import pandas as pd
df = pd.DataFrame(list(params.items()), columns=["Parameter", "Value"])
st.dataframe(df, use_container_width=True, hide_index=True)

section_header("Actions", "🎬")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Configuration", use_container_width=True):
        set_parameters(params)
        st.success("Configuration saved!")

with col2:
    if st.button("⏭️ Next: Process", use_container_width=True):
        set_parameters(params)
        set_workflow_step(3)
        st.switch_page("pages/04_Process.py")

with col3:
    if st.button("↩️ Back: Load Data", use_container_width=True):
        set_workflow_step(1)
        st.switch_page("pages/02_Load_Data.py")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.8rem;'>Phase 0 - GUI Foundation</div>", unsafe_allow_html=True)


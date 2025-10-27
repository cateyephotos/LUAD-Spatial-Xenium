"""
Configure Page - Parameter Configuration

Handles processing parameter configuration and presets with backend integration.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 3: Configure
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step, set_parameters
from ui.components import section_header, parameter_slider, parameter_selectbox

st.set_page_config(page_title="Configure - LUAD Spatial Omics", page_icon="⚙️", layout="wide")

st.title("⚙️ Configure Processing Parameters")

# Check if data is loaded
if 'loaded_data' not in st.session_state or st.session_state.loaded_data is None:
    st.error("❌ No data loaded. Please load data on the 'Load Data' page first.")
    st.stop()

# Display current data info
section_header("Current Data", "📊")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Modality", st.session_state.loaded_data.modality)
with col2:
    st.metric("Resolution", f"{st.session_state.loaded_data.resolution:.4f} µm/px")
with col3:
    st.metric("Channels", len(st.session_state.loaded_data.channel_names))

section_header("Mask Generation Parameters", "🎯")

with st.expander("Mask Generation Settings", expanded=True):
    mask_method = st.selectbox(
        "Mask Generation Method",
        ["auto", "intensity", "polygon", "circle"],
        help_text="Auto: Select based on data type"
    )

    threshold = parameter_slider(
        "Binary Threshold",
        min_val=0,
        max_val=255,
        default=160,
        help_text="Threshold for image binarization"
    )

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
    feature_detector = st.selectbox(
        "Feature Detector",
        ["sift", "orb", "akaze"],
        help_text="Algorithm for feature detection"
    )

    max_features = st.slider(
        "Max Features",
        min_value=100,
        max_value=1000,
        value=500,
        step=100,
        help_text="Maximum number of features to detect"
    )

    match_ratio = st.slider(
        "Match Ratio",
        min_value=0.5,
        max_value=1.0,
        value=0.7,
        step=0.05,
        help_text="Lowe's ratio test threshold"
    )

    ransac_threshold = st.slider(
        "RANSAC Threshold",
        min_value=1.0,
        max_value=10.0,
        value=5.0,
        step=0.5,
        help_text="RANSAC reprojection threshold"
    )

section_header("Parameter Summary", "📊")

# Build configuration dictionaries
mask_config = {
    'method': mask_method,
    'threshold': threshold,
    'kernel_size': kernel_size,
    'dilate_iterations': dilate_iter,
    'erode_iterations': erode_iter,
}

alignment_config = {
    'feature_detector': feature_detector,
    'max_features': max_features,
    'match_ratio': match_ratio,
    'ransac_threshold': ransac_threshold,
    'transformation_type': 'affine',
}

# Display configuration summary
col1, col2 = st.columns(2)

with col1:
    st.write("**Mask Generation Config:**")
    df_mask = pd.DataFrame(list(mask_config.items()), columns=["Parameter", "Value"])
    st.dataframe(df_mask, use_container_width=True, hide_index=True)

with col2:
    st.write("**Alignment Config:**")
    df_align = pd.DataFrame(list(alignment_config.items()), columns=["Parameter", "Value"])
    st.dataframe(df_align, use_container_width=True, hide_index=True)

section_header("Actions", "🎬")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("💾 Save Configuration", use_container_width=True):
        st.session_state.mask_config = mask_config
        st.session_state.alignment_config = alignment_config
        st.success("✓ Configuration saved!")

with col2:
    if st.button("⏭️ Next: Process", use_container_width=True):
        st.session_state.mask_config = mask_config
        st.session_state.alignment_config = alignment_config
        set_workflow_step(3)
        st.switch_page("pages/04_Process.py")

with col3:
    if st.button("↩️ Back: Load Data", use_container_width=True):
        set_workflow_step(1)
        st.switch_page("pages/02_Load_Data.py")

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.8rem;'>Phase 1 - Backend Integration</div>", unsafe_allow_html=True)


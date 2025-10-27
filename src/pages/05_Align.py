"""
Align Page - Image Alignment

Handles image alignment between modalities using backend pipeline.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 5: Align
"""

import streamlit as st
from pathlib import Path
import sys
import logging
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step
from ui.components import section_header, parameter_slider, metrics_row
from pipelines.image_alignment_pipeline import ImageAlignmentPipeline

st.set_page_config(page_title="Align - LUAD Spatial Omics", page_icon="🔄", layout="wide")

st.title("🔄 Align Images")

section_header("Alignment Configuration", "⚙️")

col1, col2 = st.columns(2)

with col1:
    feature_detector = st.selectbox("Feature Detector", ["sift", "orb", "akaze"])
    max_features = st.slider("Max Features", 100, 1000, 500, step=100)

with col2:
    match_ratio = st.slider("Match Ratio", 0.5, 1.0, 0.7, step=0.05)
    ransac_threshold = st.slider("RANSAC Threshold", 1.0, 10.0, 5.0, step=0.5)

# Check if data is loaded
if 'loaded_data' not in st.session_state or st.session_state.loaded_data is None:
    st.error("❌ No data loaded. Please load data on the 'Load Data' page first.")
elif 'generated_mask' not in st.session_state or st.session_state.generated_mask is None:
    st.error("❌ No mask generated. Please run mask generation on the 'Process' page first.")
else:
    section_header("Alignment Visualization", "👁️")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Reference Image")
        ref_img = st.session_state.loaded_data.load_image()
        if ref_img is not None:
            st.image(ref_img, use_column_width=True, clamp=True)

    with col2:
        st.subheader("Moving Image")
        if 'moving_data' in st.session_state and st.session_state.moving_data is not None:
            mov_img = st.session_state.moving_data.load_image()
            if mov_img is not None:
                st.image(mov_img, use_column_width=True, clamp=True)
        else:
            st.info("No moving image loaded. Load a second dataset to align.")

    section_header("Alignment Results", "📊")

    if st.button("▶️ Start Alignment", use_container_width=True):
        try:
            # Check if we have two datasets
            if 'moving_data' not in st.session_state or st.session_state.moving_data is None:
                st.error("❌ Need two datasets for alignment. Load a second dataset first.")
            else:
                # Create alignment configuration
                config = {
                    'feature_detector': feature_detector,
                    'max_features': max_features,
                    'match_ratio': match_ratio,
                    'ransac_threshold': ransac_threshold,
                    'transformation_type': 'affine',
                }

                # Create pipeline
                pipeline = ImageAlignmentPipeline(
                    st.session_state.loaded_data,
                    st.session_state.moving_data,
                    st.session_state.generated_mask,
                    config=config
                )

                # Create progress tracking UI
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Define progress callback
                def update_progress(progress: float, message: str):
                    progress_bar.progress(min(progress / 100.0, 0.99))
                    status_text.text(f"📊 {message}")

                # Register callback
                pipeline.add_progress_callback(update_progress)

                # Execute alignment
                M, aligned_img = pipeline.align()

                # Store results in session state
                st.session_state.transformation_matrix = M
                st.session_state.aligned_image = aligned_img
                st.session_state.alignment_metrics = pipeline.quality_metrics
                st.session_state.alignment_log = pipeline.get_processing_log()

                # Final progress update
                progress_bar.progress(1.0)
                status_text.text("✓ Alignment complete!")

                # Display success message
                st.success("✓ Alignment complete!")

                # Display alignment metrics
                if pipeline.quality_metrics:
                    st.subheader("Alignment Quality Metrics")
                    col1, col2, col3, col4 = st.columns(4)

                    metrics = pipeline.quality_metrics
                    with col1:
                        if 'matched_features' in metrics:
                            st.metric("Matched Features", f"{metrics['matched_features']}")
                    with col2:
                        if 'inlier_ratio' in metrics:
                            st.metric("Inlier Ratio", f"{metrics['inlier_ratio']:.2%}")
                    with col3:
                        if 'cross_correlation' in metrics:
                            st.metric("Cross-Correlation", f"{metrics['cross_correlation']:.3f}")
                    with col4:
                        if 'mse' in metrics:
                            st.metric("MSE", f"{metrics['mse']:.4f}")

        except Exception as e:
            st.error(f"❌ Error during alignment: {str(e)}")
            logging.error(f"Alignment error: {e}", exc_info=True)

section_header("Transformation Matrix", "📐")

if 'transformation_matrix' in st.session_state and st.session_state.transformation_matrix is not None:
    M = st.session_state.transformation_matrix
    st.write("**Transformation Matrix:**")
    st.write(M)

    # Display transformation parameters
    if M.shape[0] == 2:
        # Affine transformation
        st.write("**Affine Transformation Parameters:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Translation X:** {M[0, 2]:.2f}")
        with col2:
            st.write(f"**Translation Y:** {M[1, 2]:.2f}")
        with col3:
            st.write(f"**Scale:** {np.sqrt(M[0, 0]**2 + M[0, 1]**2):.4f}")

    # Display aligned image
    if 'aligned_image' in st.session_state and st.session_state.aligned_image is not None:
        st.subheader("Aligned Image")
        st.image(st.session_state.aligned_image, use_column_width=True, clamp=True)
else:
    st.info("Transformation matrix will appear here after alignment")

section_header("Actions", "🎬")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⏭️ Next: Analyze", use_container_width=True):
        set_workflow_step(5)
        st.switch_page("pages/06_Analyze.py")

with col2:
    if st.button("↩️ Back: Process", use_container_width=True):
        set_workflow_step(3)
        st.switch_page("pages/04_Process.py")

with col3:
    if st.button("🔄 Realign", use_container_width=True):
        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.8rem;'>Phase 0 - GUI Foundation</div>", unsafe_allow_html=True)


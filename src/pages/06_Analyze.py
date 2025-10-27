"""
Analyze Page - Correlation and Clustering Analysis

Handles correlation analysis and clustering visualization with backend integration.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 6: Analyze
"""

import streamlit as st
from pathlib import Path
import sys
import numpy as np
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step
from ui.components import section_header, parameter_selectbox, metrics_row

st.set_page_config(page_title="Analyze - LUAD Spatial Omics", page_icon="📊", layout="wide")

st.title("📊 Analyze Results")

# Check if data is loaded and processed
if 'loaded_data' not in st.session_state or st.session_state.loaded_data is None:
    st.error("❌ No data loaded. Please load data on the 'Load Data' page first.")
    st.stop()

if 'generated_mask' not in st.session_state or st.session_state.generated_mask is None:
    st.error("❌ No mask generated. Please run mask generation on the 'Process' page first.")
    st.stop()

section_header("Analysis Configuration", "⚙️")

col1, col2 = st.columns(2)

with col1:
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Correlation", "Clustering", "Spatial Statistics"]
    )

with col2:
    if analysis_type == "Clustering":
        clustering_method = st.selectbox(
            "Clustering Method",
            ["K-means", "Hierarchical", "DBSCAN"]
        )
    else:
        clustering_method = None

section_header("Correlation Analysis", "🔗")

if st.button("📊 Calculate Correlation", use_container_width=True):
    try:
        with st.spinner("Calculating correlation..."):
            # Get reference and aligned images
            ref_img = st.session_state.loaded_data.load_image()

            if 'aligned_image' in st.session_state and st.session_state.aligned_image is not None:
                aligned_img = st.session_state.aligned_image
            else:
                aligned_img = ref_img

            # Normalize images
            ref_norm = (ref_img - np.min(ref_img)) / (np.max(ref_img) - np.min(ref_img) + 1e-8)
            aligned_norm = (aligned_img - np.min(aligned_img)) / (np.max(aligned_img) - np.min(aligned_img) + 1e-8)

            # Calculate correlation
            correlation = np.corrcoef(ref_norm.flatten(), aligned_norm.flatten())[0, 1]

            # Store results
            st.session_state.correlation_value = correlation

            st.success(f"✓ Correlation calculated: {correlation:.4f}")

            # Display correlation heatmap
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Correlation Coefficient", f"{correlation:.4f}")
            with col2:
                st.metric("Correlation Strength", "Strong" if correlation > 0.7 else "Moderate" if correlation > 0.4 else "Weak")

    except Exception as e:
        st.error(f"❌ Error calculating correlation: {str(e)}")
        logging.error(f"Correlation error: {e}", exc_info=True)

section_header("Spatial Statistics", "📈")

if st.button("📊 Calculate Spatial Statistics", use_container_width=True):
    try:
        with st.spinner("Calculating spatial statistics..."):
            mask = st.session_state.generated_mask

            # Calculate statistics
            mask_area = np.sum(mask > 0)
            total_area = mask.shape[0] * mask.shape[1]
            coverage = (mask_area / total_area) * 100

            # Store results
            st.session_state.spatial_stats = {
                'mask_area': mask_area,
                'total_area': total_area,
                'coverage': coverage,
            }

            st.success("✓ Spatial statistics calculated")

            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mask Area (pixels)", f"{mask_area:,}")
            with col2:
                st.metric("Total Area (pixels)", f"{total_area:,}")
            with col3:
                st.metric("Coverage (%)", f"{coverage:.2f}%")

    except Exception as e:
        st.error(f"❌ Error calculating spatial statistics: {str(e)}")
        logging.error(f"Spatial statistics error: {e}", exc_info=True)

section_header("Analysis Results", "📊")

# Display available results
if 'correlation_value' in st.session_state:
    st.write(f"**Correlation Coefficient**: {st.session_state.correlation_value:.4f}")

if 'spatial_stats' in st.session_state:
    stats = st.session_state.spatial_stats
    st.write(f"**Mask Coverage**: {stats['coverage']:.2f}%")
    st.write(f"**Mask Area**: {stats['mask_area']:,} pixels")

section_header("Actions", "🎬")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⏭️ Next: Results", use_container_width=True):
        set_workflow_step(6)
        st.switch_page("pages/07_Results.py")

with col2:
    if st.button("↩️ Back: Align", use_container_width=True):
        set_workflow_step(4)
        st.switch_page("pages/05_Align.py")

with col3:
    if st.button("🔄 Reanalyze", use_container_width=True):
        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.8rem;'>Phase 0 - GUI Foundation</div>", unsafe_allow_html=True)


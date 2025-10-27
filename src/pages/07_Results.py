"""
Results Page - View and Export Results

Displays results summary and export options with backend integration.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 7: Results
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import numpy as np
import io
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step, is_workflow_complete
from ui.components import section_header, metrics_row

st.set_page_config(page_title="Results - LUAD Spatial Omics", page_icon="📊", layout="wide")

st.title("📊 Results & Export")

# Check if workflow has data
if 'loaded_data' not in st.session_state or st.session_state.loaded_data is None:
    st.error("❌ No data loaded. Please complete the workflow first.")
    st.stop()

section_header("Results Summary", "📋")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'alignment_metrics' in st.session_state and 'cross_correlation' in st.session_state.alignment_metrics:
        st.metric("Alignment Score", f"{st.session_state.alignment_metrics['cross_correlation']:.3f}")
    else:
        st.metric("Alignment Score", "N/A")

with col2:
    if 'generated_mask' in st.session_state:
        mask = st.session_state.generated_mask
        coverage = (np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])) * 100
        st.metric("Mask Coverage", f"{coverage:.2f}%")
    else:
        st.metric("Mask Coverage", "N/A")

with col3:
    if 'correlation_value' in st.session_state:
        st.metric("Correlation", f"{st.session_state.correlation_value:.3f}")
    else:
        st.metric("Correlation", "N/A")

with col4:
    st.metric("Status", "✓ Complete")

section_header("Visualization Gallery", "🖼️")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Generated Mask")
    if 'generated_mask' in st.session_state and st.session_state.generated_mask is not None:
        st.image(st.session_state.generated_mask, use_column_width=True, clamp=True)
    else:
        st.info("No mask generated")

with col2:
    st.subheader("Aligned Image")
    if 'aligned_image' in st.session_state and st.session_state.aligned_image is not None:
        st.image(st.session_state.aligned_image, use_column_width=True, clamp=True)
    else:
        st.info("No alignment performed")

section_header("Export Options", "💾")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 Export Mask (PNG)", use_container_width=True):
        if 'generated_mask' in st.session_state and st.session_state.generated_mask is not None:
            # Convert mask to uint8
            mask_uint8 = (st.session_state.generated_mask * 255).astype(np.uint8)

            # Create download button
            from PIL import Image
            img = Image.fromarray(mask_uint8)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            st.download_button(
                label="Download Mask PNG",
                data=buf.getvalue(),
                file_name=f"mask_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
        else:
            st.warning("No mask to export")

with col2:
    if st.button("📥 Export Metrics (CSV)", use_container_width=True):
        # Compile all metrics
        metrics_data = {
            'Metric': [],
            'Value': []
        }

        if 'alignment_metrics' in st.session_state:
            for key, value in st.session_state.alignment_metrics.items():
                metrics_data['Metric'].append(key)
                metrics_data['Value'].append(str(value))

        if 'spatial_stats' in st.session_state:
            for key, value in st.session_state.spatial_stats.items():
                metrics_data['Metric'].append(key)
                metrics_data['Value'].append(str(value))

        if metrics_data['Metric']:
            df_metrics = pd.DataFrame(metrics_data)
            csv = df_metrics.to_csv(index=False)

            st.download_button(
                label="Download Metrics CSV",
                data=csv,
                file_name=f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No metrics to export")

with col3:
    if st.button("📥 Export Transformation", use_container_width=True):
        if 'transformation_matrix' in st.session_state and st.session_state.transformation_matrix is not None:
            M = st.session_state.transformation_matrix

            # Save as text
            text_data = "Transformation Matrix\n"
            text_data += str(M)

            st.download_button(
                label="Download Transformation",
                data=text_data,
                file_name=f"transformation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("No transformation to export")

section_header("Metadata", "ℹ️")

metadata = {
    "Modality": st.session_state.loaded_data.modality,
    "Resolution": f"{st.session_state.loaded_data.resolution:.4f} µm/px",
    "Channels": len(st.session_state.loaded_data.channel_names),
    "Processing Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "Pipeline Version": "1.0.0",
    "Status": "Complete",
}

df = pd.DataFrame(list(metadata.items()), columns=["Key", "Value"])
st.dataframe(df, use_container_width=True, hide_index=True)

section_header("Actions", "🎬")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        set_workflow_step(0)
        st.switch_page("pages/01_Home.py")

with col2:
    if st.button("↩️ Back: Analyze", use_container_width=True):
        set_workflow_step(5)
        st.switch_page("pages/06_Analyze.py")

with col3:
    if st.button("🔄 New Project", use_container_width=True):
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("✓ Session cleared. Starting new project...")
        st.switch_page("pages/01_Home.py")

st.markdown("---")

st.success("✓ Workflow complete! All steps finished successfully.")

st.markdown("<div style='text-align: center; color: gray; font-size: 0.8rem;'>Phase 1 - Backend Integration</div>", unsafe_allow_html=True)


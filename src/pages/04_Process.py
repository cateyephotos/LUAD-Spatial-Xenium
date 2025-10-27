"""
Process Page - Mask Generation

Handles mask generation with progress tracking using backend pipeline.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 4: Process
"""

import streamlit as st
from pathlib import Path
import sys
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step
from ui.components import section_header, progress_tracker, status_indicator
from pipelines.mask_generation_pipeline import MaskGenerationPipeline

st.set_page_config(page_title="Process - LUAD Spatial Omics", page_icon="⚙️", layout="wide")

st.title("⚙️ Generate Tissue Masks")

section_header("Processing Status", "📊")

progress_tracker(
    ["Load Data", "Configure", "Process", "Align", "Analyze", "Results"],
    2
)

section_header("Mask Generation", "🎯")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### Processing Steps
    
    1. Load image data
    2. Apply binarization
    3. Morphological operations
    4. Contour detection
    5. Mask refinement
    """)

with col2:
    if 'loaded_data' in st.session_state and st.session_state.loaded_data is not None:
        st.success("✓ Data loaded and ready")
    else:
        st.warning("⚠️ No data loaded. Please go to Load Data page first.")

# Check if data is loaded
if 'loaded_data' not in st.session_state or st.session_state.loaded_data is None:
    st.error("❌ No data loaded. Please load data on the 'Load Data' page first.")
else:
    if st.button("▶️ Start Processing", use_container_width=True):
        try:
            # Get configuration from session state
            config = st.session_state.get('mask_config', {})

            # Create pipeline
            pipeline = MaskGenerationPipeline(st.session_state.loaded_data, config)

            # Create progress tracking UI
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Define progress callback
            def update_progress(progress: float, message: str):
                progress_bar.progress(min(progress / 100.0, 0.99))
                status_text.text(f"📊 {message}")

            # Register callback
            pipeline.add_progress_callback(update_progress)

            # Generate mask
            mask = pipeline.generate_mask()

            # Store results in session state
            st.session_state.generated_mask = mask
            st.session_state.processing_log = pipeline.get_processing_log()

            # Final progress update
            progress_bar.progress(1.0)
            status_text.text("✓ Mask generation complete!")

            # Display success message
            st.success("✓ Mask generation complete!")

            # Display mask statistics
            stats = pipeline.get_mask_statistics()
            if stats:
                st.subheader("Mask Statistics")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Shape", f"{stats['shape']}")
                with col2:
                    st.metric("Total Pixels", f"{stats['total_pixels']:,}")
                with col3:
                    st.metric("Masked Pixels", f"{stats['masked_pixels']:,}")
                with col4:
                    st.metric("Coverage", f"{stats['mask_percentage']:.1f}%")

        except Exception as e:
            st.error(f"❌ Error during mask generation: {str(e)}")
            logging.error(f"Mask generation error: {e}", exc_info=True)

section_header("Processing Logs", "📋")

with st.expander("View Logs", expanded=False):
    if 'processing_log' in st.session_state and st.session_state.processing_log:
        for log_entry in st.session_state.processing_log:
            st.text(log_entry)
    else:
        st.info("No processing logs yet. Run mask generation to see logs.")

section_header("Mask Preview", "👁️")

if 'generated_mask' in st.session_state and st.session_state.generated_mask is not None:
    try:
        import numpy as np
        import matplotlib.pyplot as plt

        mask = st.session_state.generated_mask

        # Create visualization
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        # Original mask
        axes[0].imshow(mask, cmap='gray')
        axes[0].set_title('Generated Mask')
        axes[0].axis('off')

        # Mask with contours
        from scipy import ndimage
        labeled, num_features = ndimage.label(mask)
        axes[1].imshow(labeled, cmap='nipy_spectral')
        axes[1].set_title(f'Labeled Regions ({num_features} regions)')
        axes[1].axis('off')

        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Could not display mask preview: {str(e)}")
else:
    st.info("Mask preview will appear here after processing")

section_header("Actions", "🎬")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⏭️ Next: Align", use_container_width=True):
        set_workflow_step(4)
        st.switch_page("pages/05_Align.py")

with col2:
    if st.button("↩️ Back: Configure", use_container_width=True):
        set_workflow_step(2)
        st.switch_page("pages/03_Configure.py")

with col3:
    if st.button("🔄 Reprocess", use_container_width=True):
        st.rerun()

st.markdown("---")
st.markdown("<div style='text-align: center; color: gray; font-size: 0.8rem;'>Phase 0 - GUI Foundation</div>", unsafe_allow_html=True)


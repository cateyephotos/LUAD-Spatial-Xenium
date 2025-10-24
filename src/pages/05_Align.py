"""
Align Page - Image Alignment

Handles image alignment between modalities.

Reference: Planning/STREAMLIT_GUI_IMPLEMENTATION.md - Page 5: Align
"""

import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from streamlit_utils import set_workflow_step
from ui.components import section_header, parameter_slider, metrics_row

st.set_page_config(page_title="Align - LUAD Spatial Omics", page_icon="🔄", layout="wide")

st.title("🔄 Align Images")

section_header("Alignment Configuration", "⚙️")

col1, col2 = st.columns(2)

with col1:
    zoom_range = parameter_slider("Zoom Range (%)", 1, 50, 10)
    shift_range = parameter_slider("Shift Range (pixels)", 1, 100, 50)

with col2:
    rotation_range = parameter_slider("Rotation Range (degrees)", 1, 90, 15)
    fitness_metric = st.selectbox("Fitness Metric", ["IoU", "MI", "CC"])

section_header("Alignment Visualization", "👁️")

st.info("Alignment visualization will be displayed here in Phase 1")

section_header("Alignment Results", "📊")

if st.button("▶️ Start Alignment", use_container_width=True):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(101):
        status_text.text(f"Alignment progress: {i}%")
        progress_bar.progress(i / 100)
        import time
        time.sleep(0.01)
    
    st.success("✓ Alignment complete!")
    
    metrics_row({
        "Alignment Score": "0.95",
        "Processing Time": "2.3s",
        "Transformation": "Affine",
        "Fitness Metric": fitness_metric,
    })

section_header("Transformation Matrix", "📐")

st.info("Transformation matrix will be displayed here")

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


# Streamlit GUI Overview

**Date**: 2025-10-23
**Status**: PLANNING
**Integration Point**: Phase 0 (Parallel to Phase 1)

---

## Executive Summary

A comprehensive Streamlit web interface will replace the CLI-based DOIT_*.py scripts, providing:

✅ Interactive workflow management
✅ Real-time parameter tuning
✅ Visual feedback and progress tracking
✅ File upload/download capabilities
✅ Results visualization and export
✅ Multi-step guided workflow

---

## Why Streamlit?

### Advantages
- **Python-native**: No JavaScript/frontend knowledge needed
- **Rapid development**: Build interactive apps in minutes
- **Built-in widgets**: File upload, sliders, forms, charts
- **Caching**: Automatic performance optimization
- **Deployment**: Easy cloud deployment (Streamlit Cloud, Docker)
- **Community**: Large ecosystem and support

### Comparison
| Feature | Streamlit | Flask | Django | FastAPI |
|---------|-----------|-------|--------|---------|
| Setup time | 5 min | 30 min | 2 hours | 30 min |
| Learning curve | Easy | Medium | Hard | Medium |
| Data viz | Built-in | Manual | Manual | Manual |
| Caching | Automatic | Manual | Manual | Manual |
| Deployment | 1-click | Complex | Complex | Complex |

---

## Architecture

### Client-Server Model
```
Browser (WebSocket)
    ↓
Streamlit Server (Python)
    ↓
Pipeline (Core Processing)
    ↓
Data Files (TIFF, PNG, etc.)
```

### Execution Flow
1. User interacts with widget
2. Streamlit reruns entire script
3. Session state persists between reruns
4. Caching prevents recomputation
5. UI updates with new results

---

## Workflow Pages

### 1. Home (01_Home.py)
- Welcome screen
- Project overview
- Quick start guide
- Recent projects

### 2. Load Data (02_Load_Data.py)
- Upload Visium/Xenium/PhenoCycler files
- File validation
- Data preview
- Metadata extraction

### 3. Configure (03_Configure.py)
- Parameter editor
- Preset configurations
- Advanced options
- Validation feedback

### 4. Process (04_Process.py)
- Mask generation
- Progress tracking
- Real-time logs
- Mask preview

### 5. Align (05_Align.py)
- Alignment visualization
- Parameter tuning
- Fitness metrics
- Results display

### 6. Analyze (06_Analyze.py)
- Correlation analysis
- Clustering visualization
- Gene expression plots
- ROI extraction

### 7. Results (07_Results.py)
- Results summary
- Visualization gallery
- Export options
- Report generation

---

## Key Features

### 1. File Upload
```python
uploaded_file = st.file_uploader(
    "Upload TIFF file",
    type=["tif", "tiff", "png"],
    accept_multiple_files=False
)
```
- Drag-and-drop support
- File validation
- Progress indication
- Size limits: 500 MB

### 2. Parameter Configuration
```python
threshold = st.slider(
    "Binary Threshold",
    min_value=0,
    max_value=255,
    value=160,
    step=1
)
```
- Real-time validation
- Preset configurations
- Parameter descriptions
- Range constraints

### 3. Progress Tracking
```python
progress_bar = st.progress(0)
status_text = st.empty()

for i in range(100):
    status_text.text(f"Processing: {i}%")
    progress_bar.progress((i + 1) / 100)
```
- Real-time updates
- Estimated time remaining
- Cancellation support
- Error handling

### 4. Visualization
```python
st.image(mask_array, caption="Generated Mask")
st.plotly_chart(alignment_plot)
st.dataframe(results_df)
```
- Image display
- Interactive charts
- Data tables
- Side-by-side comparison

### 5. Download Results
```python
st.download_button(
    label="Download Results",
    data=csv_data,
    file_name="results.csv",
    mime="text/csv"
)
```
- Multiple formats (CSV, PNG, HDF5)
- Batch download
- Metadata inclusion

---

## State Management

### Session State
```python
# Persists between reruns within a session
st.session_state.workflow_step = 2
st.session_state.loaded_data = image_array
```

### Query Parameters
```python
# Persists in URL (shareable)
st.query_params["sample_id"] = "FFPE_LUAD_3_B"
st.query_params["step"] = "alignment"
```

### Workflow State
```
Home (0) → Load Data (1) → Configure (2) → 
Process (3) → Align (4) → Analyze (5) → Results (6)
```

---

## Performance Optimization

### Caching
```python
@st.cache_data
def load_image(filepath):
    return cv2.imread(filepath)

@st.cache_resource
def init_aligner():
    return Aligner()
```

### Forms (Batch Updates)
```python
with st.form("config_form"):
    param1 = st.slider("Param 1", 0, 100)
    param2 = st.slider("Param 2", 0, 100)
    if st.form_submit_button("Apply"):
        process(param1, param2)
```

### Lazy Loading
- Load pages only when accessed
- Stream large files
- Use temporary directories

---

## Security

### Input Validation
```python
def validate_file(uploaded_file):
    if uploaded_file.size > 500 * 1024 * 1024:
        raise ValueError("File too large")
    if uploaded_file.type not in ALLOWED_TYPES:
        raise ValueError("Invalid type")
```

### Secrets Management
```toml
# .streamlit/secrets.toml
database_url = "postgresql://..."
api_key = "sk-..."
```

### CSRF Protection
- Enabled by default
- XsrfProtection in config

---

## Deployment Options

### Local Development
```bash
streamlit run src/app.py
# http://localhost:8501
```

### Streamlit Cloud
- Free hosting for public repos
- Auto-deploy from GitHub
- Secrets management
- Resource limits: 1 GB RAM

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "src/app.py"]
```

### Self-hosted
- AWS EC2, Azure VM, GCP Compute
- Kubernetes deployment
- Custom domain + SSL

---

## Integration with Pipeline

### Phase 0 (Weeks 1-2)
- Create Streamlit app structure
- Implement pages and UI
- Session state management
- No backend integration yet

### Phase 1 (Weeks 3-4)
- Create abstraction layer
- Implement core processors
- Connect to Streamlit UI

### Phase 2 (Weeks 5-6)
- Integrate alignment engine
- Connect analysis modules
- Full workflow testing

### Phase 3 (Weeks 7-8)
- Xenium support
- Performance optimization
- Production deployment

---

## Testing Strategy

### Unit Tests
```python
def test_file_validation():
    assert validate_file(valid_file) == True
    with pytest.raises(ValueError):
        validate_file(invalid_file)
```

### Integration Tests
```python
from streamlit.testing.v1 import AppTest

def test_workflow():
    at = AppTest.from_file("src/app.py")
    at.run()
    assert at.title[0].value == "Spatial Omics"
```

### Manual Testing
- File upload/download
- Parameter configuration
- Workflow navigation
- Error handling

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Page load | < 2s | TBD |
| File upload | < 5s (100 MB) | TBD |
| Widget response | < 500ms | TBD |
| Test coverage | 80%+ | TBD |
| User satisfaction | 4.5/5 | TBD |

---

## Timeline

| Week | Tasks | Deliverable |
|------|-------|-------------|
| 1 | App structure, pages | Basic UI |
| 2 | Components, state mgmt | Functional pages |
| 3-4 | Backend integration | Full workflow |
| 5-6 | Testing, optimization | Production ready |

---

## Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **API Reference**: https://docs.streamlit.io/develop/api-reference
- **Community**: https://discuss.streamlit.io
- **GitHub**: https://github.com/streamlit/streamlit

---

## Next Steps

1. ✅ Review this document
2. ⏭️ Review STREAMLIT_TECHNICAL_GUIDELINES.md
3. ⏭️ Review STREAMLIT_GUI_IMPLEMENTATION.md
4. ⏭️ Approve Phase 0 plan
5. ⏭️ Begin implementation

---

**Last Updated**: 2025-10-23
**Status**: PLANNING COMPLETE
**Ready for**: Phase 0 Implementation


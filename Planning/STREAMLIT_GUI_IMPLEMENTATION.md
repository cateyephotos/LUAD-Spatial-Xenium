# Streamlit GUI Implementation Plan

**Date**: 2025-10-23
**Status**: PLANNING
**Integration**: Phase 1 (Foundation)

---

## 1. Overview

### Goals
- Create interactive web interface for spatial omics alignment
- Replace CLI-based DOIT_*.py scripts
- Enable real-time parameter tuning
- Provide visual feedback and progress tracking
- Support multi-step workflows

### Technology Stack
- **Framework**: Streamlit 1.50.0+
- **Architecture**: Multipage app (pages/ directory)
- **State Management**: Session State + Query Parameters
- **Visualization**: Plotly, Matplotlib, OpenCV
- **Data Processing**: NumPy, Pandas, OpenCV, tifffile

---

## 2. App Structure

### Directory Layout
```
src/
├── app.py (main entry point)
├── pages/
│   ├── 01_Home.py
│   ├── 02_Load_Data.py
│   ├── 03_Configure.py
│   ├── 04_Process.py
│   ├── 05_Align.py
│   ├── 06_Analyze.py
│   └── 07_Results.py
├── ui/
│   ├── components.py (reusable UI components)
│   ├── layouts.py (page layouts)
│   └── styles.py (CSS/theming)
├── streamlit_utils/
│   ├── state_manager.py (session state helpers)
│   ├── cache_manager.py (caching utilities)
│   └── file_handler.py (file upload/download)
└── config/
    └── streamlit_config.toml
```

---

## 3. Page Specifications

### Page 1: Home (01_Home.py)
**Purpose**: Welcome, overview, quick start

**Components**:
- Title and description
- Project status indicator
- Quick links to main workflows
- Recent projects (from session state)
- Documentation links

**State**:
- `workflow_step`: Current step (0-6)
- `project_name`: Current project

### Page 2: Load Data (02_Load_Data.py)
**Purpose**: Upload and configure data sources

**Components**:
- Data source selector (Visium, Xenium, PhenoCycler, Generic OME-TIFF)
- File uploader (multi-file support)
- File preview (thumbnail, metadata)
- Data validation feedback
- Sample configuration form

**State**:
- `uploaded_files`: Dict of uploaded files
- `data_sources`: List of loaded data sources
- `current_sample`: Selected sample

**Constraints**:
- Max file size: 500 MB (configurable)
- Supported formats: .tif, .tiff, .png, .jpg, .qptiff
- Validation: File type, size, metadata

### Page 3: Configure (03_Configure.py)
**Purpose**: Set processing parameters

**Components**:
- Parameter editor (from config/parameters.yaml)
- Preset configurations (Visium, Xenium, PhenoCycler)
- Advanced options (collapsible)
- Parameter validation
- Save/load configurations

**State**:
- `parameters`: Current parameter set
- `preset_name`: Selected preset

**Constraints**:
- Validate parameter ranges
- Show parameter descriptions
- Warn on unusual values

### Page 4: Process (04_Process.py)
**Purpose**: Generate masks for each modality

**Components**:
- Processing status (per modality)
- Progress bars
- Real-time logs
- Preview of generated masks
- Processing time estimates

**State**:
- `processing_status`: Dict of status per modality
- `generated_masks`: Dict of mask arrays
- `processing_logs`: List of log messages

**Constraints**:
- Timeout: 5 minutes per modality
- Memory limit: 2 GB per operation
- Parallel processing: Up to 2 modalities

### Page 5: Align (05_Align.py)
**Purpose**: Align masks between modalities

**Components**:
- Alignment visualization (side-by-side)
- Alignment parameters (zoom, shift, rotate ranges)
- Fitness metric selector
- Alignment progress
- Alignment results (IoU, transformation matrix)

**State**:
- `alignment_params`: Current alignment parameters
- `alignment_result`: Transformation matrix + fitness
- `aligned_masks`: Aligned mask arrays

**Constraints**:
- Timeout: 10 minutes
- Search space: Configurable
- Fitness metrics: IoU, MI, CC

### Page 6: Analyze (06_Analyze.py)
**Purpose**: Correlation and clustering analysis

**Components**:
- Correlation heatmap
- Clustering visualization
- Gene expression plots
- ROI extraction
- Analysis parameters

**State**:
- `correlation_matrix`: Computed correlations
- `clustering_result`: Cluster assignments
- `roi_data`: Extracted ROI data

**Constraints**:
- Optional R integration (Seurat)
- Python-only fallback available

### Page 7: Results (07_Results.py)
**Purpose**: View and export results

**Components**:
- Results summary
- Visualization gallery
- Download options (CSV, PNG, HDF5)
- Report generation
- Metadata export

**State**:
- `results_summary`: Summary statistics
- `export_format`: Selected export format

---

## 4. UI Components

### Reusable Components (ui/components.py)

```python
def file_upload_widget(label, file_types):
    """File upload with validation"""
    
def parameter_slider(name, min_val, max_val, default):
    """Configurable slider with validation"""
    
def progress_tracker(steps, current_step):
    """Multi-step progress indicator"""
    
def image_viewer(image, title, width=400):
    """Image display with zoom/pan"""
    
def results_table(data, columns):
    """Formatted results table"""
    
def download_button(data, filename, format):
    """Download with format options"""
```

---

## 5. Session State Management

### State Structure
```python
st.session_state = {
    # Workflow
    "workflow_step": 0,
    "project_name": "",
    
    # Data
    "uploaded_files": {},
    "data_sources": [],
    "current_sample": None,
    
    # Processing
    "parameters": {},
    "processing_status": {},
    "generated_masks": {},
    
    # Alignment
    "alignment_params": {},
    "alignment_result": None,
    "aligned_masks": {},
    
    # Analysis
    "correlation_matrix": None,
    "clustering_result": None,
    "roi_data": None,
    
    # Results
    "results_summary": {},
}
```

### State Initialization
```python
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "workflow_step": 0,
        "project_name": "",
        # ... more defaults
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
```

---

## 6. Caching Strategy

### Data Caching
```python
@st.cache_data
def load_image(filepath):
    """Cache loaded images"""
    return cv2.imread(filepath)

@st.cache_data
def generate_mask(image, params):
    """Cache mask generation"""
    return mask_generator.generate(image, params)
```

### Resource Caching
```python
@st.cache_resource
def init_aligner():
    """Cache aligner instance"""
    return Aligner()

@st.cache_resource
def init_config_loader():
    """Cache config loader"""
    return ConfigLoader()
```

---

## 7. Error Handling

### User Feedback
```python
try:
    result = process_data(data)
except ValueError as e:
    st.error(f"Invalid input: {str(e)}")
except TimeoutError:
    st.error("Processing timeout (>5 min)")
except MemoryError:
    st.error("Insufficient memory")
except Exception as e:
    st.error(f"Unexpected error: {str(e)}")
    st.stop()
```

### Validation
```python
def validate_file(uploaded_file):
    """Validate uploaded file"""
    if uploaded_file.size > 500 * 1024 * 1024:
        raise ValueError("File too large (>500 MB)")
    if uploaded_file.type not in ALLOWED_TYPES:
        raise ValueError("Invalid file type")
    return True
```

---

## 8. Performance Optimization

### Lazy Loading
- Load pages only when accessed
- Cache expensive computations
- Use session state for intermediate results

### Memory Management
- Clear cache between projects
- Stream large files
- Use temporary directories

### UI Responsiveness
- Use forms to batch updates
- Show progress indicators
- Implement cancellation

---

## 9. Configuration

### .streamlit/config.toml
```toml
[client]
showErrorDetails = true
toolbarMode = "developer"

[logger]
level = "info"

[server]
maxUploadSize = 500
enableXsrfProtection = true
port = 8501

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

---

## 10. Deployment

### Local Development
```bash
streamlit run src/app.py
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "src/app.py"]
```

### Streamlit Cloud
- Push to GitHub
- Connect via Streamlit Cloud
- Auto-deploy on push

---

## 11. Testing

### Unit Tests
```python
def test_file_validation():
    assert validate_file(valid_file) == True
    with pytest.raises(ValueError):
        validate_file(invalid_file)
```

### Integration Tests
```python
def test_workflow():
    at = AppTest.from_file("src/app.py")
    at.run()
    # Test page navigation
    # Test data upload
    # Test processing
```

---

## 12. Implementation Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| 1 | 1 week | App structure, pages, state management |
| 2 | 1 week | UI components, file handling |
| 3 | 1 week | Integration with pipeline |
| 4 | 1 week | Testing, optimization, deployment |

**Total**: 4 weeks

---

## 13. Success Criteria

✅ All 7 pages functional
✅ File upload/download working
✅ Real-time progress tracking
✅ Parameter configuration UI
✅ Results visualization
✅ < 2s page load time
✅ < 500ms widget response
✅ 80%+ test coverage

---

## 14. Future Enhancements

- User authentication
- Project persistence (database)
- Batch processing
- Advanced visualization (3D)
- API endpoint for programmatic access
- Mobile-responsive design

---

**Last Updated**: 2025-10-23
**Next Phase**: Implementation (Phase 1)


# Streamlit Technical Guidelines & Best Practices

**Date**: 2025-10-23
**Version**: 1.0
**Streamlit Version**: 1.50.0+
**Python Version**: 3.9+

---

## 1. Architecture Overview

### Client-Server Model
- **Frontend**: Browser-based UI (WebSocket connection)
- **Backend**: Python script execution
- **Communication**: Bidirectional WebSocket (automatic)
- **Execution Model**: Full script rerun on each user interaction

### Key Concepts
- **Reruns**: Script executes top-to-bottom on every widget interaction
- **Session State**: Persists data between reruns within a session
- **Caching**: Avoids recomputation of expensive operations
- **Widgets**: Built-in statefulness between reruns

---

## 2. Performance Optimization

### Caching Strategy

#### @st.cache_data
```python
@st.cache_data
def load_large_image(filepath):
    """Cache expensive data operations"""
    return cv2.imread(filepath)
```
- Use for: Data transformations, database queries, ML inference
- Invalidates when: Function arguments change
- Scope: Global (shared across sessions)

#### @st.cache_resource
```python
@st.cache_resource
def init_model():
    """Cache global resources"""
    return load_ml_model()
```
- Use for: Database connections, ML models, expensive initializations
- Invalidates when: Never (unless app restarts)
- Scope: Global (shared across sessions)

### Session State
```python
if "counter" not in st.session_state:
    st.session_state.counter = 0

if st.button("Increment"):
    st.session_state.counter += 1
```
- Use for: User-specific data, form state, workflow progress
- Scope: Per-session (isolated between users)
- Persists: Between reruns within same session

### Forms (Prevent Unnecessary Reruns)
```python
with st.form("my_form"):
    name = st.text_input("Name")
    submitted = st.form_submit_button("Submit")
    if submitted:
        process_data(name)
```
- Prevents rerun on every keystroke
- Only reruns on form submission
- Reduces API calls and computations

---

## 3. File Upload & Image Processing

### File Upload Best Practices
```python
uploaded_file = st.file_uploader(
    "Upload image",
    type=["tif", "tiff", "png", "jpg"],
    accept_multiple_files=False
)

if uploaded_file is not None:
    # Read file into memory
    file_bytes = uploaded_file.read()
    
    # Process with cv2
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
```

### Constraints
- **Default limit**: 200 MB per file
- **Cloud limit**: 200 MB (configurable)
- **Temporary storage**: Deleted after session ends
- **Multiple files**: Use `accept_multiple_files=True`

### Large File Handling
```python
# For large TIFF files (>500 MB)
@st.cache_data
def load_large_tiff(filepath):
    """Load and cache large TIFF"""
    with tifffile.TiffFile(filepath) as tif:
        return tif.asarray()

# Show progress
progress_bar = st.progress(0)
for i in range(100):
    # Process chunk
    progress_bar.progress((i + 1) / 100)
```

---

## 4. Multipage App Structure

### Directory Layout
```
app/
├── app.py (main entry point)
├── pages/
│   ├── 01_Load_Data.py
│   ├── 02_Process.py
│   ├── 03_Align.py
│   └── 04_Analyze.py
├── src/
│   ├── pipeline/
│   ├── processors/
│   └── utils/
└── config/
    └── parameters.yaml
```

### Navigation
```python
# In app.py
st.set_page_config(page_title="Spatial Omics", layout="wide")

# Pages auto-discovered from pages/ directory
# Navigation handled automatically
```

---

## 5. State Management

### Session State Pattern
```python
# Initialize state
if "workflow_step" not in st.session_state:
    st.session_state.workflow_step = 0
if "loaded_data" not in st.session_state:
    st.session_state.loaded_data = None

# Use state
if st.button("Next"):
    st.session_state.workflow_step += 1
    st.rerun()
```

### Query Parameters (URL State)
```python
# Persist state in URL
st.query_params["sample_id"] = "FFPE_LUAD_3_B"
st.query_params["step"] = "alignment"

# Read from URL
sample_id = st.query_params.get("sample_id", "")
```

---

## 6. Widget Best Practices

### Avoid Unnecessary Reruns
```python
# ❌ BAD: Reruns on every keystroke
name = st.text_input("Name")
if name:
    process(name)

# ✅ GOOD: Use form
with st.form("input_form"):
    name = st.text_input("Name")
    if st.form_submit_button("Process"):
        process(name)
```

### Columns for Layout
```python
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Alignment Score", 0.95)
with col2:
    st.metric("Processing Time", "2.3s")
with col3:
    st.metric("Memory Used", "512 MB")
```

### Tabs for Organization
```python
tab1, tab2, tab3 = st.tabs(["Visium", "Xenium", "PhenoCycler"])
with tab1:
    st.write("Visium processing")
with tab2:
    st.write("Xenium processing")
with tab3:
    st.write("PhenoCycler processing")
```

---

## 7. Error Handling & Logging

### User Feedback
```python
try:
    result = process_image(image)
except Exception as e:
    st.error(f"Processing failed: {str(e)}")
    st.stop()

st.success("Processing completed!")
st.info("Alignment score: 0.95")
st.warning("Large file detected, processing may take time")
```

### Progress Tracking
```python
progress_bar = st.progress(0)
status_text = st.empty()

for i in range(100):
    status_text.text(f"Processing: {i}%")
    progress_bar.progress((i + 1) / 100)
    time.sleep(0.1)
```

---

## 8. Data Visualization

### Image Display
```python
# Display single image
st.image(image_array, caption="Processed Image", use_column_width=True)

# Display multiple images
cols = st.columns(3)
for i, img in enumerate(images):
    with cols[i % 3]:
        st.image(img, caption=f"Image {i}")
```

### Interactive Charts
```python
import plotly.express as px

fig = px.scatter(df, x="x", y="y", color="category")
st.plotly_chart(fig, use_container_width=True)
```

### DataFrames
```python
st.dataframe(df, use_container_width=True)

# Editable dataframe
edited_df = st.data_editor(df, num_rows="dynamic")
```

---

## 9. Deployment Considerations

### Local Development
```bash
streamlit run app.py
# Runs on http://localhost:8501
```

### Streamlit Community Cloud
- Free hosting for public repos
- Automatic deployment from GitHub
- Secrets management via `.streamlit/secrets.toml`
- Resource limits: 1 GB RAM, 1 CPU

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

### Configuration
```toml
# .streamlit/config.toml
[client]
showErrorDetails = true

[logger]
level = "info"

[server]
maxUploadSize = 500
enableXsrfProtection = true
```

---

## 10. Security Best Practices

### Secrets Management
```python
# .streamlit/secrets.toml
database_url = "postgresql://..."
api_key = "sk-..."

# Access in code
db_url = st.secrets["database_url"]
```

### Input Validation
```python
import re

def validate_sample_id(sample_id):
    if not re.match(r"^[A-Z0-9_]+$", sample_id):
        raise ValueError("Invalid sample ID format")
    return sample_id
```

### File Upload Security
```python
# Validate file type
if uploaded_file.type not in ["image/tiff", "image/png"]:
    st.error("Invalid file type")
    st.stop()

# Validate file size
if uploaded_file.size > 500 * 1024 * 1024:  # 500 MB
    st.error("File too large")
    st.stop()
```

---

## 11. Testing

### Unit Tests
```python
# tests/test_processors.py
def test_mask_generation():
    img = np.random.rand(512, 512)
    mask = generate_mask(img)
    assert mask.shape == img.shape
    assert mask.dtype == np.uint8
```

### Streamlit App Testing
```python
from streamlit.testing.v1 import AppTest

def test_app():
    at = AppTest.from_file("app.py")
    at.run()
    assert at.title[0].value == "Spatial Omics Alignment"
```

---

## 12. Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Page load | < 2s | Initial load |
| Image upload | < 5s | 100 MB file |
| Mask generation | < 10s | 512x512 image |
| Alignment | < 30s | Full pipeline |
| UI responsiveness | < 500ms | Widget interaction |

---

## 13. Common Pitfalls

❌ **Don't**:
- Store large objects outside session state (memory leak)
- Call expensive functions without caching
- Use global variables for user data
- Ignore widget key conflicts
- Forget to handle file upload edge cases

✅ **Do**:
- Use @st.cache_data for expensive operations
- Use st.session_state for user-specific data
- Validate all user inputs
- Use forms to batch widget updates
- Implement proper error handling

---

## 14. Resources

- **Official Docs**: https://docs.streamlit.io
- **API Reference**: https://docs.streamlit.io/develop/api-reference
- **Community**: https://discuss.streamlit.io
- **GitHub**: https://github.com/streamlit/streamlit

---

## 15. Version Compatibility

- **Streamlit**: 1.50.0+ (latest)
- **Python**: 3.9, 3.10, 3.11, 3.12
- **NumPy**: 1.20+
- **OpenCV**: 4.5+
- **Pandas**: 1.3+
- **Plotly**: 5.0+

---

**Last Updated**: 2025-10-23
**Next Review**: 2025-12-23


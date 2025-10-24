# Refactoring Roadmap for Xenium Integration

## Phase 0: Streamlit GUI Foundation (Weeks 1-2)

### 0.1 Create Streamlit App Structure
- [ ] Create `src/app.py` (main entry point)
- [ ] Create `src/pages/` directory structure
- [ ] Create `src/ui/` components module
- [ ] Create `src/streamlit_utils/` utilities
- [ ] Create `.streamlit/config.toml`
- **Status**: NOT STARTED
- **Notes**: Parallel to Phase 1

### 0.2 Implement Core Pages
- [ ] Create `pages/01_Home.py`
- [ ] Create `pages/02_Load_Data.py`
- [ ] Create `pages/03_Configure.py`
- [ ] Create `pages/04_Process.py`
- [ ] Create `pages/05_Align.py`
- [ ] Create `pages/06_Analyze.py`
- [ ] Create `pages/07_Results.py`
- **Status**: NOT STARTED
- **Notes**: Basic structure, no backend integration yet

### 0.3 Session State Management
- [ ] Implement state initialization
- [ ] Create state manager utilities
- [ ] Implement state persistence
- [ ] Add state validation
- **Status**: NOT STARTED
- **Notes**: Critical for workflow continuity

### 0.4 UI Components Library
- [ ] Create file upload widget
- [ ] Create parameter editor widget
- [ ] Create progress tracker
- [ ] Create image viewer
- [ ] Create results table
- [ ] Create download button
- **Status**: NOT STARTED
- **Notes**: Reusable across all pages

---

## Phase 1: Foundation (Weeks 3-4)

### 1.1 Create Abstraction Layer
**Goal**: Define generic interfaces for spatial data

**New Files**:
- `src/core/spatial_data.py` - Abstract base class
- `src/core/visium_data.py` - Visium implementation
- `src/core/xenium_data.py` - Xenium implementation
- `src/core/ometiff_data.py` - Generic OME-TIFF support

**Key Methods**:
```python
class SpatialData:
    - load_image() -> np.ndarray
    - get_metadata() -> dict
    - get_resolution() -> float
    - generate_mask() -> np.ndarray
```

### 1.2 Extract Configuration System
**Goal**: Replace hardcoded parameters

**New Files**:
- `src/config/parameters.yaml` - Default parameters
- `src/config/config_loader.py` - YAML parser

**Parameters to Extract**:
- Binary thresholds
- Morphology kernel sizes
- Contour area thresholds
- Circle detection parameters
- Alignment search ranges

---

## Phase 2: Modularization (Weeks 3-4)

### 2.1 Generic Image Processing
**Refactor**: `Parse_Visium_HE.py` → `src/processors/image_processor.py`

**Changes**:
- Remove sample-specific circle detection
- Create `CircleDetector` class with configurable parameters
- Create `MaskGenerator` class
- Support arbitrary image formats

### 2.2 Generic TIFF Processing
**Refactor**: `Parse_PhenoCycler_QP.py` → `src/processors/tiff_processor.py`

**Changes**:
- Create `OMETiffReader` class
- Support arbitrary channel selection
- Generic metadata extraction
- Configurable page selection

### 2.3 Generic Alignment Engine
**Refactor**: `Align_Visium-PhenoCycler.py` → `src/alignment/aligner.py`

**Changes**:
- Remove data-specific assumptions
- Create `Aligner` class with configurable search space
- Support multiple optimization strategies
- Generic fitness functions

---

## Phase 3: Pipeline Refactoring (Weeks 5-6)

### 3.1 Remove DOIT_* Scripts
**Action**: Replace with unified pipeline

**New Files**:
- `src/pipeline/pipeline.py` - Main orchestrator
- `src/pipeline/workflow.yaml` - Workflow definition

**Benefits**:
- Single entry point
- Configurable workflow
- Batch processing support

### 3.2 Remove Sample-Specific Logic
**Files to Clean**:
- `DOIT_GetDATA_LUAD3B.py` → Generic data loader
- All `if sid == "FFPE_LUAD_*"` conditions
- Hardcoded directory names

### 3.3 Decouple R Dependencies
**Goal**: Make R optional

**Options**:
1. Keep R for Seurat (recommended for now)
2. Implement Python alternatives (scikit-learn)
3. Create wrapper for both

---

## Phase 4: Xenium Support (Weeks 7-8)

### 4.1 Implement Xenium Data Class
**File**: `src/core/xenium_data.py`

**Features**:
- Parse Xenium OME-TIFF metadata
- Extract multi-channel images
- Generate fluorescence-based masks
- Support subcellular resolution

### 4.2 Xenium-PhenoCycler Alignment
**File**: `src/alignment/xenium_phenocycler_aligner.py`

**Considerations**:
- Different resolution scales
- Multi-channel alignment
- Subcellular vs. cellular features

### 4.3 Integration & Testing
- Unit tests for each component
- Integration tests for workflows
- Example notebooks

---

## Code Deletion Strategy

### Safe to Delete (No Dependencies)
- `DOIT_GetDATA_LUAD3B.py` - Replace with generic loader
- Sample-specific if/elif blocks
- Hardcoded LUAD3B paths

### Refactor (Keep Core Logic)
- `Parse_Visium_HE.py` - Extract to generic processor
- `Parse_PhenoCycler_QP.py` - Extract to generic processor
- `Align_Visium-PhenoCycler.py` - Extract to generic aligner

### Keep (Reusable)
- `util/image.py` - Core image operations
- `util/html.py` - Visualization
- `util/projection.py` - Coordinate transforms
- R scripts (for now)

---

## Backward Compatibility

### Maintain Support For
- Existing Visium-PhenoCycler workflows
- Current output directory structure (optional)
- Existing parameter values

### Migration Path
1. New code runs in parallel
2. Gradual replacement of old scripts
3. Deprecation warnings for old APIs
4. Final cleanup in v2.0

---

## Testing Strategy

### Unit Tests
- Image processing functions
- Mask generation
- Alignment algorithms
- Configuration loading

### Integration Tests
- Full Visium pipeline
- Full PhenoCycler pipeline
- Xenium pipeline
- Multi-modality workflows

### Validation
- Compare outputs with current implementation
- Benchmark performance
- Validate alignment quality

---

## Success Criteria

✓ Support Xenium OME-TIFF files
✓ Support arbitrary OME-TIFF files
✓ Maintain Visium-PhenoCycler compatibility
✓ Remove sample-specific hardcoding
✓ Configurable parameters
✓ Modular, reusable components
✓ Comprehensive documentation
✓ Unit and integration tests


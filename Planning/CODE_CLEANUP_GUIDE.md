# Code Cleanup and Modification Guide

## 1. Files to DELETE

### 1.1 Sample-Specific Orchestrators
**Files**:
- `src/DOIT_LUAD3B.py` - Main orchestrator
- `src/DOIT_GetDATA_LUAD3B.py` - Data download
- `src/DOIT_Visium_LUAD3B.py` - Wrapper
- `src/DOIT_PhenoCycler_LUAD3B.py` - Wrapper
- `src/DOIT_Normalize_LUAD3B.py` - Wrapper
- `src/DOIT_Align_LUAD3B.py` - Wrapper
- `src/DOIT_Eval_LUAD3B.py` - Wrapper
- `src/DOIT_Clustering_LUAD3B.py` - Wrapper
- `src/DOIT_GetROI_LUAD3B.py` - Wrapper

**Reason**: Replaced by unified pipeline with configuration

**Replacement**: `src/pipeline/pipeline.py`

### 1.2 Deprecated Wrappers
**Files**:
- `src/Clustering_Visium.py` - Redundant wrapper
- `src/GetDATA.py` - Generic but unused

**Reason**: Functionality moved to pipeline

---

## 2. Files to REFACTOR

### 2.1 Parse_Visium_HE.py (659 lines)

**Current Issues**:
- Hardcoded sample-specific parameters
- Fiducial detection only for Visium
- Tightly coupled to SpaceRanger format
- Hardcoded directory structure

**Refactoring Plan**:
```
Parse_Visium_HE.py
├── Extract → src/processors/image_processor.py
├── Extract → src/processors/circle_detector.py
├── Extract → src/processors/mask_generator.py
└── Keep → Legacy wrapper (deprecated)
```

**Key Changes**:
1. Remove `if sid == "FFPE_LUAD_*"` blocks
2. Create `CircleDetector` class with configurable params
3. Create `MaskGenerator` class
4. Support arbitrary image formats
5. Make SpaceRanger integration optional

**Estimated Effort**: 4-6 hours

### 2.2 Parse_PhenoCycler_QP.py (788 lines)

**Current Issues**:
- Hardcoded page selection: `[22, 4, 0, 1, 2, 10, 12, 21]`
- Tightly coupled to QPTIFF format
- Hardcoded thresholds
- Hardcoded directory structure

**Refactoring Plan**:
```
Parse_PhenoCycler_QP.py
├── Extract → src/processors/tiff_processor.py
├── Extract → src/processors/ometiff_reader.py
├── Extract → src/processors/channel_selector.py
└── Keep → Legacy wrapper (deprecated)
```

**Key Changes**:
1. Create `OMETiffReader` class
2. Create `ChannelSelector` class
3. Make page selection configurable
4. Support arbitrary TIFF formats
5. Generic metadata extraction

**Estimated Effort**: 6-8 hours

### 2.3 Align_Visium-PhenoCycler.py (1059 lines)

**Current Issues**:
- Assumes binary masks only
- Hardcoded search parameters
- Tightly coupled to Visium-PhenoCycler
- Complex nested loops

**Refactoring Plan**:
```
Align_Visium-PhenoCycler.py
├── Extract → src/alignment/aligner.py
├── Extract → src/alignment/fitness.py
├── Extract → src/alignment/search_strategy.py
└── Keep → Legacy wrapper (deprecated)
```

**Key Changes**:
1. Create `Aligner` class
2. Create `FitnessFunction` interface
3. Create `SearchStrategy` interface
4. Support multiple optimization methods
5. Configurable search space

**Estimated Effort**: 8-10 hours

### 2.4 util/image.py (190 lines)

**Current Status**: Mostly reusable

**Changes Needed**:
1. Add docstrings
2. Add type hints
3. Extract color definitions to config
4. Add unit tests
5. Optimize performance

**Estimated Effort**: 2-3 hours

---

## 3. Hardcoded Values to Extract

### 3.1 Binary Thresholds
```python
# Current (scattered)
binary_th = 10  # PhenoCycler
binary_th = 160  # Visium (FFPE_LUAD_3_B)
binary_th = 80   # Visium (FFPE_LUAD_2_C)

# New (config-driven)
config.processing.visium.binarization.threshold
config.processing.phenocycler.binarization.threshold
config.processing.xenium.binarization.threshold
```

### 3.2 Morphology Parameters
```python
# Current (scattered)
kernel = np.ones((2,2), np.uint8)
iterations = 5  # or 10, or 2

# New (config-driven)
config.processing.{modality}.morphology.kernel_size
config.processing.{modality}.morphology.dilate_iter
config.processing.{modality}.morphology.erode_iter
```

### 3.3 Contour Thresholds
```python
# Current (scattered)
hole_th = 800      # Visium
hole_th = 10000    # PhenoCycler
tiss_th = 100      # Visium
tiss_th = 10000    # PhenoCycler

# New (config-driven)
config.processing.{modality}.contour.hole_threshold
config.processing.{modality}.contour.tissue_threshold
```

### 3.4 Circle Detection Parameters
```python
# Current (hardcoded per sample)
minRadius = 10  # FFPE_LUAD_3_B
minRadius = 6   # FFPE_LUAD_2_C
minRadius = 8   # FFPE_LUAD_4_C

# New (config-driven)
config.processing.visium.circle_detection.minRadius
config.processing.visium.circle_detection.maxRadius
config.processing.visium.circle_detection.param1
config.processing.visium.circle_detection.param2
```

---

## 4. Directory Structure Changes

### 4.1 Current Structure
```
src/
├── DOIT_*.py (9 files)
├── Parse_*.py (2 files)
├── Align_*.py (1 file)
├── Clustering_Visium.py
├── GetDATA.py
├── Normalize_Visium.py
├── Eval_Visium-PhenoCycler.py
├── GetROI_Visium-PhenoCycler.py
├── exec_*.r (2 files)
└── util/
    ├── html.py
    ├── image.py
    ├── load_data.py
    └── projection.py
```

### 4.2 Proposed Structure
```
src/
├── pipeline/
│   ├── pipeline.py (new)
│   └── workflow.yaml (new)
├── core/
│   ├── spatial_data.py (new)
│   ├── visium_data.py (new)
│   ├── xenium_data.py (new)
│   └── ometiff_data.py (new)
├── processors/
│   ├── image_processor.py (new)
│   ├── tiff_processor.py (new)
│   ├── circle_detector.py (new)
│   ├── mask_generator.py (new)
│   └── channel_selector.py (new)
├── alignment/
│   ├── aligner.py (new)
│   ├── fitness.py (new)
│   └── search_strategy.py (new)
├── analysis/
│   ├── correlation.py (new)
│   └── clustering.py (new)
├── config/
│   ├── parameters.yaml (new)
│   └── config_loader.py (new)
├── util/
│   ├── image.py (refactored)
│   ├── html.py (kept)
│   ├── projection.py (kept)
│   └── load_data.py (kept)
├── scripts/
│   ├── legacy_parse_visium.py (deprecated)
│   ├── legacy_parse_phenocycler.py (deprecated)
│   └── legacy_align.py (deprecated)
└── exec/
    ├── preprocess.r (kept)
    └── clustering.r (kept)
```

---

## 5. Deletion Priority

### Phase 1 (Immediate)
- DOIT_GetDATA_LUAD3B.py
- GetDATA.py
- Clustering_Visium.py

### Phase 2 (After refactoring)
- DOIT_*.py (all 9 files)
- Parse_Visium_HE.py (move to legacy)
- Parse_PhenoCycler_QP.py (move to legacy)
- Align_Visium-PhenoCycler.py (move to legacy)

### Phase 3 (After validation)
- Legacy wrappers
- Old test files

---

## 6. Backward Compatibility

### Maintain
- Output format (optional)
- Parameter values
- Visium-PhenoCycler workflow

### Deprecate
- DOIT_* scripts
- Sample-specific logic
- Hardcoded paths

### Migrate
- Users → New pipeline API
- Scripts → Configuration files
- Parameters → Config system


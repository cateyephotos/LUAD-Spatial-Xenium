# Quick Reference Guide

## Project Goals Summary

### Current State
- Visium + PhenoCycler integration pipeline
- 8-step workflow with hardcoded LUAD3B sample logic
- Specialized for specific data formats

### Target State
- Xenium + PhenoCycler integration
- Generic OME-TIFF support
- Configurable, modular architecture
- Backward compatible with Visium

---

## Key Files Overview

### To DELETE (9 files)
```
DOIT_LUAD3B.py
DOIT_GetDATA_LUAD3B.py
DOIT_Visium_LUAD3B.py
DOIT_PhenoCycler_LUAD3B.py
DOIT_Normalize_LUAD3B.py
DOIT_Align_LUAD3B.py
DOIT_Eval_LUAD3B.py
DOIT_Clustering_LUAD3B.py
DOIT_GetROI_LUAD3B.py
```

### To REFACTOR (3 files)
```
Parse_Visium_HE.py (659 lines)
  → Extract to: image_processor.py, circle_detector.py, mask_generator.py

Parse_PhenoCycler_QP.py (788 lines)
  → Extract to: tiff_processor.py, ometiff_reader.py, channel_selector.py

Align_Visium-PhenoCycler.py (1059 lines)
  → Extract to: aligner.py, fitness.py, search_strategy.py
```

### To KEEP (4 files)
```
util/image.py (190 lines) - Core image operations
util/html.py - Visualization
util/projection.py - Coordinate transforms
util/load_data.py - Data loading
```

---

## Hardcoded Elements to Extract

### Sample-Specific Logic
```python
if sid == "FFPE_LUAD_2_C":
    circles = cv2.HoughCircles(..., minRadius=6, maxRadius=10)
elif sid == "FFPE_LUAD_4_C":
    circles = cv2.HoughCircles(..., minRadius=8, maxRadius=10)
else:  # "FFPE_LUAD_3_B"
    circles = cv2.HoughCircles(..., minRadius=10, maxRadius=10)
```
**Action**: Move to config/parameters.yaml

### Fixed Thresholds
```python
binary_th = 10          # PhenoCycler
binary_th = 160         # Visium (FFPE_LUAD_3_B)
binary_th = 80          # Visium (FFPE_LUAD_2_C)
hole_th = 800           # Visium
hole_th = 10000         # PhenoCycler
tiss_th = 100           # Visium
tiss_th = 10000         # PhenoCycler
```
**Action**: Move to config/parameters.yaml

### Fixed Page Selection
```python
PASSED = [22, 4, 0, 1, 2, 10, 12, 21]  # PhenoCycler pages
```
**Action**: Make configurable per sample

### Directory Structure
```python
RESULTDIR = WORKDIR + "/" + sid  # e.g., "FFPE_LUAD_3_B"
PREFIX = sid + "-" + "Visium"
MASKDIR = RESULTDIR + "/" + PREFIX + "-" + "MASK"
```
**Action**: Generalize with templates

---

## Processing Pipeline

### Current 8-Step Workflow
1. **GetDATA** - Download sample
2. **Visium** - Generate Visium mask
3. **PhenoCycler** - Generate PhenoCycler mask
4. **Normalize** - Seurat normalization
5. **Align** - Mask alignment
6. **Eval** - Correlation analysis
7. **Clustering** - Seurat clustering
8. **GetROI** - ROI extraction

### New Modular Approach
```
Pipeline
├── Load Data
├── Generate Masks (per modality)
├── Align Masks
├── Analyze Correlation
├── Cluster (optional)
└── Extract ROI (optional)
```

---

## Data Format Support

### Current
- **Visium**: PNG H&E + SpaceRanger JSON/CSV
- **PhenoCycler**: QPTIFF with XML metadata

### Target
- **Visium**: PNG H&E + SpaceRanger JSON/CSV (keep)
- **PhenoCycler**: QPTIFF with XML metadata (keep)
- **Xenium**: OME-TIFF with OME-XML metadata (new)
- **Generic**: Any OME-TIFF file (new)

---

## Resolution Scales

| Modality | Resolution | Scale Factor |
|----------|-----------|--------------|
| Visium | 100 µm | 1.0 |
| Xenium | 0.5 µm | 0.005 |
| PhenoCycler | 0.3 µm | 0.003 |

**Alignment Strategy**: Normalize to common resolution

---

## Configuration System

### New File: config/parameters.yaml
```yaml
processing:
  visium:
    circle_detection:
      minRadius: 10
      maxRadius: 10
    binarization:
      threshold: 160
    morphology:
      kernel_size: 2
      dilate_iter: 2
  
  xenium:
    binarization:
      threshold: 100
    morphology:
      kernel_size: 3
  
  phenocycler:
    binarization:
      threshold: 10
    morphology:
      kernel_size: 2

alignment:
  zoom_range: [0.5, 2.0]
  shift_range: [-50, 50]
  rotate_range: [0, 360]
```

---

## New Architecture

### Core Classes
```python
SpatialData (abstract)
├── VisiumData
├── XeniumData
└── OMETiffData

Aligner
├── fit_zoom()
├── fit_shift()
├── fit_rotate()
└── optimize()

Pipeline
├── load_data()
├── generate_masks()
├── align()
└── analyze()
```

---

## Implementation Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| 1 | 2 weeks | Abstraction layer, config system |
| 2 | 2 weeks | Modularize processors, alignment |
| 3 | 2 weeks | Refactor pipeline, remove DOIT_* |
| 4 | 2 weeks | Xenium support, testing |

**Total**: ~8 weeks

---

## Success Metrics

✓ Xenium OME-TIFF support
✓ Generic OME-TIFF support
✓ Visium-PhenoCycler backward compatibility
✓ No sample-specific hardcoding
✓ Configurable parameters
✓ Modular, testable components
✓ Comprehensive documentation
✓ Unit + integration tests
✓ Performance: < 30 min full pipeline

---

## Next Steps

1. **Review** this documentation
2. **Approve** refactoring roadmap
3. **Create** Planning/IMPLEMENTATION_LOG.md
4. **Begin** Phase 1 (abstraction layer)
5. **Track** progress in Planning folder


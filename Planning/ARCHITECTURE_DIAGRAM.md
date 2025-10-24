# Architecture Diagrams

## Current Architecture (Monolithic)

```
DOIT_LUAD3B.py (Orchestrator)
    ├── DOIT_GetDATA_LUAD3B.py
    ├── DOIT_Visium_LUAD3B.py
    │   └── Parse_Visium_HE.py (659 lines)
    │       ├── Circle detection (Hough)
    │       ├── Binarization
    │       ├── Morphology (D-E-D)
    │       └── Contour extraction
    ├── DOIT_PhenoCycler_LUAD3B.py
    │   └── Parse_PhenoCycler_QP.py (788 lines)
    │       ├── QPTIFF parsing
    │       ├── Channel superposition
    │       ├── Binarization
    │       ├── Morphology (D-E-D)
    │       └── Contour extraction
    ├── DOIT_Normalize_LUAD3B.py
    │   └── exec_preprocess.r (Seurat)
    ├── DOIT_Align_LUAD3B.py
    │   └── Align_Visium-PhenoCycler.py (1059 lines)
    │       ├── Zoom optimization
    │       ├── Shift optimization
    │       ├── Rotate optimization
    │       └── IoU fitness
    ├── DOIT_Eval_LUAD3B.py
    ├── DOIT_Clustering_LUAD3B.py
    │   └── exec_clustering.r (Seurat)
    └── DOIT_GetROI_LUAD3B.py

Utilities:
    ├── util/image.py (190 lines)
    ├── util/html.py
    ├── util/projection.py
    └── util/load_data.py

Issues:
    ❌ Hardcoded sample names (FFPE_LUAD_3_B)
    ❌ Hardcoded parameters (thresholds, kernels)
    ❌ Hardcoded page selection
    ❌ No configuration system
    ❌ No abstraction layer
    ❌ Tightly coupled to Visium/PhenoCycler
```

---

## Proposed Architecture (Modular)

```
Pipeline (Unified Entry Point)
    ├── Config System
    │   ├── parameters.yaml
    │   └── config_loader.py
    │
    ├── Core Data Layer
    │   ├── SpatialData (abstract)
    │   ├── VisiumData
    │   ├── XeniumData
    │   └── OMETiffData
    │
    ├── Processing Layer
    │   ├── Processors
    │   │   ├── image_processor.py
    │   │   ├── circle_detector.py
    │   │   ├── mask_generator.py
    │   │   ├── tiff_processor.py
    │   │   ├── ometiff_reader.py
    │   │   └── channel_selector.py
    │   │
    │   └── Mask Generation
    │       ├── Visium masks
    │       ├── Xenium masks
    │       └── PhenoCycler masks
    │
    ├── Alignment Layer
    │   ├── Aligner (main)
    │   ├── fitness.py (IoU, MI, etc.)
    │   └── search_strategy.py (exhaustive, coarse-to-fine, etc.)
    │
    ├── Analysis Layer
    │   ├── correlation.py
    │   ├── clustering.py (R wrapper)
    │   └── roi_extraction.py
    │
    └── Utilities
        ├── image.py (refactored)
        ├── html.py
        ├── projection.py
        └── load_data.py

Benefits:
    ✅ Configurable parameters
    ✅ Modular components
    ✅ Multiple data format support
    ✅ Reusable processors
    ✅ Testable architecture
    ✅ Extensible design
```

---

## Data Flow Comparison

### Current (Monolithic)
```
Input Data
    ↓
DOIT_Visium_LUAD3B.py
    ↓
Parse_Visium_HE.py (hardcoded logic)
    ↓
Visium Mask
    ↓
DOIT_Align_LUAD3B.py
    ↓
Align_Visium-PhenoCycler.py (hardcoded logic)
    ↓
Aligned Masks
    ↓
Output
```

### Proposed (Modular)
```
Input Data
    ↓
Pipeline.load_data()
    ↓
SpatialData Factory
    ├── VisiumData
    ├── XeniumData
    └── OMETiffData
    ↓
Config System (parameters.yaml)
    ↓
Processor Selection
    ├── ImageProcessor
    ├── TiffProcessor
    └── OMETiffReader
    ↓
Mask Generation (configurable)
    ↓
Aligner (configurable)
    ↓
Analysis (optional)
    ↓
Output
```

---

## File Organization

### Current Structure
```
src/
├── DOIT_*.py (9 files) ❌ DELETE
├── Parse_*.py (2 files) ⚠️ REFACTOR
├── Align_*.py (1 file) ⚠️ REFACTOR
├── Clustering_Visium.py ❌ DELETE
├── GetDATA.py ❌ DELETE
├── Normalize_Visium.py ⚠️ KEEP (wrapper)
├── Eval_Visium-PhenoCycler.py ⚠️ KEEP (wrapper)
├── GetROI_Visium-PhenoCycler.py ⚠️ KEEP (wrapper)
├── exec_*.r (2 files) ✅ KEEP
└── util/ ✅ KEEP (refactor)
```

### Proposed Structure
```
src/
├── pipeline/
│   ├── pipeline.py ✨ NEW
│   └── workflow.yaml ✨ NEW
├── core/
│   ├── spatial_data.py ✨ NEW
│   ├── visium_data.py ✨ NEW
│   ├── xenium_data.py ✨ NEW
│   └── ometiff_data.py ✨ NEW
├── processors/
│   ├── image_processor.py ✨ NEW
│   ├── circle_detector.py ✨ NEW
│   ├── mask_generator.py ✨ NEW
│   ├── tiff_processor.py ✨ NEW
│   ├── ometiff_reader.py ✨ NEW
│   └── channel_selector.py ✨ NEW
├── alignment/
│   ├── aligner.py ✨ NEW
│   ├── fitness.py ✨ NEW
│   └── search_strategy.py ✨ NEW
├── analysis/
│   ├── correlation.py ✨ NEW
│   ├── clustering.py ✨ NEW
│   └── roi_extraction.py ✨ NEW
├── config/
│   ├── parameters.yaml ✨ NEW
│   ├── config_loader.py ✨ NEW
│   └── defaults.py ✨ NEW
├── util/
│   ├── image.py ✅ REFACTOR
│   ├── html.py ✅ KEEP
│   ├── projection.py ✅ KEEP
│   └── load_data.py ✅ KEEP
├── legacy/
│   ├── parse_visium_he.py (deprecated)
│   ├── parse_phenocycler_qp.py (deprecated)
│   └── align_visium_phenocycler.py (deprecated)
├── exec/
│   ├── preprocess.r ✅ KEEP
│   └── clustering.r ✅ KEEP
└── tests/
    ├── test_spatial_data.py ✨ NEW
    ├── test_processors.py ✨ NEW
    ├── test_alignment.py ✨ NEW
    └── test_pipeline.py ✨ NEW
```

---

## Class Hierarchy

### SpatialData Hierarchy
```
SpatialData (abstract)
├── VisiumData
│   ├── load_image() → PNG
│   ├── get_metadata() → JSON/CSV
│   └── generate_mask() → binary
├── XeniumData
│   ├── load_image() → OME-TIFF
│   ├── get_metadata() → OME-XML
│   └── generate_mask() → binary
└── OMETiffData
    ├── load_image() → OME-TIFF
    ├── get_metadata() → OME-XML
    └── generate_mask() → binary
```

### Processor Hierarchy
```
Processor (abstract)
├── ImageProcessor
│   ├── CircleDetector
│   └── MaskGenerator
├── TiffProcessor
│   ├── OMETiffReader
│   └── ChannelSelector
└── MaskGenerator
    ├── BinarizationMask
    ├── MorphologyMask
    └── ContourMask
```

### Aligner Hierarchy
```
Aligner
├── SearchStrategy (abstract)
│   ├── ExhaustiveSearch
│   ├── CoarseToFineSearch
│   └── GradientSearch
└── FitnessFunction (abstract)
    ├── IoUFitness
    ├── MutualInformationFitness
    └── CrossCorrelationFitness
```

---

## Workflow Comparison

### Current Workflow
```
Step 1: GetDATA (hardcoded LUAD3B)
Step 2: Visium (hardcoded parameters)
Step 3: PhenoCycler (hardcoded page selection)
Step 4: Normalize (R script)
Step 5: Align (hardcoded search space)
Step 6: Eval (hardcoded correlations)
Step 7: Clustering (R script)
Step 8: GetROI (hardcoded ROI extraction)
```

### Proposed Workflow
```
Load Config (parameters.yaml)
    ↓
Load Data (any format)
    ↓
Generate Masks (configurable)
    ↓
Align Masks (configurable)
    ↓
Analyze (optional)
    ├── Correlation
    ├── Clustering
    └── ROI Extraction
    ↓
Output Results
```

---

## Migration Path

```
Phase 1: Abstraction Layer
    ├── Create SpatialData classes
    ├── Create Config system
    └── Parallel to existing code

Phase 2: Modularization
    ├── Extract processors
    ├── Extract alignment
    └── Parallel to existing code

Phase 3: Pipeline Refactoring
    ├── Create unified pipeline
    ├── Deprecate DOIT_* scripts
    └── Maintain backward compatibility

Phase 4: Xenium Support
    ├── Implement XeniumData
    ├── Test workflows
    └── Full integration
```


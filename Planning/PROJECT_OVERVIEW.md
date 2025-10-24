# LUAD-Spatial-Xenium Project Overview

## Current Project Status
**Date**: 2025-10-23

### Current Implementation
The existing codebase is a specialized pipeline for **multimodal spatial omics analysis** integrating:
- **10x Genomics Visium** (spatial transcriptomics with H&E staining)
- **Akoya Biosciences PhenoCycler** (multiplexed immunofluorescence with QPTIFF format)

### Current Workflow (8-Step Pipeline)
1. **GetDATA**: Download and extract sample data
2. **Visium**: Generate tissue masks from H&E images
3. **PhenoCycler**: Generate tissue masks from QPTIFF fluorescence data
4. **Normalize**: SCTransform normalization of Visium expression
5. **Align**: Affine transformation alignment (scale, translate, rotate) with IoU optimization
6. **Eval**: Correlation analysis between Visium genes and PhenoCycler antibodies
7. **Clustering**: Seurat-based clustering of Visium spots
8. **GetROI**: Extract and integrate aligned regions of interest

---

## Project Goals - Xenium Integration

### Primary Objective
Transform the codebase to support **10x Xenium** spatial omics data alongside PhenoCycler, enabling:

1. **Xenium-PhenoCycler Alignment**
   - Align Xenium OME-TIFF files with Akoya Biosciences PhenoCycler QPTIFF files
   - Support user-provided OME-TIFF files from various sources

2. **Flexible Multi-Modality Integration**
   - Generic OME-TIFF support (not just Xenium)
   - Maintain backward compatibility with Visium pipeline
   - Support arbitrary spatial omics data formats

3. **Streamlined Architecture**
   - Remove Visium-specific hardcoding
   - Eliminate LUAD3B sample-specific logic
   - Create modular, reusable components

---

## Key Differences: Xenium vs Visium

| Aspect | Visium | Xenium |
|--------|--------|--------|
| **Data Format** | PNG (H&E) + SpaceRanger output | OME-TIFF (multi-channel) |
| **Resolution** | ~100 µm spots | ~0.5 µm subcellular |
| **Channels** | Single H&E image | Multi-channel fluorescence |
| **Metadata** | JSON scalefactors | OME-XML metadata |
| **Mask Generation** | Circle detection (fiducials) | Fluorescence intensity thresholding |

---

## Proposed Architecture Changes

### Phase 1: Abstraction Layer
- Create generic `SpatialData` interface
- Implement `VisiumData`, `XeniumData`, `OMETiffData` classes
- Decouple mask generation from specific formats

### Phase 2: Modularization
- Extract alignment logic into reusable module
- Create generic correlation analysis
- Separate visualization from data processing

### Phase 3: Configuration-Driven Pipeline
- Replace hardcoded parameters with config files
- Support multiple sample processing
- Enable custom workflows

---

## Code Deletions & Modifications

### Candidates for Removal
- Sample-specific logic (FFPE_LUAD_3_B hardcoding)
- Visium-specific circle detection
- DOIT_GetDATA (replace with generic data loader)
- R script dependencies (consider Python alternatives)

### Candidates for Refactoring
- `Parse_Visium_HE.py` → Generic image parser
- `Parse_PhenoCycler_QP.py` → Generic TIFF parser
- `Align_Visium-PhenoCycler.py` → Generic alignment engine
- Utility functions → Modular library

---

## Next Steps
1. Document current implementation details
2. Identify core vs. sample-specific code
3. Design abstraction interfaces
4. Plan incremental refactoring


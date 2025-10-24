# Current Implementation Analysis

## File Structure Overview

### Main Pipeline Scripts (DOIT_*.py)
- **DOIT_LUAD3B.py**: Orchestrator - calls all 8 steps sequentially
- **DOIT_GetDATA_LUAD3B.py**: Downloads LUAD3B_dat.tgz
- **DOIT_Visium_LUAD3B.py**: Calls Parse_Visium_HE.py
- **DOIT_PhenoCycler_LUAD3B.py**: Calls Parse_PhenoCycler_QP.py
- **DOIT_Normalize_LUAD3B.py**: R-based Seurat normalization
- **DOIT_Align_LUAD3B.py**: Calls Align_Visium-PhenoCycler.py
- **DOIT_Eval_LUAD3B.py**: Correlation analysis
- **DOIT_Clustering_LUAD3B.py**: R-based Seurat clustering
- **DOIT_GetROI_LUAD3B.py**: ROI extraction and integration

### Generic Processing Scripts
- **Parse_Visium_HE.py** (659 lines): H&E image processing
  - Fiducial marker detection (Hough circles)
  - Tissue mask generation via binarization
  - Dilation/erosion morphology
  - Contour extraction
  
- **Parse_PhenoCycler_QP.py** (788 lines): QPTIFF processing
  - Multi-page TIFF parsing with XML metadata
  - Fluorescence intensity thresholding
  - Multi-channel superposition
  - Mask generation with hole detection

- **Align_Visium-PhenoCycler.py** (1059 lines): Alignment engine
  - Zoom (scaling) optimization
  - Translation (shift) optimization
  - Rotation optimization
  - IoU-based fitness evaluation
  - Exhaustive grid search refinement

### Utility Modules (src/util/)
- **image.py** (190 lines): Image processing utilities
  - Color definitions (BGR format)
  - Zoom, shift, rotate, centering functions
  - IoU calculation (COUNT function)
  - Morphological operations

- **html.py**: HTML report generation
- **load_data.py**: Data loading utilities
- **projection.py**: Coordinate transformation

---

## Key Hardcoded Elements

### Sample-Specific Logic
```python
# Parse_Visium_HE.py
if sid == "FFPE_LUAD_2_C":
    circles = cv2.HoughCircles(..., minRadius=6, maxRadius=10)
elif sid == "FFPE_LUAD_4_C":
    circles = cv2.HoughCircles(..., minRadius=8, maxRadius=10)
else: # "FFPE_LUAD_3_B"
    circles = cv2.HoughCircles(..., minRadius=10, maxRadius=10)
```

### Fixed Parameters
- Binary thresholds: 10, 160, 80 (sample-dependent)
- Morphology kernels: 2x2, iterations: 2, 5, 10
- Hole thresholds: 800 (Visium), 10000 (PhenoCycler)
- Tissue thresholds: 100 (Visium), 10000 (PhenoCycler)
- Circle detection parameters (minDist, param1, param2)

### Data Format Assumptions
- Visium: PNG H&E + SpaceRanger JSON/CSV
- PhenoCycler: QPTIFF with XML metadata
- Output: Always creates "FFPE_LUAD_3_B" directory structure

---

## Processing Pipeline Details

### Visium Mask Generation
1. Load PNG H&E image
2. Trim edges (20px)
3. Convert to grayscale
4. Detect fiducial circles (Hough)
5. Remove circles (white fill)
6. Binarize (threshold)
7. Dilate/Erode/Dilate morphology
8. Find contours
9. Generate mask with/without holes

### PhenoCycler Mask Generation
1. Load QPTIFF pages (extract XML metadata)
2. Select subset of pages (hardcoded: [22, 4, 0, 1, 2, 10, 12, 21])
3. Superimpose selected channels
4. Binarize (threshold > 10)
5. Dilate/Erode/Dilate morphology
6. Find contours
7. Generate mask with/without holes
8. Generate individual page masks

### Alignment Algorithm
1. **Zoom Phase**: Test scaling ratios (0.5-2.0)
2. **Shift Phase**: Test translations (±50 pixels)
3. **Rotate Phase**: Test rotations (0-360°)
4. **Optimization Phase**: Grid search around best solution
5. **Fitness**: IoU = (AND) / (OR) of binary masks

---

## Dependencies

### Python Packages
- numpy, pandas, cv2, tifffile
- matplotlib (visualization)
- xml.etree (QPTIFF metadata)

### External Tools
- R 4.3.2+ with Seurat v4.4.0+
- QuPath/StarDist (for cell detection in ROI)

### Data Format Support
- PNG (H&E images)
- QPTIFF (PhenoCycler)
- JSON (SpaceRanger scalefactors)
- CSV (tissue positions)
- TSV (features)

---

## Output Structure
```
FFPE_LUAD_3_B/
├── FFPE_LUAD_3_B-Visium-MASK/
├── FFPE_LUAD_3_B-PhenoCycler-MASK/
├── FFPE_LUAD_3_B-ALIGN/
├── FFPE_LUAD_3_B-EVAL/
├── FFPE_LUAD_3_B-Visium-CLST/
├── FFPE_LUAD_3_B-ROI/
└── FFPE_LUAD_3_B-Visium-NORM/
```


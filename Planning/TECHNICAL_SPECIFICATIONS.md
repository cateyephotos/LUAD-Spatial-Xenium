# Technical Specifications for Xenium Integration

## 1. Data Format Support

### 1.1 Xenium OME-TIFF
**Format**: Multi-page TIFF with OME-XML metadata
**Characteristics**:
- Subcellular resolution (~0.5 µm)
- Multiple fluorescence channels
- OME-XML metadata in TIFF tags
- Typically 100-200 channels

**Metadata to Extract**:
- Physical pixel size (µm)
- Channel names/wavelengths
- Image dimensions
- Acquisition parameters

### 1.2 PhenoCycler QPTIFF
**Format**: Quantitative TIFF (QPTIFF)
**Characteristics**:
- Multi-page TIFF with XML metadata
- Typically 40-50 channels
- XML in page descriptions
- Resolution in nanometers

**Metadata to Extract**:
- Biomarker names
- Resolution (nm)
- Scan profile parameters

### 1.3 Generic OME-TIFF
**Support**: Any OME-TIFF file
**Requirements**:
- Valid OME-XML metadata
- Configurable channel selection
- Flexible resolution handling

---

## 2. Mask Generation Algorithms

### 2.1 Visium (Current)
**Input**: PNG H&E image
**Process**:
1. Fiducial detection (Hough circles)
2. Circle removal
3. Binarization
4. Morphology (D-E-D)
5. Contour extraction

**Output**: Binary mask with/without holes

### 2.2 PhenoCycler (Current)
**Input**: QPTIFF multi-channel
**Process**:
1. Channel selection
2. Superposition
3. Binarization
4. Morphology (D-E-D)
5. Contour extraction

**Output**: Binary mask with/without holes

### 2.3 Xenium (New)
**Input**: OME-TIFF multi-channel
**Process**:
1. Channel selection (DAPI or specified)
2. Intensity thresholding
3. Morphology (configurable)
4. Contour extraction

**Output**: Binary mask with/without holes

---

## 3. Alignment Algorithm

### 3.1 Current Implementation
**Method**: Exhaustive search with IoU optimization

**Phases**:
1. **Zoom**: Scale factor 0.5-2.0 (step 0.1)
2. **Shift**: Translation ±50 pixels (step 1)
3. **Rotate**: 0-360° (step 1°)
4. **Refine**: Grid search around best

**Fitness**: IoU = (AND) / (OR)

### 3.2 Proposed Improvements
**Alternative Methods**:
- Phase correlation (FFT-based)
- Feature matching (SIFT/ORB)
- Mutual information
- Normalized cross-correlation

**Adaptive Search**:
- Coarse-to-fine search
- Adaptive step sizes
- Early termination

---

## 4. Resolution Handling

### 4.1 Resolution Scales
| Modality | Resolution | Unit |
|----------|-----------|------|
| Visium | ~100 | µm |
| Xenium | ~0.5 | µm |
| PhenoCycler | ~0.3 | µm |

### 4.2 Scaling Strategy
**Approach**: Normalize to common resolution
```python
# Convert all to µm
visium_px_size = 100  # µm
xenium_px_size = 0.5  # µm
phenocycler_px_size = 0.3  # µm

# Scale factor for alignment
scale_factor = xenium_px_size / visium_px_size  # 0.005
```

### 4.3 Coordinate Transformation
**Mapping**: Between different resolutions
```python
def transform_coordinates(coords, from_res, to_res):
    scale = to_res / from_res
    return coords * scale
```

---

## 5. Configuration System

### 5.1 Parameter Structure
```yaml
processing:
  visium:
    circle_detection:
      minRadius: 10
      maxRadius: 10
      param1: 25
      param2: 15
    binarization:
      threshold: 160
    morphology:
      kernel_size: 2
      dilate_iter: 2
      erode_iter: 2
  
  xenium:
    binarization:
      threshold: 100
    morphology:
      kernel_size: 3
      dilate_iter: 1
  
  phenocycler:
    binarization:
      threshold: 10
    morphology:
      kernel_size: 2
      dilate_iter: 5

alignment:
  zoom_range: [0.5, 2.0]
  zoom_step: 0.1
  shift_range: [-50, 50]
  shift_step: 1
  rotate_range: [0, 360]
  rotate_step: 1
```

---

## 6. Output Structure

### 6.1 Directory Organization
```
results/
├── sample_name/
│   ├── masks/
│   │   ├── modality1_mask.png
│   │   ├── modality1_mask_with_holes.png
│   │   ├── modality2_mask.png
│   │   └── modality2_mask_with_holes.png
│   ├── alignment/
│   │   ├── transformation_matrix.json
│   │   ├── alignment_result.png
│   │   └── metrics.json
│   ├── correlation/
│   │   ├── correlation_matrix.csv
│   │   └── plots/
│   └── reports/
│       ├── index.html
│       └── data/
```

### 6.2 Metadata Files
**transformation_matrix.json**:
```json
{
  "modality1": "xenium",
  "modality2": "phenocycler",
  "scale": 1.5,
  "translation": [10, -5],
  "rotation": 2.3,
  "iou": 0.87
}
```

---

## 7. API Design

### 7.1 Core Classes
```python
class SpatialData:
    def load_image() -> np.ndarray
    def get_metadata() -> dict
    def generate_mask() -> np.ndarray

class Aligner:
    def align(ref_mask, mov_mask) -> dict
    def transform_coordinates(coords) -> np.ndarray

class Pipeline:
    def process(config) -> dict
    def batch_process(configs) -> list
```

### 7.2 Usage Example
```python
from src.core import XeniumData, PhenoCyclerData
from src.alignment import Aligner

xenium = XeniumData("xenium.ome.tiff")
phenocycler = PhenoCyclerData("phenocycler.qptiff")

xenium_mask = xenium.generate_mask()
phenocycler_mask = phenocycler.generate_mask()

aligner = Aligner()
result = aligner.align(xenium_mask, phenocycler_mask)
```

---

## 8. Performance Targets

- Mask generation: < 1 minute
- Alignment: < 5 minutes
- Full pipeline: < 30 minutes
- Memory usage: < 8 GB


"""
Xenium spatial omics data handler with two-tier architecture.

This module implements the SpatialData interface for 10x Genomics Xenium data,
supporting both minimal (Tier 1: image-only) and full (Tier 2: complete output) workflows.

Tier 1 (Minimal): Requires only morphology.ome.tif
- Basic image loading and OME-XML metadata extraction
- Simple intensity-based mask generation
- Suitable for image alignment workflows

Tier 2 (Enhanced): Requires full Xenium output directory
- Loads cells.parquet, cell_boundaries.parquet, transcripts.parquet, etc.
- Polygon-based segmentation using cell boundaries
- Gene expression data and transcript coordinates
- Rich analysis capabilities
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import xml.etree.ElementTree as ET
import json
import warnings

try:
    import tifffile
except ImportError:
    tifffile = None

try:
    import pandas as pd
except ImportError:
    pd = None

from .spatial_data import SpatialData


class XeniumData(SpatialData):
    """
    Handler for 10x Genomics Xenium spatial omics data with two-tier support.

    **Tier 1 (Minimal - Image Only):**
    - Requires: morphology.ome.tif
    - Provides: Image data, basic metadata, intensity-based masks
    - Use case: Image alignment with other modalities

    **Tier 2 (Enhanced - Full Output):**
    - Requires: Complete Xenium output directory
    - Provides: Cell metadata, boundaries, transcripts, gene panel, quality metrics
    - Use case: Comprehensive spatial analysis

    Attributes:
        tiff_path (Path): Path to OME-TIFF file
        channels (List[str]): List of channel names
        tier (int): Data tier (1 or 2)
        has_cells (bool): Whether cell data is available
        has_boundaries (bool): Whether boundary polygons are available
        has_transcripts (bool): Whether transcript data is available
        has_gene_panel (bool): Whether gene panel is available
    """

    def __init__(self, data_path: str, filename: str = "morphology.ome.tif"):
        """
        Initialize XeniumData instance with automatic tier detection.

        Args:
            data_path: Path to Xenium data directory or file
            filename: Name of OME-TIFF file (default: morphology.ome.tif)
        """
        super().__init__(data_path, modality="xenium")

        # Handle both file and directory paths
        if self.data_path.is_file():
            self.tiff_path = self.data_path
            self.data_dir = self.data_path.parent
        else:
            self.tiff_path = self.data_path / filename
            self.data_dir = self.data_path

        # Initialize tier detection
        self.tier: int = 1  # Default to Tier 1
        self.channels: List[str] = []
        self._channel_data: Dict[int, np.ndarray] = {}

        # Tier 2 optional data
        self.has_cells: bool = False
        self.has_boundaries: bool = False
        self.has_transcripts: bool = False
        self.has_gene_panel: bool = False
        self.has_metrics: bool = False

        self._cells_data: Optional[pd.DataFrame] = None
        self._cell_boundaries: Optional[pd.DataFrame] = None
        self._nucleus_boundaries: Optional[pd.DataFrame] = None
        self._transcripts_data: Optional[pd.DataFrame] = None
        self._gene_panel: Optional[Dict[str, Any]] = None
        self._metrics: Optional[Dict[str, Any]] = None

        # Load metadata and detect tier
        self._load_metadata()
        self._detect_tier()
    
    def _load_metadata(self) -> None:
        """Load Tier 1 metadata from OME-TIFF file."""
        if not tifffile:
            raise ImportError("tifffile is required for Xenium data. Install with: pip install tifffile")

        if not self.tiff_path.exists():
            raise FileNotFoundError(f"Xenium TIFF not found: {self.tiff_path}")

        try:
            with tifffile.TiffFile(str(self.tiff_path)) as tif:
                # Extract OME-XML metadata
                if hasattr(tif, 'ome_metadata'):
                    self.metadata['ome_xml'] = tif.ome_metadata

                # Extract channel information
                if hasattr(tif, 'pages') and len(tif.pages) > 0:
                    page = tif.pages[0]

                    # Get image dimensions
                    self.metadata['height'] = page.shape[0]
                    self.metadata['width'] = page.shape[1]
                    self.metadata['num_channels'] = len(tif.pages)

                    # Extract resolution from tags
                    if hasattr(page, 'tags'):
                        if 'XResolution' in page.tags:
                            xres = page.tags['XResolution'].value
                            # Convert from pixels/inch to µm/pixel
                            self.resolution = 25400.0 / xres[0]
                        if 'YResolution' in page.tags:
                            yres = page.tags['YResolution'].value
                            self.resolution = 25400.0 / yres[0]

                    # Extract channel names from descriptions
                    for i, p in enumerate(tif.pages):
                        if hasattr(p, 'description') and p.description:
                            try:
                                root = ET.fromstring(p.description)
                                channel_name = root.find('.//Name')
                                if channel_name is not None:
                                    self.channels.append(channel_name.text)
                                else:
                                    self.channels.append(f"Channel_{i}")
                            except:
                                self.channels.append(f"Channel_{i}")
                        else:
                            self.channels.append(f"Channel_{i}")

        except Exception as e:
            raise ValueError(f"Failed to load Xenium metadata: {e}")

    def _detect_tier(self) -> None:
        """Detect available data tier and load optional Tier 2 data."""
        # Check for Tier 2 files
        cells_file = self.data_dir / "cells.parquet"
        boundaries_file = self.data_dir / "cell_boundaries.parquet"
        transcripts_file = self.data_dir / "transcripts.parquet"
        gene_panel_file = self.data_dir / "gene_panel.json"
        metrics_file = self.data_dir / "metrics_summary.csv"

        # Try to load Tier 2 data
        if cells_file.exists():
            try:
                self._load_cells_data()
                self.has_cells = True
            except Exception as e:
                warnings.warn(f"Could not load cells data: {e}")

        if boundaries_file.exists():
            try:
                self._load_boundaries_data()
                self.has_boundaries = True
            except Exception as e:
                warnings.warn(f"Could not load cell boundaries: {e}")

        if transcripts_file.exists():
            try:
                self._load_transcripts_data()
                self.has_transcripts = True
            except Exception as e:
                warnings.warn(f"Could not load transcripts data: {e}")

        if gene_panel_file.exists():
            try:
                self._load_gene_panel()
                self.has_gene_panel = True
            except Exception as e:
                warnings.warn(f"Could not load gene panel: {e}")

        if metrics_file.exists():
            try:
                self._load_metrics()
                self.has_metrics = True
            except Exception as e:
                warnings.warn(f"Could not load metrics: {e}")

        # Determine tier
        if self.has_cells and self.has_boundaries and self.has_transcripts:
            self.tier = 2
            self.metadata['tier'] = 2
            self.metadata['tier_description'] = 'Full Xenium output with cells, boundaries, and transcripts'
        else:
            self.tier = 1
            self.metadata['tier'] = 1
            self.metadata['tier_description'] = 'Minimal Xenium data (image only)'
    
    def _load_cells_data(self) -> None:
        """Load cell metadata from cells.parquet (Tier 2)."""
        if not pd:
            raise ImportError("pandas is required for Tier 2 data. Install with: pip install pandas")

        cells_file = self.data_dir / "cells.parquet"
        self._cells_data = pd.read_parquet(cells_file)
        self.metadata['num_cells'] = len(self._cells_data)
        self.metadata['cell_columns'] = list(self._cells_data.columns)

    def _load_boundaries_data(self) -> None:
        """Load cell and nucleus boundaries from parquet files (Tier 2)."""
        if not pd:
            raise ImportError("pandas is required for Tier 2 data. Install with: pip install pandas")

        cell_boundaries_file = self.data_dir / "cell_boundaries.parquet"
        nucleus_boundaries_file = self.data_dir / "nucleus_boundaries.parquet"

        if cell_boundaries_file.exists():
            self._cell_boundaries = pd.read_parquet(cell_boundaries_file)
            self.metadata['num_cell_boundaries'] = len(self._cell_boundaries)

        if nucleus_boundaries_file.exists():
            self._nucleus_boundaries = pd.read_parquet(nucleus_boundaries_file)
            self.metadata['num_nucleus_boundaries'] = len(self._nucleus_boundaries)

    def _load_transcripts_data(self) -> None:
        """Load transcript coordinates from transcripts.parquet (Tier 2)."""
        if not pd:
            raise ImportError("pandas is required for Tier 2 data. Install with: pip install pandas")

        transcripts_file = self.data_dir / "transcripts.parquet"
        self._transcripts_data = pd.read_parquet(transcripts_file)
        self.metadata['num_transcripts'] = len(self._transcripts_data)
        self.metadata['transcript_columns'] = list(self._transcripts_data.columns)

    def _load_gene_panel(self) -> None:
        """Load gene panel information from gene_panel.json (Tier 2)."""
        gene_panel_file = self.data_dir / "gene_panel.json"
        with open(gene_panel_file, 'r') as f:
            panel_data = json.load(f)

        self._gene_panel = panel_data

        # Extract key information
        if 'payload' in panel_data:
            payload = panel_data['payload']
            if 'panel' in payload:
                panel_info = payload['panel']
                self.metadata['panel_name'] = panel_info.get('identity', {}).get('name', 'Unknown')
                self.metadata['num_genes'] = panel_info.get('num_gene_targets', 0)
                self.metadata['panel_species'] = panel_info.get('species', 'Unknown')
                self.metadata['panel_tissue'] = panel_info.get('tissue', 'Unknown')

            if 'targets' in payload:
                genes = [t['type']['data']['name'] for t in payload['targets']
                        if t['type']['descriptor'] == 'gene']
                self.metadata['genes'] = genes

    def _load_metrics(self) -> None:
        """Load quality metrics from metrics_summary.csv (Tier 2)."""
        if not pd:
            raise ImportError("pandas is required for Tier 2 data. Install with: pip install pandas")

        metrics_file = self.data_dir / "metrics_summary.csv"
        metrics_df = pd.read_csv(metrics_file)

        # Convert to dictionary
        if len(metrics_df) > 0:
            self._metrics = metrics_df.iloc[0].to_dict()
            self.metadata['metrics'] = self._metrics

    def load_image(self, channel: Optional[int] = None) -> np.ndarray:
        """
        Load image data from OME-TIFF.
        
        Args:
            channel: Channel index to load (default: 0)
            
        Returns:
            Image as numpy array (uint16 or uint8)
        """
        if not tifffile:
            raise ImportError("tifffile is required for Xenium data")
        
        if channel is None:
            channel = 0
        
        if channel in self._channel_data:
            return self._channel_data[channel]
        
        if not self.tiff_path.exists():
            raise FileNotFoundError(f"Xenium TIFF not found: {self.tiff_path}")
        
        try:
            img = tifffile.imread(str(self.tiff_path), key=channel)
            self._channel_data[channel] = img
            return img
        except Exception as e:
            raise ValueError(f"Failed to load channel {channel}: {e}")
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get Xenium metadata.
        
        Returns:
            Dictionary with OME-XML, dimensions, channels, etc.
        """
        return self.metadata.copy()
    
    def get_resolution(self) -> float:
        """
        Get Xenium resolution in micrometers.
        
        Returns:
            Resolution in micrometers
        """
        return self.resolution
    
    def get_channels(self) -> List[str]:
        """
        Get list of channel names.
        
        Returns:
            List of channel names
        """
        return self.channels.copy()
    
    def generate_mask(self, **kwargs) -> np.ndarray:
        """
        Generate binary mask from Xenium data.

        **Tier 1 (Image-only)**: Uses intensity-based thresholding
        **Tier 2 (Full output)**: Uses polygon-based segmentation from cell boundaries

        Args:
            channel: Channel index to use (default: 0)
            threshold: Intensity threshold (default: auto, Tier 1 only)
            method: Mask generation method ('auto', 'intensity', 'polygon')
                   'auto' = use polygon if available, else intensity

        Returns:
            Binary mask (uint8, values 0 or 255)
        """
        method = kwargs.get('method', 'auto')

        # Auto-select method based on tier
        if method == 'auto':
            if self.tier == 2 and self.has_boundaries:
                method = 'polygon'
            else:
                method = 'intensity'

        # Use polygon-based mask if available (Tier 2)
        if method == 'polygon' and self.tier == 2 and self.has_boundaries:
            return self._generate_polygon_mask(**kwargs)

        # Fall back to intensity-based mask (Tier 1)
        return self._generate_intensity_mask(**kwargs)

    def _generate_intensity_mask(self, **kwargs) -> np.ndarray:
        """Generate mask using intensity thresholding (Tier 1)."""
        import cv2

        channel = kwargs.get('channel', 0)
        img = self.load_image(channel=channel)

        # Normalize to 0-255 range
        if img.dtype == np.uint16:
            img_norm = (img / 256).astype(np.uint8)
        else:
            img_norm = img

        # Apply threshold
        threshold = kwargs.get('threshold', None)
        if threshold is None:
            # Auto threshold using Otsu's method
            _, mask = cv2.threshold(img_norm, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, mask = cv2.threshold(img_norm, threshold, 255, cv2.THRESH_BINARY)

        return mask

    def _generate_polygon_mask(self, **kwargs) -> np.ndarray:
        """Generate mask from cell boundary polygons (Tier 2)."""
        import cv2

        if not self.has_boundaries or self._cell_boundaries is None:
            warnings.warn("Cell boundaries not available, falling back to intensity mask")
            return self._generate_intensity_mask(**kwargs)

        # Get image dimensions
        img = self.load_image(channel=0)
        height, width = img.shape[:2]

        # Create empty mask
        mask = np.zeros((height, width), dtype=np.uint8)

        try:
            # Draw polygons from cell boundaries
            for idx, row in self._cell_boundaries.iterrows():
                if 'vertex_x' in row and 'vertex_y' in row:
                    # Extract coordinates
                    x_coords = row['vertex_x']
                    y_coords = row['vertex_y']

                    if isinstance(x_coords, (list, np.ndarray)) and isinstance(y_coords, (list, np.ndarray)):
                        points = np.array(list(zip(x_coords, y_coords)), dtype=np.int32)
                        cv2.fillPoly(mask, [points], 255)
        except Exception as e:
            warnings.warn(f"Error drawing polygons: {e}, falling back to intensity mask")
            return self._generate_intensity_mask(**kwargs)

        return mask
    
    def get_cells_data(self) -> Optional[pd.DataFrame]:
        """
        Get cell metadata (Tier 2 only).

        Returns:
            DataFrame with cell data or None if not available
        """
        return self._cells_data.copy() if self._cells_data is not None else None

    def get_cell_boundaries(self) -> Optional[pd.DataFrame]:
        """
        Get cell boundary polygons (Tier 2 only).

        Returns:
            DataFrame with cell boundaries or None if not available
        """
        return self._cell_boundaries.copy() if self._cell_boundaries is not None else None

    def get_nucleus_boundaries(self) -> Optional[pd.DataFrame]:
        """
        Get nucleus boundary polygons (Tier 2 only).

        Returns:
            DataFrame with nucleus boundaries or None if not available
        """
        return self._nucleus_boundaries.copy() if self._nucleus_boundaries is not None else None

    def get_transcripts(self) -> Optional[pd.DataFrame]:
        """
        Get transcript coordinates (Tier 2 only).

        Returns:
            DataFrame with transcript data or None if not available
        """
        return self._transcripts_data.copy() if self._transcripts_data is not None else None

    def get_gene_panel(self) -> Optional[Dict[str, Any]]:
        """
        Get gene panel information (Tier 2 only).

        Returns:
            Dictionary with gene panel data or None if not available
        """
        return self._gene_panel.copy() if self._gene_panel is not None else None

    def get_genes(self) -> Optional[List[str]]:
        """
        Get list of gene names (Tier 2 only).

        Returns:
            List of gene names or None if not available
        """
        if 'genes' in self.metadata:
            return self.metadata['genes'].copy()
        return None

    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Get quality metrics (Tier 2 only).

        Returns:
            Dictionary with metrics or None if not available
        """
        return self._metrics.copy() if self._metrics is not None else None

    def get_tier_info(self) -> Dict[str, Any]:
        """
        Get information about available data tier.

        Returns:
            Dictionary with tier information
        """
        return {
            'tier': self.tier,
            'description': self.metadata.get('tier_description', ''),
            'has_cells': self.has_cells,
            'has_boundaries': self.has_boundaries,
            'has_transcripts': self.has_transcripts,
            'has_gene_panel': self.has_gene_panel,
            'has_metrics': self.has_metrics,
        }

    def validate(self) -> tuple:
        """
        Validate Xenium data.

        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid, msg = super().validate()
        if not is_valid:
            return is_valid, msg

        if not self.tiff_path.exists():
            return False, f"Xenium TIFF not found: {self.tiff_path}"

        if not tifffile:
            return False, "tifffile library not installed"

        return True, ""


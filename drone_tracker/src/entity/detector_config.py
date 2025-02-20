from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class DetectorConfig:
    """Configuration parameters for sphere detection."""
    min_object_size: int = 20  # Minimum diameter in pixels
    max_object_size: int = 200  # Maximum diameter in pixels
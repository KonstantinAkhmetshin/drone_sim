from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class DetectorConfig:
    target_color: Tuple[int, int, int] 
    color_tolerance: int = 20
    min_object_size: int = 100
    max_object_size: int = 10000
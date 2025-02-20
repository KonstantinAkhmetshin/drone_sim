"""
Object detection module using OpenCV for sphere detection.
Uses Hough Circle Transform to detect circular/spherical objects in the image.
"""
import cv2
import numpy as np
from typing import Optional, Tuple
from entity.detector_config import DetectorConfig

class ObjectDetector:
    """Detects spherical objects using circle detection."""
    
    def __init__(self, config: DetectorConfig):
        """
        Initialize detector with configuration parameters.
        
        Args:
            config: Configuration parameters for detection
        """
        self.config = config
        self.min_radius = config.min_object_size // 2
        self.max_radius = config.max_object_size // 2
        
    def detect_object(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect spherical objects using Hough Circle Transform.
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (x, y, width, height) of detected sphere or None
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (9, 9), 2)
        
        # Detect circles using Hough Circle Transform
        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,  # Resolution ratio
            minDist=50,  # Min distance between circles
            param1=50,  # Upper threshold for edge detection
            param2=30,  # Threshold for circle detection
            minRadius=self.min_radius,
            maxRadius=self.max_radius
        )
        
        if circles is not None:
            # Convert to integer coordinates
            circles = np.uint16(np.around(circles))
            
            # Get the first (most prominent) circle
            x, y, r = circles[0][0]
            
            # Convert to bounding box format (x, y, width, height)
            return (int(x - r), int(y - r), int(2 * r), int(2 * r))
            
        return None
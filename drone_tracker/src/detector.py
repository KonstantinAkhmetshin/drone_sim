# File: src/detector.py
"""
Object detection module using OpenCV for visual tracking.
Supports color-based and feature-based detection methods.

-Uses OpenCV for color-based object detection
-Converts images to HSV color space for more robust color detection
-Can detect objects within specified size constraints
-Returns bounding box coordinates of detected objects
"""
import cv2
import numpy as np
from typing import Optional, Tuple, Dict

class ObjectDetector:
    """Detects objects using various computer vision methods."""
    
    def __init__(self, config: Dict):
        """
        Initialize detector with configuration parameters.
        
        Args:
            config: Dictionary containing detection parameters
                   (color ranges, thresholds, etc.)
        """
        self.config = config
        self.target_color = np.array(config["target_color"])
        self.color_tolerance = config["color_tolerance"]
        self.min_size = config["min_object_size"]
        self.max_size = config["max_object_size"]
        
    def detect_color(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect objects based on color thresholding.
        
        Args:
            frame: Input image frame
            
        Returns:
            Tuple of (x, y, width, height) of detected object or None
        """
        # Convert to HSV for better color detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create color mask
        lower = np.array([self.target_color[0] - self.color_tolerance,
                         50, 50])
        upper = np.array([self.target_color[0] + self.color_tolerance,
                         255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)
        
        # Find largest contour within size constraints
        largest_contour = None
        largest_area = 0
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_size < area < self.max_size and area > largest_area:
                largest_contour = contour
                largest_area = area
                
        if largest_contour is not None:
            x, y, w, h = cv2.boundingRect(largest_contour)
            return (x, y, w, h)
        
        return None
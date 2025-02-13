#!/usr/bin/env python3

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass
class DetectionConfig:
    """Configuration parameters for object detection"""
    target_color: Tuple[int, int, int]  # RGB values
    color_tolerance: int
    min_object_size: int
    max_object_size: int
    detection_threshold: float

@dataclass
class Detection:
    """Object detection result"""
    center: Tuple[int, int]  # (x, y) in pixels
    size: float  # Area in pixels
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h)

class ObjectDetector:
    """
    Color-based object detector using OpenCV.
    Detects objects based on color thresholding and contour analysis.
    """
    
    def __init__(self, config: DetectionConfig):
        """
        Initialize the detector with configuration parameters.
        
        Args:
            config (DetectionConfig): Configuration parameters for detection
        """
        self.config = config
        
        # Convert RGB target color to HSV for better color detection
        rgb_color = np.uint8([[self.config.target_color]])
        self.target_hsv = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)[0][0]
        
    def detect(self, image: np.ndarray) -> Optional[Detection]:
        """
        Detect the target object in an image.cv2cv2
        
        Args:
            image (np.ndarray): Input image in BGR format
            
        Returns:
            Optional[Detection]: Detection result if object found, None otherwise
        """
        # Convert image to HSV color space
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create color mask with tolerance
        lower_bound = np.array([
            max(0, self.target_hsv[0] - self.config.color_tolerance),
            max(0, self.target_hsv[1] - self.config.color_tolerance),
            max(0, self.target_hsv[2] - self.config.color_tolerance)
        ])
        
        upper_bound = np.array([
            min(180, self.target_hsv[0] + self.config.color_tolerance),
            min(255, self.target_hsv[1] + self.config.color_tolerance),
            min(255, self.target_hsv[2] + self.config.color_tolerance)
        ])
        
        # Apply color threshold
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # Find the largest contour within size constraints
        valid_contours = [
            cnt for cnt in contours
            if self.config.min_object_size <= cv2.contourArea(cnt) <= self.config.max_object_size
        ]
        
        if not valid_contours:
            return None
            
        # Get the largest valid contour
        largest_contour = max(valid_contours, key=cv2.contourArea)
        
        # Calculate contour properties
        area = cv2.contourArea(largest_contour)
        x, y, w, h = cv2.boundingRect(largest_contour)
        center = (x + w//2, y + h//2)
        
        # Calculate confidence based on area and color match
        roi = image[y:y+h, x:x+w]
        color_confidence = self._calculate_color_confidence(roi)
        size_confidence = self._calculate_size_confidence(area)
        confidence = min(color_confidence * size_confidence, 1.0)
        
        if confidence < self.config.detection_threshold:
            return None
            
        return Detection(
            center=center,
            size=area,
            confidence=confidence,
            bounding_box=(x, y, w, h)
        )
        
    def _calculate_color_confidence(self, roi: np.ndarray) -> float:
        """
        Calculate confidence based on color match.
        
        Args:
            roi (np.ndarray): Region of interest containing the detected object
            
        Returns:
            float: Confidence value between 0 and 1
        """
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Calculate how well the ROI matches the target color
        diff = np.abs(hsv_roi - self.target_hsv)
        color_diff = np.mean(diff) / 255.0
        return 1.0 - color_diff
        
    def _calculate_size_confidence(self, area: float) -> float:
        """
        Calculate confidence based on object size.
        
        Args:
            area (float): Area of detected object in pixels
            
        Returns:
            float: Confidence value between 0 and 1
        """
        # Calculate how well the area fits within the expected range
        min_conf = self.config.min_object_size
        max_conf = self.config.max_object_size
        
        if area < min_conf or area > max_conf:
            return 0.0
            
        # Higher confidence when closer to the middle of the range
        optimal_size = (min_conf + max_conf) / 2
        size_diff = abs(area - optimal_size)
        size_range = (max_conf - min_conf) / 2
        
        return 1.0 - (size_diff / size_range)

    def draw_detection(self, image: np.ndarray, detection: Detection) -> np.ndarray:
        """
        Draw detection results on the image.
        
        Args:
            image (np.ndarray): Input image
            detection (Detection): Detection result
            
        Returns:
            np.ndarray: Image with detection visualization
        """
        output = image.copy()
        
        # Draw bounding box
        x, y, w, h = detection.bounding_box
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Draw center point
        cv2.circle(output, detection.center, 5, (0, 0, 255), -1)
        
        # Add confidence text
        text = f"Conf: {detection.confidence:.2f}"
        cv2.putText(output, text, (x, y - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return output
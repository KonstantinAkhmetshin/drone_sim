#!/usr/bin/env python3

import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional, List
import time

@dataclass
class DetectionConfig:
    """Configuration parameters for object detection"""
    target_color: Tuple[int, int, int]  # RGB values
    color_tolerance: int
    min_object_size: int
    max_object_size: int
    detection_threshold: float

    def validate(self) -> None:
        """Validate configuration parameters"""
        if not all(0 <= x <= 255 for x in self.target_color):
            raise ValueError("Target color values must be between 0 and 255")
        if self.color_tolerance < 0 or self.color_tolerance > 255:
            raise ValueError("Color tolerance must be between 0 and 255")
        if self.min_object_size < 0:
            raise ValueError("Minimum object size must be positive")
        if self.max_object_size < self.min_object_size:
            raise ValueError("Maximum object size must be greater than minimum")
        if not 0 <= self.detection_threshold <= 1:
            raise ValueError("Detection threshold must be between 0 and 1")

@dataclass
class Detection:
    """Object detection result"""
    center: Tuple[int, int]  # (x, y) in pixels
    size: float  # Area in pixels
    confidence: float
    bounding_box: Tuple[int, int, int, int]  # (x, y, w, h)
    timestamp: float  # Time of detection

class ObjectDetector:
    """
    Color-based object detector using OpenCV.
    Detects objects based on color thresholding and contour analysis.
    Includes features for robust detection in various lighting conditions.
    """
    
    def __init__(self, config: DetectionConfig):
        """
        Initialize the detector with configuration parameters.
        
        Args:
            config (DetectionConfig): Configuration parameters for detection
        """
        self.config = config
        self.config.validate()
        
        # Convert RGB target color to HSV for better color detection
        rgb_color = np.uint8([[self.config.target_color]])
        self.target_hsv = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2HSV)[0][0]
        
        # Initialize detection history for tracking
        self.detection_history: List[Detection] = []
        self.history_max_size = 5
        
        # Initialize adaptive parameters
        self.brightness_offset = 0
        self.last_good_detection_time = 0
        
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better detection
        
        Args:
            image: Input BGR image
            
        Returns:
            Preprocessed image
        """
        # Convert to float32 for processing
        float_img = image.astype(np.float32) / 255.0
        
        # Apply adaptive brightness adjustment
        adjusted = cv2.convertScaleAbs(
            float_img, 
            alpha=1.0 + self.brightness_offset/100.0,
            beta=self.brightness_offset
        )
        
        # Apply mild denoising
        denoised = cv2.fastNlMeansDenoisingColored(
            adjusted,
            None,
            10,
            10,
            7,
            21
        )
        
        return denoised
        
    def detect(self, image: np.ndarray) -> Optional[Detection]:
        """
        Detect the target object in an image.
        
        Args:
            image: Input image in BGR format
            
        Returns:
            Optional[Detection]: Detection result if object found, None otherwise
        """
        try:
            # Preprocess image
            processed = self.preprocess_image(image)
            
            # Convert to HSV color space
            hsv_image = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)
            
            # Create color mask with tolerance
            lower_bound = np.array([
                max(0, self.target_hsv[0] - self.config.color_tolerance),
                max(30, self.target_hsv[1] - self.config.color_tolerance),  # Minimum saturation
                max(30, self.target_hsv[2] - self.config.color_tolerance)   # Minimum value
            ])
            
            upper_bound = np.array([
                min(180, self.target_hsv[0] + self.config.color_tolerance),
                min(255, self.target_hsv[1] + self.config.color_tolerance),
                min(255, self.target_hsv[2] + self.config.color_tolerance)
            ])
            
            # Apply color threshold
            mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
            
            # Apply morphological operations to reduce noise
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            
            # Find contours in the mask
            contours, _ = cv2.findContours(
                mask, 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            if not contours:
                return None
                
            # Find valid contours within size constraints
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
            
            # Calculate confidence based on multiple factors
            color_confidence = self._calculate_color_confidence(
                processed[y:y+h, x:x+w]
            )
            
            size_confidence = self._calculate_size_confidence(area)
            shape_confidence = self._calculate_shape_confidence(largest_contour)
            
            # Combine confidences
            confidence = (
                color_confidence * 0.4 +
                size_confidence * 0.3 +
                shape_confidence * 0.3
            )
            
            if confidence < self.config.detection_threshold:
                return None
                
            # Create detection object
            detection = Detection(
                center=center,
                size=area,
                confidence=confidence,
                bounding_box=(x, y, w, h),
                timestamp=time.time()
            )
            
            # Update detection history
            self._update_history(detection)
            
            # Update adaptive parameters
            self._update_adaptive_params(detection)
            
            return detection
            
        except Exception as e:
            print(f"Error in object detection: {e}")
            return None
            
    def _calculate_color_confidence(self, roi: np.ndarray) -> float:
        """
        Calculate confidence based on color match
        
        Args:
            roi: Region of interest containing the detected object
            
        Returns:
            float: Confidence value between 0 and 1
        """
        if roi.size == 0:
            return 0.0
            
        # Convert ROI to HSV
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Calculate color difference
        diff = np.abs(hsv_roi - self.target_hsv)
        
        # Weight hue difference more heavily
        weighted_diff = (diff[:,:,0] * 2 + diff[:,:,1] + diff[:,:,2]) / 4
        
        # Normalize and invert so 1.0 means perfect match
        confidence = 1.0 - (np.mean(weighted_diff) / 255.0)
        return max(0.0, min(1.0, confidence))
        
    def _calculate_size_confidence(self, area: float) -> float:
        """
        Calculate confidence based on object size
        
        Args:
            area: Area of detected object in pixels
            
        Returns:
            float: Confidence value between 0 and 1
        """
        # Calculate how well the area fits within the expected range
        min_conf = self.config.min_object_size
        max_conf = self.config.max_object_size
        optimal_size = (min_conf + max_conf) / 2
        
        # Use gaussian-like function for smooth falloff
        size_diff = abs(area - optimal_size)
        size_range = (max_conf - min_conf) / 2
        
        confidence = np.exp(-(size_diff ** 2) / (2 * size_range ** 2))
        return max(0.0, min(1.0, confidence))
        
    def _calculate_shape_confidence(self, contour: np.ndarray) -> float:
        """
        Calculate confidence based on shape regularity
        
        Args:
            contour: Contour points array
            
        Returns:
            float: Confidence value between 0 and 1
        """
        # Calculate contour metrics
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        
        if perimeter == 0:
            return 0.0
            
        # Calculate circularity (1.0 for perfect circle)
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        
        # Calculate convexity
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        convexity = area / hull_area if hull_area > 0 else 0
        
        # Combine metrics
        confidence = (circularity + convexity) / 2
        return max(0.0, min(1.0, confidence))
        
    def _update_history(self, detection: Detection) -> None:
        """
        Update detection history
        
        Args:
            detection: New detection to add to history
        """
        self.detection_history.append(detection)
        if len(self.detection_history) > self.history_max_size:
            self.detection_history.pop(0)
            
    def _update_adaptive_params(self, detection: Detection) -> None:
        """
        Update adaptive parameters based on detection success
        
        Args:
            detection: Current detection
        """
        # Update brightness offset based on detection confidence
        if detection.confidence > 0.8:
            self.brightness_offset = max(-50, min(50, self.brightness_offset))
            self.last_good_detection_time = detection.timestamp
        else:
            # Gradually adjust brightness if detections are poor
            time_since_good = time.time() - self.last_good_detection_time
            if time_since_good > 1.0:
                self.brightness_offset += 5.0 if detection.confidence < 0.5 else -5.0
                
    def draw_detection(self, image: np.ndarray, detection: Detection) -> np.ndarray:
        """
        Draw detection results on the image
        
        Args:
            image: Input image
            detection: Detection result
            
        Returns:
            np.ndarray: Image with detection visualization
        """
        output = image.copy()
        
        # Draw bounding box
        x, y, w, h = detection.bounding_box
        cv2.rectangle(
            output,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )
        
        # Draw center point
        cv2.circle(
            output,
            detection.center,
            5,
            (0, 0, 255),
            -1
        )
        
        # Add confidence text
        text = f"Conf: {detection.confidence:.2f}"
        cv2.putText(
            output,
            text,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )
        
        # Add size information
        size_text = f"Size: {detection.size:.0f}px"
        cv2.putText(
            output,
            size_text,
            (x, y - 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )
        
        return output
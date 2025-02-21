"""
Enhanced object detection module with adjusted parameters for more robust sphere detection.
"""
import cv2
import numpy as np
from typing import Optional, Tuple
from entity.detector_config import DetectorConfig

class ObjectDetector:
    """Detects dark spherical objects using contour detection and circle fitting."""
    
    def __init__(self, config: DetectorConfig):
        """Initialize detector with configuration parameters."""
        self.config = config
        self.min_radius = config.min_object_size // 2
        self.max_radius = config.max_object_size // 2
        
        # Detection parameters tuned for dark sphere
        self.threshold_value = 80  # Threshold for dark objects
        self.blur_size = (5, 5)
        self.min_circularity = 0.4  # Lowered from 0.7
        self.max_score = 1.0  # Maximum acceptable score
        
    def detect_object(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect dark spherical objects against light background.
        
        Args:
            frame: Input grayscale image frame
            
        Returns:
            Tuple of (x, y, width, height) of detected sphere or None
        """
        try:
            print(f"Processing frame: {frame.shape}")
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(frame, self.blur_size, 0)
            
            # Simple binary threshold for dark objects
            _, binary = cv2.threshold(
                blurred,
                self.threshold_value,
                255,
                cv2.THRESH_BINARY_INV
            )
            
            # Find contours
            contours, _ = cv2.findContours(
                binary,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            print(f"Found {len(contours)} contours")
            
            best_match = None
            best_score = float('inf')
            
            for contour in contours:
                # Check contour area
                area = cv2.contourArea(contour)
                expected_min_area = np.pi * (self.min_radius ** 2)
                expected_max_area = np.pi * (self.max_radius ** 2)
                
                if area < expected_min_area or area > expected_max_area:
                    continue
                
                # Fit circle
                (x, y), radius = cv2.minEnclosingCircle(contour)
                
                if radius < self.min_radius or radius > self.max_radius:
                    continue
                
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * np.pi * area / (perimeter ** 2)
                
                # Calculate solidity
                hull = cv2.convexHull(contour)
                hull_area = cv2.contourArea(hull)
                solidity = float(area) / hull_area if hull_area > 0 else 0
                
                # Calculate center position weight (prefer objects near image center)
                center_x = frame.shape[1] / 2
                center_y = frame.shape[0] / 2
                dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                max_dist = np.sqrt(center_x**2 + center_y**2)
                position_weight = dist_from_center / max_dist
                
                # Combined score (lower is better)
                score = (
                    (1.0 - circularity) * 0.4 +    # Circularity contribution
                    (1.0 - solidity) * 0.3 +       # Solidity contribution
                    position_weight * 0.3          # Position contribution
                )
                
                print(f"Candidate - Center: ({x:.1f}, {y:.1f}), Radius: {radius:.1f}, "
                      f"Circularity: {circularity:.2f}, Solidity: {solidity:.2f}, "
                      f"Position Weight: {position_weight:.2f}, Score: {score:.2f}")
                
                if score < best_score and circularity > self.min_circularity and score < self.max_score:
                    best_score = score
                    best_match = (x, y, radius)
            
            if best_match:
                x, y, radius = best_match
                print(f"Best match - Center: ({x:.1f}, {y:.1f}), Radius: {radius:.1f}, Score: {best_score:.2f}")
                return (
                    int(x - radius),
                    int(y - radius),
                    int(2 * radius),
                    int(2 * radius)
                )
            
            print("No suitable matches found")
            return None
            
        except Exception as e:
            print(f"Error in detection: {str(e)}")
            return None
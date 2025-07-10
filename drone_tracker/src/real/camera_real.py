"""
Webcam camera interface for capturing frames from laptop's built-in camera.

- Interfaces with OpenCV for capturing camera frames
- Handles image resizing and conversion
- Optimized for tennis ball detection
"""
import cv2
import numpy as np
from typing import Optional

class WebcamCamera:
    def __init__(self, camera_id=0, width=640, height=480):
        """
        Initialize webcam camera interface.
        
        Args:
            camera_id: Camera device ID (0 for built-in webcam)
            width: Target frame width
            height: Target frame height
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        
        print(f"Initializing webcam camera with target resolution: {self.width}x{self.height}")

    def start(self):
        """Start camera capture."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"Failed to open camera with ID {self.camera_id}")
                return False
                
            # Set resolution
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            # Check if resolution was set correctly
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            print(f"Camera initialized with resolution: {actual_width}x{actual_height}")
            
            return True
        except Exception as e:
            print(f"Failed to start camera: {str(e)}")
            return False

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from webcam.
        Returns: RGB numpy array or None if capture fails
        """
        try:
            if self.cap is None or not self.cap.isOpened():
                if not self.start():
                    return None
                    
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                return None

            # Resize if necessary
            if frame.shape[0] != self.height or frame.shape[1] != self.width:
                frame = cv2.resize(frame, (self.width, self.height))
                
            return frame

        except Exception as e:
            print(f"Failed to capture frame: {str(e)}")
            return None

    def release(self):
        """Clean up resources."""
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            print("Camera released")
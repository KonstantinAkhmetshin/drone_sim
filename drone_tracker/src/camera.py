"""
AirSim camera interface for capturing drone camera images.

-Interfaces with AirSim for capturing drone camera frames
-Returns grayscale images for shape-based tracking
-Handles image resizing and conversion
-Optimized for circle/sphere detection
"""
import airsim
import numpy as np
from typing import Optional
import cv2

class AirSimCamera:
    def __init__(self):
        """Initialize AirSim camera interface."""
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        
        # Target resolution - can be reduced for better performance
        self.width = 640
        self.height = 480
        print(f"Initializing camera with target resolution: {self.width}x{self.height}")

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from AirSim drone camera.
        Returns: Grayscale numpy array or None if capture fails
        """
        try:
            # Get image from front camera
            response = self.client.simGetImage("0", airsim.ImageType.Scene)
            if not response:
                print("No image received from AirSim")
                return None

            # Decode the compressed image data directly to grayscale
            img_arr = np.frombuffer(response, np.uint8)
            img_gray = cv2.imdecode(img_arr, cv2.IMREAD_GRAYSCALE)
            
            if img_gray is None:
                print("Failed to decode image data")
                return None

            # Resize if necessary
            if img_gray.shape != (self.height, self.width):
                img_gray = cv2.resize(img_gray, (self.width, self.height))

            return img_gray

        except Exception as e:
            print(f"Failed to capture frame: {str(e)}")
            if 'response' in locals():
                print(f"Raw data size: {len(response)}")
            return None

    def release(self):
        """Clean up resources."""
        pass  # No cleanup needed for AirSim
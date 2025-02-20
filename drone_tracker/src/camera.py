"""
AirSim camera interface for capturing drone camera images.

-Interfaces with AirSim for capturing drone camera frames
-Properly decodes compressed image data
-Handles image resizing and conversion
-Has error handling for failed frame captures
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
        
        # Target resolution
        self.width = 640
        self.height = 480
        print(f"Initializing camera with target resolution: {self.width}x{self.height}")

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from AirSim drone camera.
        Returns: RGB numpy array or None if capture fails
        """
        try:
            # Get RGB image from front camera
            response = self.client.simGetImage("0", airsim.ImageType.Scene)
            if not response:
                print("No image received from AirSim")
                return None

            # Decode the compressed image data
            img_arr = np.frombuffer(response, np.uint8)
            img_bgr = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            
            if img_bgr is None:
                print("Failed to decode image data")
                return None

            # Resize if necessary
            if img_bgr.shape[:2] != (self.height, self.width):
                img_bgr = cv2.resize(img_bgr, (self.width, self.height))

            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            return img_rgb

        except Exception as e:
            print(f"Failed to capture frame: {str(e)}")
            if 'response' in locals():
                print(f"Raw data size: {len(response)}")
            return None

    def release(self):
        """Clean up resources."""
        pass  # No cleanup needed for AirSim
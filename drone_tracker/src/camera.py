"""
AirSim camera interface for capturing drone camera images.

-Interfaces with AirSim for capturing drone camera frames
-Provides 640x480 RGB images
-Has error handling for failed frame captures

"""
import airsim
import numpy as np
from typing import Optional

class AirSimCamera:
    def __init__(self):
        """Initialize AirSim camera interface."""
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a frame from AirSim drone camera.
        Returns: RGB numpy array or None if capture fails
        """
        try:
            # Get RGB image from front camera
            response = self.client.simGetImage("0", airsim.ImageType.Scene)
            if response:
                # Convert string to numpy array
                img1d = np.frombuffer(response, dtype=np.uint8)
                # Reshape array to image format
                img_rgb = img1d.reshape(480, 640, 3)  # AirSim default size
                return img_rgb
            return None
        except Exception as e:
            print(f"Failed to capture frame: {str(e)}")
            return None

    def release(self):
        """Clean up resources."""
        pass  # No cleanup needed for AirSim
"""
Simple object tracking system using AirSim.


-Combines detection and control
-Uses proportional control to keep object centered in frame
-Has configurable parameters for tracking behavior
"""
import cv2
import numpy as np
import time
from typing import Tuple

from camera import AirSimCamera
from controller import AirSimController
from detector import ObjectDetector

class ObjectTracker:
    def __init__(self, target_color: Tuple[int, int, int]):
        """
        Initialize tracking system.
        Args:
            target_color: HSV color to track
        """
        self.camera = AirSimCamera()
        self.controller = AirSimController()
        self.detector = ObjectDetector(target_color)
        
        # Control parameters
        self.max_speed = 2.0  # m/s
        self.frame_width = 640
        self.frame_height = 480
        
    def start(self):
        """Start the tracking system."""
        self.controller.start()
        self.controller.takeoff()
        time.sleep(2)  # Wait for stable takeoff
        
    def update(self):
        """Main tracking update loop."""
        # Get camera frame
        frame = self.camera.capture_frame()
        if frame is None:
            return
            
        # Detect object
        bbox = self.detector.detect_color(frame)
        if bbox is None:
            self.controller.stop()
            return
            
        # Calculate target position
        x, y, w, h = bbox
        center_x = x + w/2
        center_y = y + h/2
        
        # Calculate normalized error (-1 to 1)
        error_x = (center_x - self.frame_width/2) / (self.frame_width/2)
        error_y = (center_y - self.frame_height/2) / (self.frame_height/2)
        
        # Calculate velocities (simple proportional control)
        vx = -error_x * self.max_speed  # Forward/backward
        vy = -error_y * self.max_speed  # Left/right
        vz = 0  # Maintain altitude
        
        # Apply velocity commands
        self.controller.move_by_velocity(vx, vy, vz, 0.1)
        
    def stop(self):
        """Stop tracking and land."""
        self.controller.land()
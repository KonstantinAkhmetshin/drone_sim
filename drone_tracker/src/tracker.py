"""
Simple sphere tracking system using AirSim.
Uses circle detection to track spherical objects and maintain them in frame center.
"""
import cv2
import numpy as np
import time

from camera import AirSimCamera
from controller import AirSimController
from detector import ObjectDetector
from entity.detector_config import DetectorConfig

class ObjectTracker:
    def __init__(self, detector_config: DetectorConfig):
        """
        Initialize tracking system.
        Args:
            detector_config: Configuration for the detector
        """
        self.camera = AirSimCamera()
        self.controller = AirSimController()
        self.detector = ObjectDetector(detector_config)
        
        # Control parameters - reduced for smoother tracking
        self.max_speed = 1.0  # m/s 
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
            
        # Detect sphere
        bbox = self.detector.detect_object(frame)
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
        
        # Calculate velocities with smoother control
        vx = -error_x * self.max_speed
        vy = -error_y * self.max_speed
        vz = 0  # Maintain altitude
        
        # Apply velocity commands with longer duration for smoother movement
        self.controller.move_by_velocity(vx, vy, vz, 0.2)  
        
    def stop(self):
        """Stop tracking and land."""
        self.controller.land()
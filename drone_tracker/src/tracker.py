"""
Enhanced tracking system with stable movement control and yaw correction.
"""
import time
import numpy as np

from camera import AirSimCamera
from controller import AirSimController
from detector import ObjectDetector
from entity.detector_config import DetectorConfig
from typing import Tuple

class ObjectTracker:
    def __init__(self, detector_config: DetectorConfig):
        """Initialize tracking system."""
        self.camera = AirSimCamera()
        self.controller = AirSimController()
        self.detector = ObjectDetector(detector_config)
        
        # Camera parameters
        self.frame_width = 640
        self.frame_height = 480
        self.fov_degrees = 90
        self.fov_radians = np.radians(self.fov_degrees)
        
        # Known sphere parameters
        self.sphere_diameter = 1.0  # meters
        
        # Control parameters - reduced for stability
        self.max_centering_speed = 0.3   # Maximum speed for centering
        self.forward_speed = 1.0         # Forward speed when centered
        self.min_speed = 0.05           # Minimum speed threshold
        self.max_yaw_rate = 2.0        # Maximum yaw rate in degrees/second
        self.yaw_deadzone = 0.02        # Deadzone for yaw corrections (normalized)
        
        # Movement thresholds
        self.centering_threshold_x = 0.5   # Horizontal centering threshold (20%)
        self.centering_threshold_y = 0.5   # Vertical centering threshold (30%)
        self.deadzone = 0.01             # Small deadzone for stability
        
        # Smoothing
        self.smoothing_factor = 0.5      # For velocity smoothing
        self.last_vx = 0
        self.last_vy = 0
        self.last_vz = 0
        
    def estimate_distance(self, bbox_width: float) -> float:
        """Estimate distance to sphere using apparent size."""
        angular_size = bbox_width * self.fov_radians / self.frame_width
        distance = self.sphere_diameter / np.tan(angular_size)
        return float(distance)
        
    def start(self):
        """Start the tracking system."""
        print("Initializing tracking system...")
        self.controller.start()
        self.controller.takeoff()
        time.sleep(2)
        
    def calculate_velocity(self, error: float, axis: str) -> float:
        """Calculate velocity with smooth proportional control."""
        if abs(error) < self.deadzone:
            print(f"{axis} within deadzone ({error:.3f})")
            return 0.0
            
        # Basic proportional control
        velocity = -error * self.max_centering_speed
        
        # Apply limits
        velocity = float(np.clip(velocity, -self.max_centering_speed, self.max_centering_speed))
        
        if abs(velocity) < self.min_speed:
            velocity = 0.0
            
        print(f"{axis} error: {error:.3f}, velocity: {velocity:.3f} m/s")
        return velocity
        
    def smooth_velocity(self, current: float, last: float) -> float:
        """Apply smoothing to velocity commands."""
        return current * (1 - self.smoothing_factor) + last * self.smoothing_factor
        
    def is_centered(self, error_x: float, error_y: float) -> bool:
        """Check if target is well-centered."""
        return (abs(error_x) < self.centering_threshold_x and 
                abs(error_y) < self.centering_threshold_y)
        
    def update(self, bbox: Tuple[int, int, int, int]):
        """Main tracking update loop with stable movement."""
        try:
            if bbox is None:
                # TODO : If the object is lost try to yaw to find it!
                print("No detection - hovering")
                self.controller.stop()
                # Reset smoothing history when target lost
                self.last_vx = 0
                self.last_vy = 0
                self.last_vz = 0
                return
                
            # Calculate target position
            x, y, w, h = bbox
            center_x = x + w/2
            center_y = y + h/2
            
            # Calculate normalized errors (-1 to 1)
            error_x = (center_x - self.frame_width/2) / (self.frame_width/2)
            error_y = (center_y - self.frame_height/2) / (self.frame_height/2)
            
            print(f'error_x : {error_x} error_y {error_y}') 

            # Distance for logging
            distance = self.estimate_distance(w)
            print(f"Distance to sphere: {distance:.2f}m")
            
            if distance < 0.1 and abs(error_x) < 0.05 and abs(error_y) < 0.05:
                print("TARGET APPROACHED!!!")
                self.controller.stop()
                return

            # Calculate yaw correction based on horizontal error
            yaw_rate = 0.0
            if abs(error_x) > self.yaw_deadzone:
                yaw_rate = -error_x * self.max_yaw_rate
                print(f"Applying yaw correction: {yaw_rate:.2f} deg/s")

            
            # Calculate base forward speed based on horizontal centering
            if abs(error_x) < self.centering_threshold_x:
                # If horizontally centered, move forward with full speed
                base_forward = self.forward_speed
            else:
                # Partial forward movement while centering
                base_forward = self.forward_speed * (1 - abs(error_x))  # Slow down if misaligned
                                
            # Combine forward movement with centering adjustment
            vx = vx = max(base_forward, self.min_speed)
            vy = -self.calculate_velocity(error_x, 'X')  # Left/right correction
            vz = -self.calculate_velocity(error_y, 'Z')  # Up/down correction
            
            print(f"Forward speed: {base_forward:.2f}, Total vx: {vx:.2f}")
            
            # Apply smoothing
            vx = self.smooth_velocity(vx, self.last_vx)
            vy = self.smooth_velocity(vy, self.last_vy)
            vz = self.smooth_velocity(vz, self.last_vz)
            
            # Store velocities for next iteration
            self.last_vx = vx
            self.last_vy = vy
            self.last_vz = vz
            
            # Apply velocity commands with yaw correction
            print(f"Commanding velocity: vx={vx:.2f}, vy={vy:.2f}, vz={vz:.2f}, yaw_rate={yaw_rate:.2f}")
            self.controller.move_by_velocity(vx, vy, vz, yaw_rate, 2.0)
            
        except Exception as e:
            print(f"Error in tracking update: {str(e)}")
            self.controller.stop()
        
    def stop(self):
        """Stop tracking and land."""
        print("Landing...")
        self.controller.land()
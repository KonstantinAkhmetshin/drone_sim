"""
Enhanced AirSim drone controller optimized for tracking movement.
"""
import airsim
import numpy as np
from typing import Tuple

class AirSimController:
    def __init__(self):
        """Initialize AirSim controller."""
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        
        # Control parameters
        self.max_tilt_angle = 45.0  # Increased for more aggressive movement
        self.takeoff_height = -2.0   # meters
        self.hover_height = -2.0     # meters
        
    def start(self):
        """Initialize drone for flight."""
        print("Enabling API control...")
        self.client.enableApiControl(True)
        self.client.armDisarm(True)
        
        # Configure vehicle settings for more aggressive movement
        self.client.simSetVehiclePose(
            airsim.Pose(airsim.Vector3r(0, 0, self.takeoff_height)),
            True
        )
        
    def takeoff(self):
        """Take off safely."""
        print("Taking off...")
        self.client.takeoffAsync().join()
        print("Takeoff complete")
        
    def move_by_velocity(self, vx: float, vy: float, vz: float, yaw_rate: float, duration: float):
        """
        Move drone by specified velocity with yaw control.
        
        Args:
            vx, vy, vz: velocity components in m/s
            yaw_rate: angular velocity in degrees/second
            duration: time to maintain velocity in seconds
        """
        # Clean velocity commands
        vx = float(np.clip(vx, -10, 10))
        vy = float(np.clip(vy, -10, 10))
        vz = float(np.clip(vz, -2, 2))
        yaw_rate = float(np.clip(yaw_rate, -45, 45))  # Limit yaw rate to ±45 degrees/sec
        
        try:
            self.client.moveByVelocityAsync(
                vx, vy, vz,
                duration,
                drivetrain=airsim.DrivetrainType.MaxDegreeOfFreedom,
                yaw_mode=airsim.YawMode(True, yaw_rate)
            ).join()
            
        except Exception as e:
            print(f"Movement error: {str(e)}")
            self.stop()
        
    def get_position(self) -> Tuple[float, float, float]:
        """Get current position of the drone."""
        state = self.client.getMultirotorState()
        pos = state.kinematics_estimated.position
        return (pos.x_val, pos.y_val, pos.z_val)
        
    def stop(self):
        """Stop movement smoothly."""
        print("Stopping movement...")
        self.client.hoverAsync().join()
        
    def land(self):
        """Land the drone safely."""
        print("Landing...")
        self.client.landAsync().join()
        self.client.armDisarm(False)
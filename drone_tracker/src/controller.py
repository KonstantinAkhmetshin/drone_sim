"""
AirSim drone controller for basic movement commands.
"""
import airsim
import time
from typing import Tuple

class AirSimController:
    def __init__(self):
        """Initialize AirSim controller."""
        self.client = airsim.MultirotorClient()
        self.client.confirmConnection()
        
    def start(self):
        """Initialize drone for flight."""
        self.client.enableApiControl(True)
        self.client.armDisarm(True)
        
    def takeoff(self):
        """Take off safely."""
        print("Taking off...")
        self.client.takeoffAsync().join()
        
    def move_by_velocity(self, vx: float, vy: float, vz: float, duration: float):
        """
        Move drone by specified velocity.
        Args:
            vx, vy, vz: velocity components in m/s
            duration: time to maintain velocity in seconds
        """
        self.client.moveByVelocityAsync(vx, vy, vz, duration)
        
    def get_position(self) -> Tuple[float, float, float]:
        """Get current position of the drone."""
        state = self.client.getMultirotorState()
        pos = state.kinematics_estimated.position
        return (pos.x_val, pos.y_val, pos.z_val)
        
    def land(self):
        """Land the drone safely."""
        print("Landing...")
        self.client.landAsync().join()
        
    def stop(self):
        """Stop all movement."""
        self.client.hoverAsync().join()
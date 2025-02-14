"""
Main entry point for the drone tracking system.
"""
import airsim
import cv2
import numpy as np
import time
from src.tracker import TrackingSystem
from config.tracker_config import *

def main():
    """Main function to run the drone tracking system."""
    # Initialize AirSim client
    client = airsim.MultirotorClient()
    client.confirmConnection()
    
    # Initialize tracking system
    tracking_system = TrackingSystem(client)
    
    try:
        # Main control loop
        while True:
            tracking_system.update()
            time.sleep(1/30)  # 30 Hz update rate
            
    except KeyboardInterrupt:
        print("Stopping tracking system...")
    finally:
        client.reset()

if __name__ == "__main__":
    main()

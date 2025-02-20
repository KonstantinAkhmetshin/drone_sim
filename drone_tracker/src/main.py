"""
Test script for sphere tracking in AirSim simulation.
This script:
1. Spawns a green sphere in the simulation
2. Initializes the drone tracking system
3. Starts tracking the sphere
"""

import time
import sys
import os
from pathlib import Path

# Add the drone_tracker package to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "drone_tracker"))

from tracker import ObjectTracker
from visualization import TrackingVisualizer
from entity.detector_config import DetectorConfig
import airsim

def spawn_sphere(client):
    """
    Spawn a green sphere in front of the drone.
    
    Args:
        client: AirSim client instance
    Returns:
        bool: True if spawn successful, False otherwise
    """
    try:
        # Spawn sphere 10 meters in front of drone
        scale = airsim.Vector3r(1.0, 1.0, 1.0)  # 1 meter sphere
        pose = airsim.Pose(position_val=airsim.Vector3r(10.0, 0.0, -2.0))
        success = client.simSpawnObject("Sphere", "sphere", pose, scale, True)
        
        if success:
            print("Successfully spawned sphere!")
            return True
        else:
            print("Failed to spawn sphere")
            return False
            
    except Exception as e:
        print(f"Error spawning sphere: {str(e)}")
        return False

def main():
    try:
        # Initialize AirSim client
        client = airsim.MultirotorClient()
        client.confirmConnection()
        
        # Spawn the sphere
        if not spawn_sphere(client):
            print("Failed to spawn sphere, exiting...")
            return
            
        # Initialize tracking system
        config = DetectorConfig(
            min_object_size=20,   # Minimum size in pixels
            max_object_size=200   # Maximum size in pixels
        )
        
        tracker = ObjectTracker(config)
        visualizer = TrackingVisualizer("Sphere Tracking")
        
        print("Starting tracking system...")
        tracker.start()
        time.sleep(2)  # Wait for stable takeoff
        
        print("Tracking sphere... Press Ctrl+C to stop")
        while True:
            # Get camera frame
            frame = tracker.camera.capture_frame()
            if frame is None:
                print("Failed to capture frame, retrying...")
                continue
                
            # Detect and track sphere
            bbox = tracker.detector.detect_object(frame)
            
            # Update visualization
            vis_frame = visualizer.draw_tracking_info(
                frame, 
                bbox,
                {'position': tracker.controller.get_position()}
            )
            visualizer.show(vis_frame)
            
            # Update drone position
            tracker.update()
            
            # Small delay to prevent overwhelming the simulation
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping tracking system...")
    except Exception as e:
        print(f"Error during tracking: {str(e)}")
    finally:
        if 'tracker' in locals():
            tracker.stop()
        if 'visualizer' in locals():
            visualizer.close()

if __name__ == "__main__":
    main()
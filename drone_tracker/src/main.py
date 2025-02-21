"""
Main script for sphere tracking with fixed visualization.
"""
import time
import airsim
from tracker import ObjectTracker
from visualization import TrackingVisualizer
from entity.detector_config import DetectorConfig

def spawn_sphere(client):
    """Spawn a sphere in front of the drone."""
    try:
        scale = airsim.Vector3r(1.0, 1.0, 1.0)
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
            min_object_size=15,
            max_object_size=300
        )
        
        tracker = ObjectTracker(config)
        visualizer = TrackingVisualizer("Sphere Tracking")
        
        print("Starting tracking system...")
        tracker.start()
        
        print("Tracking sphere... Press Ctrl+C to stop")
        while True:
            # Get camera frame
            frame = tracker.camera.capture_frame()
            if frame is None:
                print("Failed to capture frame, retrying...")
                continue
                
            # Detect and track sphere
            bbox = tracker.detector.detect_object(frame)
            
            # Get distance if object detected
            distance = None
            if bbox is not None:
                distance = tracker.estimate_distance(bbox[2])
            
            # Update visualization
            vis_frame = visualizer.draw_tracking_info(
                frame,
                bbox,
                distance=distance
            )
            visualizer.show(vis_frame)
            
            # Update drone position
            tracker.update()
            
            # Small delay
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping tracking system...")
    except Exception as e:
        print(f"Error during tracking: {str(e)}")
    finally:
        if 'tracker' in locals():
            tracker.stop()

if __name__ == "__main__":
    main()
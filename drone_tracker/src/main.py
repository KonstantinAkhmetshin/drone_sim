"""
Main script for sphere tracking with fixed visualization.
"""
import time
import airsim
from tracker import ObjectTracker
from visualization import TrackingVisualizer
from entity.detector_config import DetectorConfig
import cv2


def spawn_sphere(client):
    """Spawn a sphere in front of the drone."""
    try:
        scale = airsim.Vector3r(1.0, 1.0, 1.0)
        pose = airsim.Pose(position_val=airsim.Vector3r(10.0, 0.0, -2.0))
        objectName = client.simSpawnObject("Sphere", "sphere", pose, scale, True)
        
        if objectName:
            print(f"Successfully spawned sphere! {objectName}")
            return (True, objectName)
        else:
            print("Failed to spawn sphere")
            return (False, objectName)
            
    except Exception as e:
        print(f"Error spawning sphere: {str(e)}")
        return False

def main():
    objectName = None
    try:
        # Initialize AirSim client
        client = airsim.MultirotorClient()
        client.confirmConnection()
        
        success, objectName = spawn_sphere(client)

        # Spawn the sphere
        if not success:
            print("Failed to spawn sphere, exiting...")
            return
            
        # Initialize tracking system
        config = DetectorConfig(
            min_object_size=15,
            max_object_size=400
        )
        
        tracker = ObjectTracker(config)
        visualizer = TrackingVisualizer("Sphere Tracking")
        
        print("Starting tracking system...")
        tracker.start()
        
        print("Tracking sphere... Press Ctrl+C to stop")
        processing_step = 1
        while True:

            if processing_step > 12:
                break

            # Get camera frame
            frame = tracker.camera.capture_frame()
            if frame is None:
                print("Failed to capture frame, retrying...")
                continue

            print (f">>>PROCESSING STEP :{processing_step}")    
            # Detect and track sphere
            bbox = tracker.detector.detect_object(frame, processing_step)
            
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
            tracker.update(bbox)
            
            processing_step += 1
            # Small delay
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping tracking system...")
    except Exception as e:
        print(f"Error during tracking: {str(e)}")
    finally:
        print(f"Cleaing up. Object name is {objectName}")
        client.simDestroyObject(objectName)
        client.reset()
        if 'tracker' in locals():
            tracker.stop()
        if 'visualizer' in locals(): 
            visualizer.close()

if __name__ == "__main__":
    main()
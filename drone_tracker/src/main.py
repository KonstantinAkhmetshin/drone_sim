"""
Main script to run the object tracking system.
"""
import time
from tracker import ObjectTracker
from .visualization import TrackingVisualizer

def main():
    # Initialize tracker with target color (green in HSV)
    target_color = (60, 255, 255)  # Green in HSV
    tracker = ObjectTracker(target_color)
    visualizer = TrackingVisualizer()
    try:
        # Start tracking
        print("Starting tracking system...")
        tracker.start()
        
        # Main loop
        print("Tracking... Press Ctrl+C to stop")
        while True:
            frame = tracker.camera.capture_frame()
            bbox = tracker.detector.detect_color(frame)
            vis_frame = visualizer.draw_tracking_info(frame, bbox)
            visualizer.show(vis_frame)
            tracker.update()
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping tracking system...")
    finally:
        tracker.stop()
        visualizer.close()

if __name__ == "__main__":
    main()
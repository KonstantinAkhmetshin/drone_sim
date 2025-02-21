"""
Enhanced visualization module with fixed status display.
"""
import cv2
import numpy as np
from typing import Optional, Tuple

class TrackingVisualizer:
    def __init__(self, window_name: str = "Drone Tracking"):
        """Initialize visualizer."""
        self.window_name = window_name
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
    def draw_tracking_info(self, frame: np.ndarray, 
                         bbox: Optional[Tuple[int, int, int, int]] = None,
                         distance: Optional[float] = None) -> np.ndarray:
        """
        Draw tracking visualization with status information.
        
        Args:
            frame: Input grayscale camera frame
            bbox: Detected object bounding box (x,y,w,h)
            distance: Estimated distance to object
            
        Returns:
            Frame with visualization overlays
        """
        # Convert grayscale to BGR for colored visualization
        vis_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        h, w = frame.shape[:2]
        
        # Draw detection box and tracking info
        if bbox is not None:
            x, y, w_box, h_box = bbox
            # Bounding box
            cv2.rectangle(vis_frame, (x,y), (x+w_box,y+h_box), (0,255,0), 2)
            
            # Center point and crosshair
            center_x = x + w_box//2
            center_y = y + h_box//2
            cv2.circle(vis_frame, (center_x, center_y), 2, (0,0,255), 3)
            
            # Draw lines to center
            frame_center_x = w // 2
            frame_center_y = h // 2
            cv2.line(vis_frame, 
                    (frame_center_x, frame_center_y),
                    (center_x, center_y),
                    (255,0,0), 1)
            
            # Display distance information
            if distance is not None:
                # Distance value
                cv2.putText(vis_frame,
                           f"Distance: {distance:.2f}m",
                           (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX,
                           0.7,
                           (0,255,0),
                           2)
                
                # Approach status
                if distance > 1.0:
                    status = "APPROACHING"
                    color = (0,255,0)
                else:
                    status = "MIN DISTANCE"
                    color = (0,0,255)
                    
                cv2.putText(vis_frame,
                           status,
                           (w-200, 30),
                           cv2.FONT_HERSHEY_SIMPLEX,
                           0.7,
                           color,
                           2)
        
        # Draw frame center crosshairs
        cv2.line(vis_frame, (w//2,0), (w//2,h), (255,0,0), 1)
        cv2.line(vis_frame, (0,h//2), (w,h//2), (255,0,0), 1)
        
        return vis_frame
        
    def show(self, frame: np.ndarray):
        """Display the frame."""
        cv2.imshow(self.window_name, frame)
        cv2.waitKey(1)
        
    def close(self):
        """Clean up resources."""
        cv2.destroyAllWindows()
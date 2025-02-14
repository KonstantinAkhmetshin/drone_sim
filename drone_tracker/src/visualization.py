"""
Visualization module for debugging drone tracking.
Displays camera feed with tracking overlay and drone state information.

-Provides real-time visual feedback
-Shows tracking boxes, crosshairs, and drone state
-Useful for debugging and monitoring
"""
import cv2
import numpy as np
from typing import Optional, Tuple

class TrackingVisualizer:
    def __init__(self, window_name: str = "Drone Tracking"):
        """Initialize visualizer with window name."""
        self.window_name = window_name
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
    def draw_tracking_info(self, frame: np.ndarray, 
                         bbox: Optional[Tuple[int, int, int, int]] = None,
                         drone_state: Optional[dict] = None) -> np.ndarray:
        """
        Draw tracking visualization overlays on frame.
        
        Args:
            frame: Input camera frame
            bbox: Detected object bounding box (x,y,w,h)
            drone_state: Dictionary containing drone telemetry
            
        Returns:
            Frame with visualization overlays
        """
        vis_frame = frame.copy()
        
        # Draw detection box
        if bbox is not None:
            x, y, w, h = bbox
            cv2.rectangle(vis_frame, (x,y), (x+w,y+h), (0,255,0), 2)
            
            # Draw center crosshair
            center_x = x + w//2
            center_y = y + h//2
            cv2.drawMarker(vis_frame, (center_x, center_y), 
                          (0,255,0), cv2.MARKER_CROSS, 20, 2)
                          
        # Draw frame centerline
        h, w = frame.shape[:2]
        cv2.line(vis_frame, (w//2,0), (w//2,h), (255,0,0), 1)
        cv2.line(vis_frame, (0,h//2), (w,h//2), (255,0,0), 1)
        
        # Draw drone state
        if drone_state:
            text = []
            if 'velocity' in drone_state:
                vx, vy, vz = drone_state['velocity']
                text.append(f"Vel: ({vx:.1f}, {vy:.1f}, {vz:.1f})")
            if 'position' in drone_state:    
                px, py, pz = drone_state['position']
                text.append(f"Pos: ({px:.1f}, {py:.1f}, {pz:.1f})")
                
            for i, t in enumerate(text):
                cv2.putText(vis_frame, t, (10, 30+30*i), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                           
        return vis_frame
        
    def show(self, frame: np.ndarray):
        """Display the frame."""
        cv2.imshow(self.window_name, frame)
        cv2.waitKey(1)
        
    def close(self):
        """Clean up resources."""
        cv2.destroyAllWindows()
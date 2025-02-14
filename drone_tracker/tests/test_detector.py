"""
Test suite for drone tracking system components.
"""
import unittest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch
import os
import sys

# Add the src directory to the Python path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, src_path)

sys.modules['airsim'] = MagicMock()

# Now import the modules
from detector import ObjectDetector
from tracker import ObjectTracker
from camera import AirSimCamera
from entity.detector_config import DetectorConfig


class TestObjectDetector(unittest.TestCase):
    def setUp(self):
        """Set up test detector."""
        self.config = {
            "target_color": (60, 255, 255),  # Green in HSV
            "color_tolerance": 30,  # Increased tolerance
            "min_object_size": 100,
            "max_object_size": 100000  # Increased max size
        }
        self.detector = ObjectDetector(self.config)
        
    def test_color_detection(self):
        print("""Test color-based object detection.""")
        # Create test image with green rectangle in BGR
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(img, (100,100), (200,200), (0,255,0), -1)  # BGR green
        
        # Convert to HSV (which is what the detector expects)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Save debug image
        cv2.imwrite('debug_input.png', cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR))
        
        # Detect object
        bbox = self.detector.detect_color(img_hsv)
        
        # Verify detection
        self.assertIsNotNone(bbox, "Detection failed - no bounding box returned")
        if bbox is not None:  # Additional debug info if test fails
            x, y, w, h = bbox
            print(f"Detected bbox: x={x}, y={y}, w={w}, h={h}")
            self.assertTrue(90 <= x <= 110, f"X coordinate {x} outside expected range")
            self.assertTrue(90 <= y <= 110, f"Y coordinate {y} outside expected range")
            self.assertTrue(90 <= w <= 110, f"Width {w} outside expected range")
            self.assertTrue(90 <= h <= 110, f"Height {h} outside expected range")
        print("passed")    

    def test_no_detection_empty_frame(self):
        print(""""Test detection with empty frame.""")
        # Create black frame
        img_black = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Should return None for frame with no green
        bbox = self.detector.detect_color(img_black)
        self.assertIsNone(bbox, "Should not detect anything in black frame")    
        print("passed")    


class TestObjectTracker(unittest.TestCase):
    @patch('airsim.MultirotorClient')
    def setUp(self, mock_client):
        """Set up test tracker with mocked dependencies."""
        self.tracker = ObjectTracker(DetectorConfig(
                                            target_color=(60, 255, 255), # Green in HSV
                                            color_tolerance=30,
                                            min_object_size=50,
                                            max_object_size=5000))
        self.tracker.camera = MagicMock()
        self.tracker.controller = MagicMock()

    def test_tracker_initialization(self):
        print("""Test tracker initialization.""")
        self.assertEqual(self.tracker.max_speed, 2.0, "Incorrect max speed")
        self.assertEqual(self.tracker.frame_width, 640, "Incorrect frame width")
        self.assertEqual(self.tracker.frame_height, 480, "Incorrect frame height")
        print("passed")

    def test_tracking_update_with_target(self):
        print("""Test tracking update with visible target.""")
        # Create frame with target
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(test_frame, (320,240), (370,290), (0,255,0), -1)
        test_frame_hsv = cv2.cvtColor(test_frame, cv2.COLOR_BGR2HSV)
        
        # Setup mock
        self.tracker.camera.capture_frame.return_value = test_frame_hsv
        
        # Run update
        self.tracker.update()
        
        # Verify drone movement was commanded
        self.tracker.controller.move_by_velocity.assert_called_once()
        self.tracker.controller.stop.assert_not_called()
        print("passed")

    def test_tracking_update_no_target(self):
        print("""Test tracking update with no visible target.""")
        # Create empty frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Setup mock
        self.tracker.camera.capture_frame.return_value = test_frame
        
        # Run update
        self.tracker.update()
        
        # Verify drone stops when no target found
        self.tracker.controller.stop.assert_called_once()
        self.tracker.controller.move_by_velocity.assert_not_called()
        print("passed")

class TestCamera(unittest.TestCase):
    @patch('airsim.MultirotorClient')
    def setUp(self, mock_client):
        """Set up test camera with mocked AirSim client."""
        self.camera = AirSimCamera()
        self.mock_client = mock_client.return_value

    def test_camera_capture_failure(self):
        """Test camera behavior when capture fails."""
        # Setup mock to return None
        self.mock_client.simGetImage.return_value = None
        
        # Should handle failed capture gracefully
        frame = self.camera.capture_frame()
        self.assertIsNone(frame, "Should return None when capture fails")

if __name__ == '__main__':
    unittest.main()
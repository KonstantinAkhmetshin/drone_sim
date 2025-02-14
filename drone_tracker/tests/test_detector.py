"""
Test suite for drone tracking system components.
"""
import unittest
import numpy as np
import cv2
from unittest.mock import MagicMock, patch

from drone_tracker.src.detector import ObjectDetector
from drone_tracker.src.tracker import ObjectTracker

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
        """Test color-based object detection."""
        # Create test image with green rectangle in BGR
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(img, (100,100), (200,200), (0,255,0), -1)  # BGR green
        
        # Convert to HSV (which is what the detector expects)
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Detect object
        bbox = self.detector.detect_color(img_hsv)
        
        # Verify detection
        self.assertIsNotNone(bbox, "Detection failed - no bounding box returned")
        if bbox is not None:  # Additional debug info if test fails
            x, y, w, h = bbox
            self.assertTrue(90 <= x <= 110, f"X coordinate {x} outside expected range")
            self.assertTrue(90 <= y <= 110, f"Y coordinate {y} outside expected range")
            self.assertTrue(90 <= w <= 110, f"Width {w} outside expected range")
            self.assertTrue(90 <= h <= 110, f"Height {h} outside expected range")

@patch('airsim.MultirotorClient')
class TestObjectTracker(unittest.TestCase):
    def setUp(self):
        """Set up test tracker with mocked components."""
        # Mock AirSim client
        self.mock_client = MagicMock()
        with patch('airsim.MultirotorClient', return_value=self.mock_client):
            self.tracker = ObjectTracker((60, 255, 255))
        
        # Mock camera and controller explicitly
        self.tracker.camera = MagicMock()
        self.tracker.controller = MagicMock()
        
    def test_tracking_update(self, mock_airsim):
        """Test tracking update loop."""
        # Create test frame with a green rectangle
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(test_frame, (320,240), (370,290), (0,255,0), -1)
        
        # Convert to HSV
        test_frame_hsv = cv2.cvtColor(test_frame, cv2.COLOR_BGR2HSV)
        
        # Mock camera to return our test frame
        self.tracker.camera.capture_frame.return_value = test_frame_hsv
        
        # Run update
        self.tracker.update()
        
        # Verify drone commands were called
        self.tracker.controller.move_by_velocity.assert_called_once()
        
    def test_no_target(self, mock_airsim):
        """Test behavior when no target is visible."""
        # Mock empty frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.tracker.camera.capture_frame.return_value = test_frame
        
        # Run update
        self.tracker.update()
        
        # Verify drone stops when no target is found
        self.tracker.controller.stop.assert_called_once()

if __name__ == '__main__':
    unittest.main()
#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool
from cv_bridge import CvBridge
import numpy as np
import cv2
from typing import Optional, Tuple

from .object_detector import ObjectDetector, DetectionConfig
from .control_manager import ControlManager

class TrackerNode(Node):
    """
    Main node for coordinating object detection and drone control.
    Processes camera feed and manages tracking behavior.
    """
    
    def __init__(self):
        super().__init__('tracker_node')
        
        # Initialize CV bridge
        self.bridge = CvBridge()
        
        # Initialize object detector with configuration from parameters
        self.declare_parameters(
            namespace='',
            parameters=[
                ('target_color', [0, 255, 0]),  # Default: gREEN
                ('color_tolerance', 20),
                ('min_object_size', 100),
                ('max_object_size', 100000),
                ('detection_threshold', 0.7),
                ('enable_visualization', True)
            ]
        )
        
        # Create detector configuration
        detector_config = DetectionConfig(
            target_color=tuple(self.get_parameter('target_color').value),
            color_tolerance=self.get_parameter('color_tolerance').value,
            min_object_size=self.get_parameter('min_object_size').value,
            max_object_size=self.get_parameter('max_object_size').value,
            detection_threshold=self.get_parameter('detection_threshold').value
        )
        
        self.detector = ObjectDetector(detector_config)
        
        # Initialize control manager
        self.control_manager = ControlManager()
        
        # Create subscribers
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',  # From simulation camera
            self.image_callback,
            10
        )
        
        # Create publishers
        self.target_pose_pub = self.create_publisher(
            PoseStamped,
            '/drone0/target_pose',
            10
        )
        
        self.debug_image_pub = self.create_publisher(
            Image,
            '/tracker/debug_image',
            10
        )
        
        # Initialize tracking state
        self.tracking_active = False
        self.last_detection_time = self.get_clock().now()
        self.lost_target_timeout = 1.0  # seconds
        
        # Camera parameters (from simulation)
        self.camera_fov = 1.0472  # 60 degrees in radians
        self.camera_width = 640
        self.camera_height = 480
        
        self.get_logger().info('Tracker node initialized')
        
    def image_callback(self, msg: Image) -> None:
        """
        Process incoming camera images
        
        Args:
            msg: ROS Image message
        """
        try:
            # Convert ROS Image message to OpenCV image
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            
            # Detect object in the image
            detection = self.detector.detect(cv_image)  # Returns single Detection object
            
            if detection:
                # Update tracking state
                self.tracking_active = True
                self.last_detection_time = self.get_clock().now()
                
                # Calculate 3D position from detection
                target_pose = self.calculate_target_pose(detection)
                
                # Publish target pose
                if target_pose is not None:
                    self.target_pose_pub.publish(target_pose)
                    
                # Enable tracking in control manager
                self.control_manager.enable_tracking(True)
                
            else:
                # Check if we've lost the target
                time_since_detection = (self.get_clock().now() - self.last_detection_time).nanoseconds / 1e9
                                    
                if time_since_detection > self.lost_target_timeout:
                    self.tracking_active = False
                    self.control_manager.enable_tracking(False)
            
            # Create and publish debug visualization
            if self.get_parameter('enable_visualization').value:
                debug_image = self.create_debug_visualization(cv_image, detection)
                debug_msg = self.bridge.cv2_to_imgmsg(debug_image, "bgr8")
                self.debug_image_pub.publish(debug_msg)
                
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')


    def calculate_target_pose(self, detection) -> Optional[PoseStamped]:
        """
        Calculate 3D pose from detection
        
        Args:
            detection: Detection object from detector
            
        Returns:
            Optional[PoseStamped]: Target pose or None if calculation fails
        """
        try:
            # Get image center coordinates
            center_x = self.camera_width / 2
            center_y = self.camera_height / 2
            
            # Calculate angular offsets
            x_offset = ((detection.center[0] - center_x) / 
                       self.camera_width * self.camera_fov)
            y_offset = ((detection.center[1] - center_y) / 
                       self.camera_height * self.camera_fov)
            
            # Estimate distance based on object size
            # This is a simple estimation - you might want to improve this
            nominal_size = 100000  # Expected size at 1 meter
            distance = np.sqrt(nominal_size / detection.size)
            
            # Calculate 3D position
            x = distance * np.cos(y_offset) * np.sin(x_offset)
            y = distance * np.cos(y_offset) * np.cos(x_offset)
            z = distance * np.sin(y_offset)
            
            # Create pose message
            pose_msg = PoseStamped()
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            pose_msg.header.frame_id = 'camera_frame'
            
            pose_msg.pose.position.x = float(x)
            pose_msg.pose.position.y = float(y)
            pose_msg.pose.position.z = float(z)
            
            # Set orientation to identity quaternion
            pose_msg.pose.orientation.w = 1.0
            
            return pose_msg
            
        except Exception as e:
            self.get_logger().error(f'Error calculating target pose: {e}')
            return None
            
    def create_debug_visualization(self, image, detection):
        """
        Create debug visualization image
        
        Args:
            image: Original image
            detection: Single detection object or None
            
        Returns:
            Image with debug visualization
        """
        debug_image = image.copy()
        
        # Draw detection
        if detection:
            debug_image = self.detector.draw_detection(debug_image, detection)
            
        # Add tracking status
        status_text = "Tracking: Active" if self.tracking_active else "Tracking: Lost"
        cv2.putText(debug_image, status_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
        return debug_image
        
def main(args=None):
    rclpy.init(args=args)
    tracker = TrackerNode()
    
    try:
        rclpy.spin(tracker)
    except KeyboardInterrupt:
        pass
    finally:
        tracker.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
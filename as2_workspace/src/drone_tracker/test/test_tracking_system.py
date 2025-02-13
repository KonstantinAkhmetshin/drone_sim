#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge
import cv2
import numpy as np
import time
from typing import Optional, List, Dict
import matplotlib.pyplot as plt

class TrackingSystemTester(Node):
    """
    Test node for verifying drone tracking system functionality.
    Tests individual components and full system integration.
    """
    
    def __init__(self):
        super().__init__('tracking_system_tester')
        
        # Initialize CV bridge
        self.bridge = CvBridge()
        
        # Test status
        self.tests_status = {
            'detector': False,
            'control': False,
            'tracking': False
        }
        
        # Data collection for analysis
        self.tracking_data = {
            'target_positions': [],
            'drone_positions': [],
            'tracking_errors': [],
            'timestamps': []
        }
        
        # Subscribe to relevant topics
        self.image_sub = self.create_subscription(
            Image,
            '/tracker/debug_image',
            self.debug_image_callback,
            10
        )
        
        self.target_pose_sub = self.create_subscription(
            PoseStamped,
            '/drone0/target_pose',
            self.target_pose_callback,
            10
        )
        
        self.drone_pose_sub = self.create_subscription(
            Odometry,
            '/drone0/odom',
            self.drone_pose_callback,
            10
        )
        
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/drone0/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        
        # Publishers for test inputs
        self.test_image_pub = self.create_publisher(
            Image,
            '/camera/image_raw',
            10
        )
        
        # Initialize test parameters
        self.start_time = time.time()
        self.test_duration = 30.0  # seconds
        self.detection_count = 0
        self.control_commands_count = 0
        
        # Create test timer
        self.test_timer = self.create_timer(1.0, self.test_status_callback)
        
        self.get_logger().info('Tracking System Tester initialized')
        
    def generate_test_image(self, target_pos: tuple) -> np.ndarray:
        """
        Generate test image with target object
        
        Args:
            target_pos: (x, y) position of target in image
            
        Returns:
            np.ndarray: Test image
        """
        # Create blank image
        image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Draw red circle as target
        cv2.circle(image, target_pos, 20, (0, 0, 255), -1)
        
        return image
        
    def test_detector(self) -> bool:
        """
        Test object detector functionality
        
        Returns:
            bool: True if test passed
        """
        self.get_logger().info('Testing object detector...')
        
        # Generate test images with target at different positions
        test_positions = [
            (320, 240),  # Center
            (100, 100),  # Top-left
            (540, 380),  # Bottom-right
            (320, 100),  # Top
            (320, 380)   # Bottom
        ]
        
        detected_count = 0
        for pos in test_positions:
            # Generate and publish test image
            test_image = self.generate_test_image(pos)
            msg = self.bridge.cv2_to_imgmsg(test_image, "bgr8")
            self.test_image_pub.publish(msg)
            
            # Wait for detection
            time.sleep(0.5)
            
            if self.detection_count > 0:
                detected_count += 1
                self.detection_count = 0
        
        detection_success = detected_count >= len(test_positions) * 0.8
        self.get_logger().info(f'Detector test {"passed" if detection_success else "failed"}')
        return detection_success
        
    def test_control_response(self) -> bool:
        """
        Test control system response
        
        Returns:
            bool: True if test passed
        """
        self.get_logger().info('Testing control response...')
        
        # Generate test target positions
        test_positions = [
            (0.0, 0.0, 2.0),    # Directly above
            (1.0, 0.0, 2.0),    # Forward
            (0.0, 1.0, 2.0),    # Right
            (-1.0, 0.0, 2.0),   # Back
            (0.0, -1.0, 2.0)    # Left
        ]
        
        response_count = 0
        for pos in test_positions:
            # Create and publish target pose
            pose_msg = PoseStamped()
            pose_msg.header.stamp = self.get_clock().now().to_msg()
            pose_msg.header.frame_id = 'camera_frame'
            pose_msg.pose.position.x = pos[0]
            pose_msg.pose.position.y = pos[1]
            pose_msg.pose.position.z = pos[2]
            pose_msg.pose.orientation.w = 1.0
            
            # Reset control command counter
            self.control_commands_count = 0
            
            # Wait for control response
            time.sleep(0.5)
            
            if self.control_commands_count > 0:
                response_count += 1
        
        control_success = response_count >= len(test_positions) * 0.8
        self.get_logger().info(f'Control test {"passed" if control_success else "failed"}')
        return control_success
        
    def test_full_tracking(self) -> bool:
        """
        Test full tracking system integration
        
        Returns:
            bool: True if test passed
        """
        self.get_logger().info('Testing full tracking system...')
        
        # Clear previous data
        self.tracking_data = {
            'target_positions': [],
            'drone_positions': [],
            'tracking_errors': [],
            'timestamps': []
        }
        
        # Run circular motion test
        test_start_time = time.time()
        while time.time() - test_start_time < self.test_duration:
            # Generate circular target motion
            t = time.time() - test_start_time
            x = 2.0 * np.cos(t * 0.2)
            y = 2.0 * np.sin(t * 0.2)
            z = 2.0
            
            # Create target at position
            image = self.generate_test_image(
                (int(320 + x * 100), int(240 + y * 100))
            )
            msg = self.bridge.cv2_to_imgmsg(image, "bgr8")
            self.test_image_pub.publish(msg)
            
            time.sleep(0.03)  # ~30 Hz
            
        # Analyze tracking performance
        if len(self.tracking_data['tracking_errors']) > 0:
            mean_error = np.mean(self.tracking_data['tracking_errors'])
            max_error = np.max(self.tracking_data['tracking_errors'])
            
            tracking_success = mean_error < 1.0 and max_error < 2.0
            self.get_logger().info(f'Mean tracking error: {mean_error:.2f}m')
            self.get_logger().info(f'Max tracking error: {max_error:.2f}m')
            self.get_logger().info(f'Tracking test {"passed" if tracking_success else "failed"}')
            
            # Generate performance plots
            self.plot_tracking_performance()
            
            return tracking_success
        
        return False
        
    def plot_tracking_performance(self) -> None:
        """Generate plots of tracking performance"""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
            
            # Plot positions
            times = np.array(self.tracking_data['timestamps']) - self.tracking_data['timestamps'][0]
            target_pos = np.array(self.tracking_data['target_positions'])
            drone_pos = np.array(self.tracking_data['drone_positions'])
            
            ax1.plot(times, target_pos[:, 0], 'r-', label='Target X')
            ax1.plot(times, target_pos[:, 1], 'g-', label='Target Y')
            ax1.plot(times, drone_pos[:, 0], 'r--', label='Drone X')
            ax1.plot(times, drone_pos[:, 1], 'g--', label='Drone Y')
            ax1.set_xlabel('Time (s)')
            ax1.set_ylabel('Position (m)')
            ax1.legend()
            ax1.grid(True)
            ax1.set_title('Position Tracking')
            
            # Plot tracking error
            errors = np.array(self.tracking_data['tracking_errors'])
            ax2.plot(times, errors, 'b-', label='Tracking Error')
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Error (m)')
            ax2.legend()
            ax2.grid(True)
            ax2.set_title('Tracking Error')
            
            plt.tight_layout()
            plt.savefig('tracking_performance.png')
            plt.close()
            
        except Exception as e:
            self.get_logger().error(f'Error generating plots: {e}')
        
    def debug_image_callback(self, msg: Image) -> None:
        """Handle debug image messages"""
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            self.detection_count += 1
        except Exception as e:
            self.get_logger().error(f'Error processing debug image: {e}')
            
    def target_pose_callback(self, msg: PoseStamped) -> None:
        """Handle target pose messages"""
        pos = np.array([
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z
        ])
        self.tracking_data['target_positions'].append(pos)
        self.tracking_data['timestamps'].append(time.time())
        
    def drone_pose_callback(self, msg: Odometry) -> None:
        """Handle drone pose messages"""
        pos = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z
        ])
        self.tracking_data['drone_positions'].append(pos)
        
        # Calculate tracking error if we have target position
        if len(self.tracking_data['target_positions']) > 0:
            target_pos = self.tracking_data['target_positions'][-1]
            error = np.linalg.norm(pos - target_pos)
            self.tracking_data['tracking_errors'].append(error)
        
    def cmd_vel_callback(self, msg: Twist) -> None:
        """Handle velocity command messages"""
        self.control_commands_count += 1
        
    def test_status_callback(self) -> None:
        """Periodic test status update"""
        elapsed_time = time.time() - self.start_time
        
        if not self.tests_status['detector'] and elapsed_time > 1.0:
            self.tests_status['detector'] = self.test_detector()
            
        elif not self.tests_status['control'] and elapsed_time > 5.0:
            self.tests_status['control'] = self.test_control_response()
            
        elif not self.tests_status['tracking'] and elapsed_time > 10.0:
            self.tests_status['tracking'] = self.test_full_tracking()
            
        # Check if all tests are complete
        if all(self.tests_status.values()):
            self.get_logger().info('All tests completed!')
            self.test_timer.cancel()

def main(args=None):
    rclpy.init(args=args)
    tester = TrackingSystemTester()
    
    try:
        rclpy.spin(tester)
    except KeyboardInterrupt:
        pass
    finally:
        tester.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
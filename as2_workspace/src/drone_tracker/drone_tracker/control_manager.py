#!/usr/bin/env python3

import numpy as np
from typing import Optional, Dict
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool
import time

class ControlManager(Node):
    """
    Manages drone control and movement based on tracking data.
    Simulation version using ROS2 and Gazebo.
    """
    
    def __init__(self):
        super().__init__('control_manager')
        
        # Control parameters from configuration
        self.declare_parameters(
            namespace='',
            parameters=[
                ('max_velocity', 2.0),
                ('max_acceleration', 1.0),
                ('max_yaw_rate', 45.0),
                ('tracking_distance', 3.0),
                ('min_altitude', 2.0),
                ('max_altitude', 10.0),
                ('position_tolerance', 0.3),
                ('yaw_tolerance', 5.0),
                ('pid_gains_pos_x', 0.5),
                ('pid_gains_pos_y', 0.5),
                ('pid_gains_pos_z', 0.5),
                ('pid_gains_yaw', 2.0)
            ]
        )
        
        # Load parameters with proper error handling
        try:
            self.control_params = self._load_parameters()
        except Exception as e:
            self.get_logger().error(f'Failed to load parameters: {e}')
            raise
        
        # Initialize control states with proper typing
        self.last_target_pose: Optional[PoseStamped] = None
        self.current_pose: Optional[PoseStamped] = None
        self.last_control_time: float = time.time()
        self.is_tracking_active: bool = False
        
        # Initialize PID control errors
        self.last_position_error = np.zeros(3)
        self.integral_position_error = np.zeros(3)
        
        # ROS2 Publishers with QoS profiles
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            'cmd_vel',
            10  # QoS depth
        )
        
        self.status_pub = self.create_publisher(
            Bool,
            'tracking_status',
            10
        )
        
        # ROS2 Subscribers with QoS profiles
        self.target_sub = self.create_subscription(
            PoseStamped,
            'target_pose',
            self.target_callback,
            10
        )
        
        self.odom_sub = self.create_subscription(
            Odometry,
            'odom',
            self.odom_callback,
            10
        )
        
        # Control loop timer with error handling
        try:
            self.timer = self.create_timer(
                1.0/30.0,  # 30 Hz
                self.control_loop
            )
        except Exception as e:
            self.get_logger().error(f'Failed to create control timer: {e}')
            raise
        
        self.get_logger().info('Control Manager initialized successfully')
        
    def _load_parameters(self) -> Dict:
        """Load and validate all parameters"""
        params = {
            'max_velocity': self.get_parameter('max_velocity').value,
            'max_acceleration': self.get_parameter('max_acceleration').value,
            'max_yaw_rate': self.get_parameter('max_yaw_rate').value,
            'tracking_distance': self.get_parameter('tracking_distance').value,
            'min_altitude': self.get_parameter('min_altitude').value,
            'max_altitude': self.get_parameter('max_altitude').value,
            'position_tolerance': self.get_parameter('position_tolerance').value,
            'yaw_tolerance': self.get_parameter('yaw_tolerance').value,
            'pid_gains': {
                'pos_x': self.get_parameter('pid_gains_pos_x').value,
                'pos_y': self.get_parameter('pid_gains_pos_y').value,
                'pos_z': self.get_parameter('pid_gains_pos_z').value,
                'yaw': self.get_parameter('pid_gains_yaw').value
            }
        }
        
        # Validate parameters
        if params['max_velocity'] <= 0:
            raise ValueError('max_velocity must be positive')
        if params['max_acceleration'] <= 0:
            raise ValueError('max_acceleration must be positive')
            
        return params
        
    def target_callback(self, msg: PoseStamped):
        """Handle target pose updates with proper frame transformation"""
        try:
            # Transform target pose to drone's frame
            drone_frame = f'{self.namespace}/base_link'
            if msg.header.frame_id != drone_frame:
                transform = self.tf_buffer.lookup_transform(
                    drone_frame,
                    msg.header.frame_id,
                    rclpy.time.Time())
                msg = tf2_geometry_msgs.do_transform_pose(msg, transform)
            self.last_target_pose = msg
        except Exception as e:
            self.get_logger().error(f'Transform failed: {e}')
        
    def odom_callback(self, msg: Odometry) -> None:
        """
        Handle odometry updates
        Args:
            msg: Odometry message
        """
        self.current_pose = msg.pose.pose
        
    def enable_tracking(self, enable: bool) -> None:
        """
        Enable or disable tracking mode
        Args:
            enable: True to enable tracking, False to disable
        """
        if enable != self.is_tracking_active:
            self.is_tracking_active = enable
            self.get_logger().info(f"Tracking {'enabled' if enable else 'disabled'}")
            
            if not enable:
                # Reset control states when disabling
                self.last_target_pose = None
                self.integral_position_error = np.zeros(3)
                self.last_position_error = np.zeros(3)
                self.send_zero_velocity()
                
    def send_zero_velocity(self) -> None:
        """Send zero velocity command with proper handling"""
        try:
            cmd = Twist()
            self.cmd_vel_pub.publish(cmd)
        except Exception as e:
            self.get_logger().error(f'Failed to publish zero velocity: {e}')
            
    def calculate_control_commands(self) -> Optional[Twist]:
        """
        Calculate control commands based on current state using PID control
        Returns:
            Optional[Twist]: Control commands or None if calculation fails
        """
        if not self.last_target_pose or not self.current_pose:
            return None
            
        try:
            # Calculate time delta
            current_time = time.time()
            dt = current_time - self.last_control_time
            self.last_control_time = current_time
            
            # Extract positions
            target_pos = np.array([
                self.last_target_pose.pose.position.x,
                self.last_target_pose.pose.position.y,
                self.last_target_pose.pose.position.z
            ])
            
            current_pos = np.array([
                self.current_pose.position.x,
                self.current_pose.position.y,
                self.current_pose.position.z
            ])
            
            # Calculate position error
            pos_error = target_pos - current_pos
            
            # Update integral and derivative terms
            self.integral_position_error += pos_error * dt
            derivative_error = (pos_error - self.last_position_error) / dt if dt > 0 else 0
            self.last_position_error = pos_error
            
            # Calculate PID control output
            pid_output = (
                pos_error * self.control_params['pid_gains']['pos_x'] +
                self.integral_position_error * 0.1 +  # Small integral gain
                derivative_error * 0.1  # Small derivative gain
            )
            
            # Apply velocity limits
            speed = np.linalg.norm(pid_output)
            if speed > self.control_params['max_velocity']:
                pid_output = pid_output * self.control_params['max_velocity'] / speed
                
            # Create velocity command
            cmd = Twist()
            cmd.linear.x = float(pid_output[0])
            cmd.linear.y = float(pid_output[1])
            cmd.linear.z = float(pid_output[2])
            
            # Calculate yaw to face target
            target_yaw = np.arctan2(pos_error[1], pos_error[0])
            current_yaw = self.get_yaw_from_quaternion(
                self.current_pose.orientation.x,
                self.current_pose.orientation.y,
                self.current_pose.orientation.z,
                self.current_pose.orientation.w
            )
            
            # Normalize yaw error to [-pi, pi]
            yaw_error = np.arctan2(np.sin(target_yaw - current_yaw), 
                                 np.cos(target_yaw - current_yaw))
            
            # Apply yaw rate limit
            yaw_rate = np.clip(
                yaw_error * self.control_params['pid_gains']['yaw'],
                -np.radians(self.control_params['max_yaw_rate']),
                np.radians(self.control_params['max_yaw_rate'])
            )
            
            cmd.angular.z = float(yaw_rate)
            
            return cmd
            
        except Exception as e:
            self.get_logger().error(f'Error in control calculation: {e}')
            return None
            
    def get_yaw_from_quaternion(self, x: float, y: float, z: float, w: float) -> float:
        """
        Extract yaw angle from quaternion
        Args:
            x, y, z, w: Quaternion components
        Returns:
            float: Yaw angle in radians
        """
        # Calculate yaw (z-axis rotation) from quaternion
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        return np.arctan2(siny_cosp, cosy_cosp)
        
    def control_loop(self) -> None:
        """Main control loop with error handling"""
        try:
            if not self.is_tracking_active:
                return
                
            # Calculate and send control commands
            cmd = self.calculate_control_commands()
            if cmd is not None:
                self.cmd_vel_pub.publish(cmd)
            else:
                self.send_zero_velocity()
                
            # Publish tracking status
            status_msg = Bool()
            status_msg.data = self.is_tracking_active
            self.status_pub.publish(status_msg)
            
        except Exception as e:
            self.get_logger().error(f"Error in control loop: {e}")
            self.enable_tracking(False)
            self.send_zero_velocity()

def main(args=None):
    rclpy.init(args=args)
    controller = ControlManager()
    
    try:
        rclpy.spin(controller)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        controller.get_logger().error(f"Unexpected error: {e}")
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
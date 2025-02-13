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
        self
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
                ('yaw_tolerance', 5.0)
            ]
        )
        
        # Load parameters
        self.control_params = {
            'max_velocity': self.get_parameter('max_velocity').value,
            'max_acceleration': self.get_parameter('max_acceleration').value,
            'max_yaw_rate': self.get_parameter('max_yaw_rate').value,
            'tracking_distance': self.get_parameter('tracking_distance').value,
            'min_altitude': self.get_parameter('min_altitude').value,
            'max_altitude': self.get_parameter('max_altitude').value,
            'position_tolerance': self.get_parameter('position_tolerance').value,
            'yaw_tolerance': self.get_parameter('yaw_tolerance').value,
        }
        
        # Initialize control states
        self.last_target_pose = None
        self.current_pose = None
        self.last_control_time = time.time()
        self.is_tracking_active = False
        
        # ROS2 Publishers
        self.cmd_vel_pub = self.create_publisher(
            Twist,
            '/drone0/cmd_vel',  # Using namespace from launch file
            10
        )
        
        self.status_pub = self.create_publisher(
            Bool,
            '/drone0/tracking_status',
            10
        )
        
        # ROS2 Subscribers
        self.target_sub = self.create_subscription(
            PoseStamped,
            '/drone0/target_pose',
            self.target_callback,
            10
        )
        
        self.odom_sub = self.create_subscription(
            Odometry,
            '/drone0/odom',
            self.odom_callback,
            10
        )
        
        # Control loop timer
        self.timer = self.create_timer(
            1.0/30.0,  # 30 Hz
            self.control_loop
        )
        
        self.get_logger().info('Control Manager initialized for simulation')
        
    def target_callback(self, msg: PoseStamped) -> None:
        """Handle incoming target pose updates"""
        self.last_target_pose = msg
        
    def odom_callback(self, msg: Odometry) -> None:
        """Handle odometry updates"""
        self.current_pose = msg.pose.pose
        
    def enable_tracking(self, enable: bool) -> None:
        """Enable or disable tracking mode"""
        if enable != self.is_tracking_active:
            self.is_tracking_active = enable
            self.get_logger().info(f"Tracking {'enabled' if enable else 'disabled'}")
            
            if not enable:
                self.last_target_pose = None
                self.send_zero_velocity()
                
    def send_zero_velocity(self) -> None:
        """Send zero velocity command"""
        cmd = Twist()
        self.cmd_vel_pub.publish(cmd)
        
    def calculate_control_commands(self) -> Optional[Twist]:
        """Calculate control commands based on current state"""
        if not self.last_target_pose or not self.current_pose:
            return None
            
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
        
        # Calculate desired velocity (P controller)
        kp = 0.5  # Position gain
        desired_vel = kp * pos_error
        
        # Apply velocity limits
        speed = np.linalg.norm(desired_vel)
        if speed > self.control_params['max_velocity']:
            desired_vel = desired_vel * self.control_params['max_velocity'] / speed
            
        # Create velocity command
        cmd = Twist()
        cmd.linear.x = float(desired_vel[0])
        cmd.linear.y = float(desired_vel[1])
        cmd.linear.z = float(desired_vel[2])
        
        # Calculate yaw to face target
        target_yaw = np.arctan2(pos_error[1], pos_error[0])
        # Get current yaw from quaternion
        _, _, current_yaw = self.quaternion_to_euler(
            self.current_pose.orientation.x,
            self.current_pose.orientation.y,
            self.current_pose.orientation.z,
            self.current_pose.orientation.w
        )
        
        # Calculate yaw error and normalize
        yaw_error = np.arctan2(np.sin(target_yaw - current_yaw), 
                              np.cos(target_yaw - current_yaw))
        
        # Apply yaw rate limit
        yaw_rate = np.clip(yaw_error * 2.0,
                          -np.radians(self.control_params['max_yaw_rate']),
                          np.radians(self.control_params['max_yaw_rate']))
                          
        cmd.angular.z = float(yaw_rate)
        
        return cmd
        
    def quaternion_to_euler(self, x: float, y: float, z: float, w: float) -> tuple:
        """Convert quaternion to euler angles"""
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = np.arctan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        pitch = np.arcsin(sinp)
        
        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = np.arctan2(siny_cosp, cosy_cosp)
        
        return roll, pitch, yaw
        
    def control_loop(self) -> None:
        """Main control loop"""
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
    finally:
        controller.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
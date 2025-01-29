#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    ExecuteProcess,
    GroupAction
)
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Declare arguments
    namespace = LaunchConfiguration('namespace')
    use_sim_time = LaunchConfiguration('use_sim_time')
    world_file = LaunchConfiguration('world_file')

    # Declare launch arguments
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='drone0',
        description='Namespace of the drone'
    )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )

    declare_world_file_cmd = DeclareLaunchArgument(
        'world_file',
        default_value=os.path.join(
            get_package_share_directory('drone_tracker'),
            'worlds',
            'tracking_world.world'
        ),
        description='Gazebo world file'
    )

    # Load config files
    config_sim = os.path.join(
        get_package_share_directory('drone_tracker'),
        'config',
        'simulation_params.yaml'
    )
    config_tracker = os.path.join(
        get_package_share_directory('drone_tracker'),
        'config',
        'tracker_params.yaml'
    )

    # Launch Gazebo Garden
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_file],
        output='screen'
    )

    # Bridge between Gazebo and ROS
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='parameter_bridge',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            # Add required bridges here
            'bridge_topics': [
                # Add topic remappings as needed
                '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
                '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
                '/camera@sensor_msgs/msg/Image[gz.msgs.Image',
            ]
        }]
    )

    # Launch Aerostack2 base nodes
    as2_core = GroupAction([
        PushRosNamespace(namespace),
        
        # Platform interface
        Node(
            package='as2_platform_gazebo',
            executable='as2_platform_gazebo_node',
            name='platform',
            parameters=[{
                'use_sim_time': use_sim_time,
                'simulation_mode': True
            }],
            output='screen'
        ),

        # State estimator
        Node(
            package='as2_state_estimator',
            executable='as2_state_estimator_node',
            name='state_estimator',
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
            output='screen'
        ),

        # Controller
        Node(
            package='as2_controller',
            executable='as2_controller_node',
            name='controller',
            parameters=[{
                'use_sim_time': use_sim_time,
            }],
            output='screen'
        ),

        # Tracker node (our custom node)
        Node(
            package='drone_tracker',
            executable='tracker_node',
            name='tracker',
            parameters=[
                {'use_sim_time': use_sim_time},
                config_sim,
                config_tracker
            ],
            output='screen'
        )
    ])  # Closing bracket for GroupAction

    # Create launch description and add actions
    ld = LaunchDescription()

    # Add declared arguments
    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_world_file_cmd)

    # Add main actions
    ld.add_action(gazebo)
    ld.add_action(bridge)
    ld.add_action(as2_core)

    return ld
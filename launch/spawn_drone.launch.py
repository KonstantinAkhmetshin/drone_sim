from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get the package share directory
    pkg_share = get_package_share_directory('drone_sim')
    
    # Path to the model file
    model_path = os.path.join(pkg_share, 'drone.sdf')
    
    # Print model path for debugging
    print(f"Using model from: {model_path}")
    
    # Launch Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        launch_arguments={
            'gz_args': '-v 4 empty.world',  # Added verbose flag and explicit world
        }.items(),
    )
    
    # Add small delay to ensure Gazebo is fully loaded
    delay = ExecuteProcess(
        cmd=['sleep', '2'],
        output='screen'
    )
    
    # Node to spawn the drone
    spawn_drone = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-file', model_path,
            '-name', 'drone',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '2.0',
            '-R', '0.0',
            '-P', '0.0',
            '-Y', '0.0'
        ]
    )
    
    # Node to control the drone
    drone_controller = Node(
        package='drone_sim',
        executable='drone_controller',
        name='drone_controller',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        delay,
        spawn_drone,
        drone_controller
    ])
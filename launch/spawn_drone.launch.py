# Launches Gazebo with an empty world
# Spawns the drone model at position (0,0,0.5)
# Starts the drone controller node
# Coordinates all necessary ROS2 nodes for simulation

# Import required ROS2 launch modules
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # Get the package share directory path
    pkg_share = get_package_share_directory('drone_sim')
    
    # Include Gazebo launch file with empty world
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ]),
        # Launch arguments for Gazebo
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )
    
    # Node to spawn the drone in Gazebo
    spawn_drone = Node(
        package='ros_gz_sim',  # Package containing spawn tool
        executable='create',    # Spawn executable name
        arguments=[
            '-name', 'drone',   # Model name
            '-x', '0.0',        # X position
            '-y', '0.0',        # Y position
            '-z', '0.5',        # Z position
            '-file', os.path.join(pkg_share, 'models', 'drone.sdf')  # Path to model file
        ],
        output='screen'  # Display output in terminal
    )
    
    # Node to control the drone
    drone_controller = Node(
        package='drone_sim',
        executable='drone_controller',
        name='drone_controller'
    )
    
    # Return launch description with all nodes
    return LaunchDescription([
        gazebo,
        spawn_drone,
        drone_controller
    ])

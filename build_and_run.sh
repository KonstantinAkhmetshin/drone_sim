#!/bin/bash

# Stop on any error
set -e

# Source ROS2 environment
source /opt/ros/jazzy/setup.bash

# Clean previous build
rm -rf build/ install/

# Build the package
colcon build

# Source the newly built package
source install/setup.bash

# Run the simulation
ros2 launch drone_sim spawn_drone.launch.py
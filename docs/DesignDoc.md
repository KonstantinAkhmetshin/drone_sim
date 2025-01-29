# Autonomous Drone Object Tracking System

## Project Overview
This project implements an autonomous drone object tracking system using ROS2, Aerostack2 (AS2), and Gazebo Garden simulator. The system enables a quadcopter to autonomously track and follow a moving target using computer vision and advanced control algorithms.

## System Architecture

### High-Level Components
1. **Simulation Environment** (Gazebo Garden)
   - Provides physics simulation
   - Handles drone dynamics
   - Simulates sensor data (cameras, IMU)
   - Contains the target object for tracking

2. **ROS2-Gazebo Bridge**
   - Enables communication between ROS2 and Gazebo
   - Handles message translations
   - Manages simulation time synchronization

3. **Aerostack2 Framework**
   - Provides drone control infrastructure
   - Handles state estimation
   - Manages platform interfaces
   - Coordinates behavior execution

4. **Object Tracking System**
   - Processes camera images
   - Detects and tracks target objects
   - Generates control commands

## Directory Structure Explanation

```
as2_workspace/src/drone_tracker/
├── config/                      # Configuration directory
│   ├── simulation_params.yaml   # Simulation configuration
│   └── tracker_params.yaml      # Tracking algorithm parameters
├── launch/
│   └── simulation.launch.py     # Main launch file
├── worlds/
│   └── tracking_world.world     # Gazebo world definition
├── models/                      # Gazebo model files
├── resource/
│   └── drone_tracker           # Package resource index
├── drone_tracker/              # Python module directory
│   ├── __init__.py
│   └── tracker_node.py        # Main tracking implementation
├── package.xml                 # Package manifest
└── setup.py                   # Package setup script
```

### File Details and Purpose

#### Configuration Files
1. `simulation_params.yaml`
   - Drone physical parameters (mass, inertia)
   - Camera configuration
   - PID controller gains
   - ROS2-Gazebo bridge settings
   Purpose: Defines all simulation-related parameters in one place for easy tuning

2. `tracker_params.yaml`
   - Object detection settings
   - Tracking algorithm parameters
   - Movement constraints
   - Logging configuration
   Purpose: Controls the behavior of the tracking system

#### Launch Files
`simulation.launch.py`
- Launches all necessary components
- Configures node parameters
- Sets up ROS2-Gazebo bridge
- Initializes Aerostack2 nodes
Purpose: Provides a single entry point to start the entire system

#### World Files
`tracking_world.world`
- Defines simulation environment
- Specifies target object properties
- Configures physics settings
- Sets up lighting and ground plane
Purpose: Creates the virtual environment for testing

#### Python Module Files
1. `tracker_node.py`
   - Implements main tracking logic
   - Processes camera images
   - Generates control commands
   - Manages target tracking state
   Purpose: Core implementation of the tracking system

## System Workflow

### Initialization Phase
1. Launch file starts Gazebo simulation
2. ROS2-Gazebo bridge establishes communication
3. Aerostack2 nodes initialize
4. Tracker node begins monitoring camera feed

### Operation Phase
1. **Image Processing**
   - Camera feed is received from Gazebo
   - Images are processed to detect target
   - Target position is extracted

2. **Target Tracking**
   - Target position is tracked over time
   - Velocity and trajectory are estimated
   - Target state is maintained

3. **Control Generation**
   - Desired drone position is calculated
   - Control commands are generated
   - Commands are sent to Aerostack2

4. **Execution**
   - Aerostack2 processes commands
   - Drone movement is simulated in Gazebo
   - New sensor data is generated

## Key Features

### Object Detection
- Color-based detection
- Size filtering
- Position estimation
- Confidence scoring

### Tracking Algorithm
- Position prediction
- Lost target recovery
- Multiple object disambiguation
- Noise filtering

### Control System
- PID control for position
- Smooth trajectory generation
- Speed and acceleration limits
- Safety constraints

## Parameters and Configuration

### Key Simulation Parameters
- Drone physical properties
- Camera specifications
- Control gains
- World properties

### Key Tracking Parameters
- Detection thresholds
- Tracking constraints
- Following behavior
- Safety limits

## Development and Testing

### Build Instructions
```bash
cd as2_workspace
colcon build
source install/setup.bash
```

### Launch Commands
```bash
ros2 launch drone_tracker simulation.launch.py
```

### Testing Scenarios
1. Stationary target tracking
2. Moving target following
3. Lost target recovery
4. Multiple object disambiguation

## Future Enhancements
1. Multiple drone coordination
2. Advanced object recognition
3. Dynamic obstacle avoidance
4. Path planning optimization

## Dependencies
- ROS2 Jazzy
- Gazebo Garden
- Aerostack2
- OpenCV
- Python 3.8+

## Performance Considerations
- Image processing frequency
- Control loop rate
- Communication latency
- Resource utilization

## Safety Features
- Maximum speed limits
- Safe distance maintenance
- Lost target handling
- Emergency stop conditions
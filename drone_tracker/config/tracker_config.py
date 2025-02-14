"""
Configuration parameters for the drone tracking system.
"""

# Detection parameters
DETECTION_CONFIG = {
    "target_color": (0, 255, 0),  # Green in BGR
    "color_tolerance": 20,
    "min_object_size": 100,
    "max_object_size": 10000,
    "confidence_threshold": 0.7
}

# Controller parameters
CONTROLLER_CONFIG = {
    "max_velocity": 5.0,  # meters per second
    "tracking_distance": 5.0,  # meters
    "pid_gains": {
        "x": {"P": 0.5, "I": 0.0, "D": 0.1},
        "y": {"P": 0.5, "I": 0.0, "D": 0.1},
        "z": {"P": 0.5, "I": 0.0, "D": 0.1},
        "yaw": {"P": 1.0, "I": 0.0, "D": 0.1}
    }
}

# Camera parameters
CAMERA_CONFIG = {
    "width": 640,
    "height": 480,
    "fov": 90,
    "fps": 30
}

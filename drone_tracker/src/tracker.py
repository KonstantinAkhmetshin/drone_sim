"""
Main tracking system that coordinates detection and control.
"""
import airsim
import cv2
import numpy as np
from typing import Optional, Dict
from .detector import ObjectDetector
from .controller import DroneController

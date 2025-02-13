# setup.py
from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'drone_tracker'

setup(
    # Package information
    name=package_name,
    version='0.0.1',
    packages=find_packages(),
    
    # Dependencies
    install_requires=[
        'setuptools',
        'opencv-python',
        'numpy',
    ],
    
    # Package data and resources
    data_files=[
        # Package index
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
            
        # Package manifest
        ('share/' + package_name, ['package.xml']),
        
        # Launch files
        (os.path.join('share', package_name, 'launch'),
         glob('launch/*launch.[pxy][yma]*')),
         
        # Configuration files
        (os.path.join('share', package_name, 'config'), [
            'config/simulation_params.yaml',
            'config/tracker_params.yaml',
        ]),
        
        # World files
        (os.path.join('share', package_name, 'worlds'),
         glob('worlds/*.world')),
         
        # Model files
        (os.path.join('share', package_name, 'models'),
         glob('models/**/*', recursive=True)),
    ],
    
    # Make package zip safe
    zip_safe=True,
    
    # Maintainer info
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Autonomous drone object tracking package',
    license='Apache-2.0',
    
    # Tests
    tests_require=['pytest'],
    
    # Entry points for ROS2 nodes
    entry_points={
        'console_scripts': [
            'tracker_node = drone_tracker.tracker_node:main',
            'control_manager = drone_tracker.control_manager:main', 
            'test_tracking_system = test.test_tracking_system:main',
        ],
    },
)
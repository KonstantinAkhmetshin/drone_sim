from setuptools import setup
import os
from glob import glob

package_name = 'drone_tracker'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # Include all launch files
        (os.path.join('share', package_name, 'launch'), 
         glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        # Include all configuration files
        (os.path.join('share', package_name, 'config'), [
            'config/simulation_params.yaml',
            'config/tracker_params.yaml'
        ]),
        # Include all world files
        (os.path.join('share', package_name, 'worlds'),
         glob(os.path.join('worlds', '*.world'))),
        # Include all model files
        (os.path.join('share', package_name, 'models'),
         glob(os.path.join('models', '*.*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your.email@example.com',
    description='Autonomous drone object tracking package',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'tracker_node = drone_tracker.tracker_node:main',
        ],
    },
)
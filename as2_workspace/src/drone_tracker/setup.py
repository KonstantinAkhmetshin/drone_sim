from setuptools import setup

package_name = 'drone_tracker'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/config', [
            'config/default_params.yaml',
            'config/simulation_params.yaml'
        ]),
        ('share/' + package_name + '/launch', [
            'launch/simulation.launch.py',
            'launch/hardware.launch.py'
        ]),
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

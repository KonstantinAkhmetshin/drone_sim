from setuptools import setup

setup(
    name='drone_sim',
    version='0.0.1',
    packages=['drone_sim'],
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/drone_sim']),
        ('share/drone_sim/launch', ['launch/spawn_drone.launch.py']),
        ('share/drone_sim/models', ['models/model.sdf']),
    ],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='you@example.com',
    description='Drone simulation package',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'drone_controller = drone_sim.drone_controller:main',
        ],
    },
)
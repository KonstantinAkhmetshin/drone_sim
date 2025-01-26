from setuptools import setup

setup(
   name='drone_sim',
   version='0.0.1',
   packages=['python'],
   install_requires=['setuptools'],
   data_files=[
       ('share/ament_index/resource_index/packages', ['resources/drone_sim']),
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
           'drone_controller = python.drone_controller:main',
       ],
   },
)
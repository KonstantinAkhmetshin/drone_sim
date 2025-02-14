from setuptools import setup, find_packages

setup(
    name="drone_tracker",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'opencv-python',
        'airsim',
        'matplotlib'
    ],
)

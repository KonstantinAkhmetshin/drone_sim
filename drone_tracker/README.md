# Drone Object Tracking System

This project implements autonomous object tracking using AirSim drone simulation.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AirSim:
- Copy `config/settings.json` to AirSim settings location
- Adjust parameters in `config/tracker_config.py` as needed

## Usage

Run the tracking system:
```bash
python main.py
```

## Testing

Run the test suite:
```bash
python -m unittest tests/test_tracking.py
```

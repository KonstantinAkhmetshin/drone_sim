"""
Flight Controller Connection Test Script

This script verifies the connection to a flight controller via USB
and prints basic system information and parameters.

For SpeedyBee F405 V4 FC (or similar) running ArduPilot.
"""

import time
from pymavlink import mavutil
import sys

def connect_to_fc():
    """
    Attempt to connect to the flight controller via USB.
    Returns a MAVLink connection object or None if connection fails.
    """
    # Try common USB-C connection strings on Linux
    connection_strings = [
        '/dev/ttyACM0',  # Common Linux USB-C device
        '/dev/ttyACM1',
        '/dev/ttyUSB0',  # Alternative Linux USB device
        '/dev/ttyUSB1',
        '/dev/ttyS0',    # Serial port that might be used by USB-C
        '/dev/serial/by-id/usb-*',  # Try to find USB devices by ID
    ]
    
    # For manual connection string
    if len(sys.argv) > 1:
        connection_strings.insert(0, sys.argv[1])
    
    print("Attempting to connect to flight controller...")
    
    for device in connection_strings:
        try:
            print(f"Trying {device}...")
            # Connect with MAVLink (common protocol for ArduPilot/PX4)
            connection = mavutil.mavlink_connection(device, baud=115200)
            connection.wait_heartbeat(timeout=5)
            print(f"Connected to system: {connection.target_system}")
            return connection
        except Exception as e:
            print(f"Failed to connect to {device}: {e}")
    
    return None

def get_fc_status(connection):
    """
    Request and display basic flight controller status information.
    """
    if not connection:
        print("No connection available")
        return
    
    try:
        # Request system status
        connection.mav.request_data_stream_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            1,  # Rate in Hz
            1   # Start/stop (1=start)
        )
        
        print("\n--- Flight Controller Information ---")
        
        # Get firmware version
        connection.mav.command_long_send(
            connection.target_system,
            connection.target_component,
            mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
            0,  # Confirmation
            mavutil.mavlink.MAVLINK_MSG_ID_AUTOPILOT_VERSION,
            0, 0, 0, 0, 0, 0  # Parameters
        )
        
        # Wait for heartbeat to confirm system is responding
        msg = connection.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
        if msg:
            print(f"System type: {msg.type}")
            print(f"Autopilot type: {msg.autopilot}")
            print(f"System mode: {msg.custom_mode}")
            print(f"System status: {msg.system_status}")
        else:
            print("No heartbeat received - connection may be unstable")
        
        # Get basic parameters
        print("\n--- Basic Parameters ---")
        params_to_check = ['FRAME_TYPE', 'FRAME_CLASS', 'PILOT_THR_BHV', 'BATT_MONITOR']
        
        for param in params_to_check:
            connection.mav.param_request_read_send(
                connection.target_system, connection.target_component,
                param.encode('utf-8'),
                -1  # -1 for requesting by name
            )
            msg = connection.recv_match(type='PARAM_VALUE', blocking=True, timeout=2)
            if msg:
                print(f"{param}: {msg.param_value}")
            else:
                print(f"{param}: Not available")
        
        # Get battery info
        print("\n--- Battery Status ---")
        start_time = time.time()
        while time.time() - start_time < 3:  # Try for 3 seconds
            msg = connection.recv_match(type='SYS_STATUS', blocking=True, timeout=1)
            if msg:
                voltage = msg.voltage_battery / 1000.0  # Convert from millivolts to volts
                current = msg.current_battery / 100.0   # Convert to amps
                remaining = msg.battery_remaining       # Percentage
                print(f"Battery: {voltage:.2f}V, Current: {current:.2f}A, Remaining: {remaining}%")
                break
        
        # Get GPS status if available
        print("\n--- GPS Status ---")
        start_time = time.time()
        while time.time() - start_time < 3:  # Try for 3 seconds
            msg = connection.recv_match(type='GPS_RAW_INT', blocking=True, timeout=1)
            if msg:
                fix_type = msg.fix_type
                satellites = msg.satellites_visible
                print(f"GPS Fix Type: {fix_type} (0=No GPS, 1=No Fix, 2=2D Fix, 3=3D Fix)")
                print(f"Satellites visible: {satellites}")
                break
            
    except Exception as e:
        print(f"Error while getting FC status: {e}")

def main():
    """Main function to test FC connection and get basic status."""
    connection = connect_to_fc()
    
    if connection:
        print("Successfully connected to flight controller!")
        get_fc_status(connection)
        
        print("\nConnection test complete.")
        print("If you see system information above, your FC is properly connected.")
        print("If some information is missing, that may be normal depending on your setup.")
    else:
        print("\nFailed to connect to flight controller.")
        print("Please check:")
        print("1. USB cable is properly connected")
        print("2. Flight controller is powered on")
        print("3. Correct drivers are installed")
        print("4. Try specifying the port manually: python fc_connection_test.py /dev/ttyXXX")

if __name__ == "__main__":
    main()
#
# MAVLink Motor Test Script for ArduPilot
#
# This script sends a MAVLink command to test each motor of a quadcopter individually.
# It uses the recommended MAV_CMD_DO_MOTOR_TEST command.
#
# Author: Gemini
#

import time
from pymavlink import mavutil

# ######################################################################################
# ##################  S A F E T Y   W A R N I N G  #####################################
# ######################################################################################
#
# !! REMOVE ALL PROPELLERS BEFORE RUNNING THIS SCRIPT !!
#
# Spinning motors are extremely dangerous. Failure to remove propellers can result in
# serious personal injury and/or damage to your property.
#
# By running this script, you acknowledge that you have removed all propellers and
# that you are solely responsible for any consequences.
#
# ######################################################################################

# --- Configuration ---
# Set the connection string for your vehicle.
# Examples:
# - Serial (USB): '/dev/ttyACM0' (Linux) or 'COM3' (Windows)
# - Telemetry Radio: '/dev/ttyUSB0' (Linux) or 'COM5' (Windows)
# - UDP (SITL or Companion Computer): 'udp:127.0.0.1:14550'
CONNECTION_STRING = '/dev/ttyACM0'
BAUD_RATE = 57600 # This is only used for serial connections

# --- Motor Test Parameters ---
# The throttle percentage to apply during the test.
# START WITH A LOW VALUE (5-10%) to ensure everything is working as expected.
THROTTLE_PERCENT = 15

# The duration in seconds to run each motor.
MOTOR_TEST_DURATION_S = 2

def run_motor_test():
    """
    Connects to the vehicle and runs the motor test sequence.
    """
    print("--- MAVLink Motor Test Script ---")
    print("WARNING: ENSURE ALL PROPELLERS ARE REMOVED.")
    
    # Simple countdown to give the user a final chance to abort
    for i in range(5, 0, -1):
        print(f"Starting in {i} seconds... (Press Ctrl+C to abort)")
        time.sleep(1)

    master = None
    try:
        # --- Connect to the Vehicle ---
        print(f"\nConnecting to vehicle on: {CONNECTION_STRING}")
        if 'udp' in CONNECTION_STRING or 'tcp' in CONNECTION_STRING:
            master = mavutil.mavlink_connection(CONNECTION_STRING)
        else:
            master = mavutil.mavlink_connection(CONNECTION_STRING, baud=BAUD_RATE)

        # Wait for the first heartbeat message to confirm a connection
        print("Waiting for heartbeat...")
        master.wait_heartbeat()
        print(f"Heartbeat received from system (ID: {master.target_system}, Component: {master.target_component})")
        print("Connection successful!")
        time.sleep(1) # Add a short delay to allow the connection to stabilize

        # --- Run Test Sequence ---
        # For a quadcopter, motors are typically numbered 1 through 4.
        # This loop will test each one sequentially.
        print("\n--- Starting Motor Test Sequence ---")
        for motor_index in range(1, 5):
            print(f"Testing Motor #{motor_index} at {THROTTLE_PERCENT}% for {MOTOR_TEST_DURATION_S} seconds.")
            
            # Send the MAV_CMD_DO_MOTOR_TEST command
            master.mav.command_long_send(
                master.target_system,                           # Target system ID
                master.target_component,                        # Target component ID
                mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,          # Command
                0,                                              # Confirmation
                motor_index,                                    # Param 1: Motor sequence number (1-indexed)
                mavutil.mavlink.MOTOR_TEST_THROTTLE_PERCENT,    # Param 2: Throttle type
                THROTTLE_PERCENT,                               # Param 3: Throttle value
                MOTOR_TEST_DURATION_S,                          # Param 4: Duration (seconds)
                0,                                              # Param 5: Not used
                0,                                              # Param 6: Not used
                0                                               # Param 7: Not used
            )
            
            # Wait for the test on the current motor to complete
            time.sleep(MOTOR_TEST_DURATION_S + 1) # Add 1s buffer

        print("\n--- Motor test sequence finished. ---")

    except KeyboardInterrupt:
        print("\nScript aborted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Could not connect to the vehicle or run the test. Please check:")
        print("- Is the vehicle powered on and connected?")
        print("- Is the CONNECTION_STRING correct?")
        print("- If using a serial port, is the BAUD_RATE correct and is the port available?")
    finally:
        if master:
            master.close()
        print("Script finished.")

if __name__ == "__main__":
    run_motor_test()

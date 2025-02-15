import airsim
import time

def spawn_basic_target():
    """
    Attempts to spawn a simple cube in front of the drone using basic parameters.
    """
    try:
        # Connect to AirSim
        client = airsim.MultirotorClient()
        client.confirmConnection()
        
        # Enable API control
        client.enableApiControl(True)
        client.armDisarm(True)
        
        print("AirSim connected and API control enabled")
        
        # Wait a moment for everything to initialize
        time.sleep(2)
        
        # Get drone's position
        state = client.getMultirotorState()
        pos = state.kinematics_estimated.position
        
        # Calculate spawn position (3 meters in front, at same height)
        spawn_pos = {
            "x": float(pos.x_val + 1.0),
            "y": float(pos.y_val),
            "z": float(pos.z_val)
        }
        
        print(f"Attempting to spawn object at: x={spawn_pos['x']}, y={spawn_pos['y']}, z={spawn_pos['z']}")
        
        # Try to spawn a basic cube
        scale = airsim.Vector3r(1.0, 1.0, 1.0)
        pose = airsim.Pose(position_val=airsim.Vector3r(5.0, 0.0, 0.0))
         
        success = client.simSpawnObject("Cube", "cube", pose, scale, True)

        if success:
            print("Successfully spawned object!")
            
            # Point drone towards the object
            client.hoverAsync().join()
            print("Drone stabilized")
            
            return True
        else:
            print("Failed to spawn object")
            return False
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Detailed error info:")
        print(f"Error type: {type(e)}")
        print(f"Error args: {e.args}")
        return False

if __name__ == "__main__":
    print("Starting basic spawn test...")
    print("Make sure AirSim is running and drone is visible")
    input("Press Enter to continue...")
    
    result = spawn_basic_target()
    if not result:
        print("\nTroubleshooting tips:")
        print("1. Make sure AirSim is fully loaded")
        print("2. Check if drone is visible in the environment")
        print("3. Try restarting AirSim")
        print("4. Make sure you're running in the correct environment")
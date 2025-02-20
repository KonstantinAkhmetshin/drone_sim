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
        
        
        # Try to spawn a basic cube
        scale = airsim.Vector3r(1.0, 1.0, 1.0)
        pose = airsim.Pose(position_val=airsim.Vector3r(10.0, 0.0, 0.0))
         
        objectName = "Sphere" 
        asssrtName = "sphere"
        success = client.simSpawnObject(objectName, asssrtName, pose, scale, True)

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
    result = spawn_basic_target()
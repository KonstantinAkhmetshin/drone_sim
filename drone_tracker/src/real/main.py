"""
Tennis Ball Detector using iPhone's EpocCam as webcam source.

This script captures frames from your iPhone via EpocCam, detects tennis balls using 
HSV color filtering and contour analysis, and displays the results in real-time
with detected balls framed in a green box.

Press 'q' to quit
Press 'h' to show current HSV values
Press 'c' to cycle through available cameras
Use trackbars to adjust HSV thresholds for better detection
"""
import cv2
import numpy as np
import time
import argparse


def list_available_cameras(max_to_check=10):
    """Check which camera indices are available"""
    available = []
    for i in range(max_to_check):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                available.append(i)
                print(f"Camera {i} is available: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
            cap.release()
    return available


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tennis Ball Detector with EpocCam Support')
    parser.add_argument('--camera', type=int, default=0, help='Camera device ID (default: 0)')
    parser.add_argument('--width', type=int, default=1280, help='Camera width (default: 1280)')
    parser.add_argument('--height', type=int, default=720, help='Camera height (default: 720)')
    parser.add_argument('--list', action='store_true', help='List available cameras and exit')
    args = parser.parse_args()
    
    # List available cameras if requested
    if args.list:
        print("Listing available cameras:")
        available_cameras = list_available_cameras()
        print(f"Found {len(available_cameras)} cameras: {available_cameras}")
        return
    
    # Variables for camera switching
    current_camera = args.camera
    available_cameras = []
    
    def open_camera(camera_id):
        """Open a camera and configure it"""
        cap = cv2.VideoCapture(camera_id)
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_id}")
            return None
            
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
        
        print(f"Opened camera {camera_id}: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
        return cap
    
    # Open initial camera
    cap = open_camera(current_camera)
    if cap is None:
        print("Failed to open initial camera. Try using --list to see available cameras.")
        return
    
    # Create window and trackbars for HSV adjustment
    cv2.namedWindow('Tennis Ball Detector')
    cv2.createTrackbar('H min', 'Tennis Ball Detector', 25, 179, lambda x: None)
    cv2.createTrackbar('H max', 'Tennis Ball Detector', 45, 179, lambda x: None)
    cv2.createTrackbar('S min', 'Tennis Ball Detector', 100, 255, lambda x: None)
    cv2.createTrackbar('S max', 'Tennis Ball Detector', 255, 255, lambda x: None)
    cv2.createTrackbar('V min', 'Tennis Ball Detector', 100, 255, lambda x: None)
    cv2.createTrackbar('V max', 'Tennis Ball Detector', 255, 255, lambda x: None)
    cv2.createTrackbar('Min Radius', 'Tennis Ball Detector', 10, 100, lambda x: None)
    cv2.createTrackbar('Max Radius', 'Tennis Ball Detector', 50, 200, lambda x: None)
    
    # Performance tracking
    frame_times = []
    start_time = time.time()
    frame_count = 0
    fps = 0
    
    print("Tennis Ball Detector running.")
    print("Controls:")
    print("  'q' - Quit")
    print("  'h' - Show HSV values")
    print("  'c' - Cycle through available cameras")
    
    try:
        while True:
            loop_start = time.time()
            
            # Read frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame, trying next camera...")
                # Try to switch to another camera
                if not available_cameras:
                    available_cameras = list_available_cameras()
                
                if len(available_cameras) > 1:
                    current_index = available_cameras.index(current_camera) if current_camera in available_cameras else -1
                    next_index = (current_index + 1) % len(available_cameras)
                    current_camera = available_cameras[next_index]
                    
                    # Release current camera and open new one
                    cap.release()
                    cap = open_camera(current_camera)
                    if cap is None:
                        break
                    continue
                else:
                    print("No other cameras available.")
                    break
            
            # Create copies for visualization
            orig_frame = frame.copy()
            debug_frame = frame.copy()
            
            # Get HSV threshold values from trackbars
            h_min = cv2.getTrackbarPos('H min', 'Tennis Ball Detector')
            h_max = cv2.getTrackbarPos('H max', 'Tennis Ball Detector')
            s_min = cv2.getTrackbarPos('S min', 'Tennis Ball Detector')
            s_max = cv2.getTrackbarPos('S max', 'Tennis Ball Detector')
            v_min = cv2.getTrackbarPos('V min', 'Tennis Ball Detector')
            v_max = cv2.getTrackbarPos('V max', 'Tennis Ball Detector')
            min_radius = cv2.getTrackbarPos('Min Radius', 'Tennis Ball Detector')
            max_radius = cv2.getTrackbarPos('Max Radius', 'Tennis Ball Detector')
            
            # Convert to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Apply Gaussian blur to reduce noise
            hsv = cv2.GaussianBlur(hsv, (5, 5), 0)
            
            # Create mask for tennis ball color
            lower_hsv = np.array([h_min, s_min, v_min])
            upper_hsv = np.array([h_max, s_max, v_max])
            mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
            
            # Apply morphological operations to clean up the mask
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.erode(mask, kernel, iterations=1)
            mask = cv2.dilate(mask, kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Show binary mask in a separate window
            # cv2.imshow('Binary Mask', mask)
            
            # Draw all contours on debug frame
            cv2.drawContours(debug_frame, contours, -1, (0, 0, 255), 2)
            
            # Process each contour
            best_ball = None
            best_score = float('inf')
            
            for contour in contours:
                # Get area and perimeter
                area = cv2.contourArea(contour)
                if area < 50:  # Filter out tiny contours
                    continue
                    
                # Fit circle
                (x, y), radius = cv2.minEnclosingCircle(contour)
                center = (int(x), int(y))
                radius = int(radius)
                
                # Check radius constraints
                if radius < min_radius or radius > max_radius:
                    continue
                
                # Calculate circularity
                perimeter = cv2.arcLength(contour, True)
                circularity = 4 * np.pi * area / (perimeter ** 2) if perimeter > 0 else 0
                
                # Skip if not circular enough
                if circularity < 0.6:
                    continue
                
                # Calculate center position weight (prefer objects near image center)
                center_x = frame.shape[1] / 2
                center_y = frame.shape[0] / 2
                dist_from_center = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                max_dist = np.sqrt(center_x**2 + center_y**2)
                position_weight = dist_from_center / max_dist if max_dist > 0 else 0
                
                # Combined score (lower is better)
                score = (1.0 - circularity) * 0.7 + position_weight * 0.3
                
                # Draw potential match on debug frame
                cv2.circle(debug_frame, center, radius, (255, 0, 0), 2)
                cv2.putText(
                    debug_frame,
                    f"C:{circularity:.2f} S:{score:.2f}",
                    (center[0] - radius, center[1] - radius - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1
                )
                
                # Keep track of best match
                if score < best_score:
                    best_score = score
                    best_ball = (center, radius, circularity, score, contour)
            
            # Draw best match if found
            if best_ball:
                center, radius, circularity, score, contour = best_ball
                
                # Calculate bounding box for the detected ball
                x, y, w, h = cv2.boundingRect(contour)
                
                # Draw green bounding box around the ball
                cv2.rectangle(orig_frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
                
                # Draw circle and center point
                cv2.circle(orig_frame, center, radius, (0, 255, 0), 2)
                cv2.circle(orig_frame, center, 5, (0, 0, 255), -1)  # Center dot
                
                # Draw crosshair to center
                frame_center = (frame.shape[1] // 2, frame.shape[0] // 2)
                cv2.line(orig_frame, frame_center, center, (0, 255, 255), 2)
                
                # Add info text
                cv2.putText(
                    orig_frame,
                    f"Tennis Ball: r={radius}, circ={circularity:.2f}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )
                
                # Calculate distance from image center
                dist_x = center[0] - frame.shape[1]/2
                dist_y = center[1] - frame.shape[0]/2
                
                # Show position relative to center
                position_text = f"Position: "
                if abs(dist_x) < 50 and abs(dist_y) < 50:
                    position_text += "CENTERED"
                else:
                    if dist_x > 50:
                        position_text += "RIGHT "
                    elif dist_x < -50:
                        position_text += "LEFT "
                        
                    if dist_y > 50:
                        position_text += "DOWN"
                    elif dist_y < -50:
                        position_text += "UP"
                        
                cv2.putText(
                    orig_frame,
                    position_text,
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )
            else:
                # No ball found
                cv2.putText(
                    orig_frame,
                    "No tennis ball detected",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2
                )
            
            # Calculate FPS
            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                fps = frame_count / elapsed
                frame_count = 0
                start_time = time.time()
            
            # Display FPS and processing time
            process_time = time.time() - loop_start
            frame_times.append(process_time)
            if len(frame_times) > 30:
                frame_times.pop(0)
            avg_process_time = sum(frame_times) / len(frame_times)
            
            cv2.putText(
                orig_frame,
                f"FPS: {fps:.1f} | Process: {avg_process_time*1000:.1f}ms | Camera: {current_camera}",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )
            
            # Show frames
            cv2.imshow('Tennis Ball Detector', orig_frame)
            cv2.imshow('Debug View', debug_frame)
            
            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Quitting...")
                break
            elif key == ord('h'):
                print(f"Current HSV Range: [{h_min},{s_min},{v_min}] to [{h_max},{s_max},{v_max}]")
                print(f"Radius Range: {min_radius} to {max_radius}")
            elif key == ord('c'):
                # Cycle through available cameras
                if not available_cameras:
                    available_cameras = list_available_cameras()
                
                if len(available_cameras) > 1:
                    current_index = available_cameras.index(current_camera) if current_camera in available_cameras else -1
                    next_index = (current_index + 1) % len(available_cameras)
                    current_camera = available_cameras[next_index]
                    
                    print(f"Switching to camera {current_camera}")
                    
                    # Release current camera and open new one
                    cap.release()
                    cap = open_camera(current_camera)
                    if cap is None:
                        break
                else:
                    print("No other cameras available.")
    
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Release resources
        if 'cap' in locals() and cap is not None:
            cap.release()
        cv2.destroyAllWindows()
        print("Detector stopped")


if __name__ == "__main__":
    main()
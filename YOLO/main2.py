from BT2 import bluetooth_login
from Yolo import run_mediapipe_hand_detection
from detect import Face
from save import register_face
#from GazeTracking.example import Monitor
from ultralytics import YOLO
import mediapipe as mp
import subprocess
import threading
import cv2
import time


if __name__ == "__main__":
    print("Starting the system...")
    #custom_model = YOLO('Versions/Hands.pt')q
    #Monitor()
    flag = 0 
    flag2= 0
    trigger_object = "Thumbs up"  # Define the object to trigger Mediapipe
    trigger_object2 = "Thumbs Down"
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    
    cap = cv2.VideoCapture(0)  # Open the primary camera
    # Global variables to manage Mediapipe process
    mediapipe_running = False
    mediapipe_process = None
    def detect_gesture(landmarks):
        """
        Detect gestures based on hand landmarks with refined logic.

        Args:
            landmarks (list): List of hand landmarks.

        Returns:
            str: Detected gesture name or None if no gesture is recognized.
        """
        # Get key landmarks for analysis
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        index_base = landmarks[5]
        middle_tip = landmarks[12]
        middle_base = landmarks[9]
        ring_tip = landmarks[16]
        ring_base = landmarks[13]
        pinky_tip = landmarks[20]
        pinky_base = landmarks[17]

        # Gesture: "Stop" (All 4 fingers extended upward)
        if (
           
            index_tip.y < index_base.y and
            middle_tip.y < middle_base.y and
            ring_tip.y < ring_base.y and
            pinky_tip.y < pinky_base.y
        ):
            return "Stop"

        # Gesture: "Thumbs down" (Thumb bent downward)
        if (
            thumb_tip.y > thumb_ip.y and 
            index_tip.y > index_base.y and 
            middle_tip.y > middle_base.y
        ):
            return "Thumbs down"

        # Gesture: "Thumbs up" (Thumb extended upward and above other fingers)
        if (
            thumb_tip.y < thumb_ip.y and 
            thumb_tip.y < index_base.y and 
            middle_tip.y > middle_base.y
        ):
            return "Thumbs up"

        # Gesture: "Right" (Hand rotated with index and thumb extended horizontally)
        if (
            index_tip.x > index_base.x and 
            thumb_tip.x > thumb_ip.x and 
            thumb_tip.y > thumb_ip.y
        ):
            return "Right"

        # Add more gestures as needed
        return None

    
    last_gesture_time = 0 
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture video.")
                    break

                # Convert frame to RGB for MediaPipe processing
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw hand landmarks on the frame
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        
                        # Detect gestures
                        current_time = time.time()
                        if current_time - last_gesture_time >= 2:
                            gesture = detect_gesture(hand_landmarks.landmark)
                            if gesture:
                                print(f"Detected gesture: {gesture}")
                                last_gesture_time = current_time

                                if gesture == "Thumbs up":
                                    flag=1
                                    print("Bluettooth login...")
                                elif gesture == "Thumbs down":
                                    flag=2
                                    print("Face login...")
                                
                                elif gesture == "Stop":
                                    if(flag==1):
                                        flag2=1
                                    elif(flag==2):
                                        flag2=2
                                    cap.release()
                                    cv2.destroyAllWindows()
                                    break
                            
                                

                # Display the frame with landmarks
                cv2.imshow("MediaPipe Hand Detection", frame)

                if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
                    break

    cap.release()
    cv2.destroyAllWindows()
    if(flag2==1):
        mac_address = bluetooth_login()
        if not mac_address:
            print("Exiting due to unsuccessful login.")
        else:
            print("Login successful. Starting YOLO detection.")
            
            # Step 2: YOLO Object Detection and Mediapipe Trigger
            run_mediapipe_hand_detection()
    elif(flag2==2):
        enter=Face()
        if(enter==None):
           print("no face is registered")
           print("Please register your face first")
           register_face()

        else:
            run_mediapipe_hand_detection()
            


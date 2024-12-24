import cv2
import mediapipe as mp
import subprocess
import threading
from ultralytics import YOLO
import time

# Initialize MediaPipe Hands module
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

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

        # Gesture: "Thumbs down" (Thumb bent downward)
        if thumb_tip.y > thumb_ip.y and index_tip.y > index_base.y and middle_tip.y > middle_base.y:
            return "Thumbs down"

        # Gesture: "Thumbs up" (Thumb extended upward and above other fingers)
        if thumb_tip.y < thumb_ip.y and thumb_tip.y < index_base.y and middle_tip.y > middle_base.y:
            return "Thumbs up"

        # Gesture: "Stop" (Index finger pointing upward)
        if index_tip.y < index_base.y and thumb_tip.x < thumb_ip.x:  # Index finger is up and thumb is closed
            return "Stop"

        # Gesture: "Right" (Hand rotated with index and thumb extended horizontally)
        if index_tip.x > index_base.x and thumb_tip.x > thumb_ip.x and thumb_tip.y > thumb_ip.y:
            return "Right"
        
        if index_tip.x < index_base.x and thumb_tip.x < thumb_ip.x and thumb_tip.y > thumb_ip.y:
            return "Left"

        # Add more gestures as needed
        return None


def run_mediapipe():
    """Launch Mediapipe in a separate process."""
    global mediapipe_process
    global mediapipe_running
    if mediapipe_process is None:
        mediapipe_running = True
        mediapipe_process = subprocess.Popen(["python", "Mediapipe.py"])
        print("Mediapipe started.")


def stop_mediapipe():
    """Stop the Mediapipe process."""
    global mediapipe_process
    if mediapipe_process is not None:
        mediapipe_process.terminate()
        mediapipe_process = None
        print("Mediapipe stopped.")

def run_yolo_model():
    """
    Run a YOLO model to detect objects and display results in a window with annotations.
    """
    model = YOLO('Versions/best.pt')

    # Open video capture
    cap = cv2.VideoCapture(0)  # Use the primary camera

    if not cap.isOpened():
        print("Failed to open camera.")
        return

    print("Running YOLO model. Press 'Esc' to exit.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture video.")
            break
        base_results = model(frame)
        # YOLO model inference
        annotated_base_frame = base_results[0].plot()

        cv2.imshow("YOLO Detection",  annotated_base_frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break

    cap.release()
    cv2.destroyAllWindows()


def run_mediapipe_hand_detection():
    """
    Use MediaPipe Hand Tracking to detect gestures and trigger actions.

    Actions:
        - Thumbs up: Start Mediapipe.
        - Thumbs down: Launch `main2.py`.
        - Stop: Terminate program and launch `emotions.py`.
        - Right: Stop Mediapipe if running.
    """
    cap = cv2.VideoCapture(0)  # Open the primary camera
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

                    current_time = time.time()
                    if current_time - last_gesture_time >= 2:
                        gesture = detect_gesture(hand_landmarks.landmark)
                        if gesture:
                            print(f"Detected gesture: {gesture}")
                            last_gesture_time = current_time

                            if gesture == "Thumbs up":
                                if not mediapipe_running:  # Launch Mediapipe if not already running
                                    threading.Thread(target=run_mediapipe, daemon=True).start()
                                    cap.release()
                                    cv2.destroyAllWindows()
                                    return

                            elif gesture == "Left":
                                print("Launching main2.py...")
                                cap.release()
                                cv2.destroyAllWindows()
                                subprocess.run(["python", "emotions.py"])
                                return
                            #elif gesture == "Stop":
                                #print("Exiting program...")
                                #cap.release()
                                #cv2.destroyAllWindows()
                                #subprocess.run(["python", "emotions.py"])
                                #return
                            elif gesture == "Right":
                                print("Stopping Mediapipe...")
                                stop_mediapipe()
                            elif gesture == "Thumbs down":
                                print("Running YOLO model...")
                                cap.release()
                                cv2.destroyAllWindows()
                                run_yolo_model()
                                return

            # Display the frame with landmarks
            cv2.imshow("MediaPipe Hand Detection", frame)

            if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
                break

    cap.release()
    cv2.destroyAllWindows()

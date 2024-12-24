import threading
import bluetooth
import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import StringVar
import mediapipe as mp
import time

# Load your gesture detection mode
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
def load_registered_users(file_path="registered_users.txt"):
    """Load registered MAC addresses from a file."""
    try:
        with open(file_path, 'r') as file:
            mac_addresses = {line.strip() for line in file.readlines()}
        return mac_addresses
    except FileNotFoundError:
        print(f"File {file_path} not found. No registered users.")
        return set()

def is_user_registered(device_mac, registered_users):
    """Check if a device MAC address is registered."""
    return device_mac in registered_users

def bluetooth_login():
    """Select a Bluetooth device using gestures with GUI feedback."""
    print("Scanning for Bluetooth devices...")
    devices = bluetooth.discover_devices(lookup_names=True)
    
    if not devices:
        print("No Bluetooth devices found. Ensure Bluetooth is enabled.")
        return None

    print("Devices found:")
    for i, (addr, name) in enumerate(devices):
        print(f"{i + 1}: {name} [{addr}]")

    # Load registered MAC addresses
    registered_users = load_registered_users()
    print("Registered MAC addresses loaded.")

    # Filter devices to only show those with registered MAC addresses
    devices = [(addr, name) for addr, name in devices if is_user_registered(addr, registered_users)]
    if not devices:
        print("No devices found with registered MAC addresses.")
        return None

    # Index for tracking the currently selected device
    selected_index = 0

    # Shared variable to store the selected device
    selected_device = [None, None]  # Use a mutable container to store both MAC and name
    selection_event = threading.Event()

    # Create a GUI for displaying the selected device
    root = tk.Tk()
    root.title("Bluetooth Device Selection")
    root.geometry("400x200")

    selected_device_var = StringVar()
    selected_device_var.set(f"Selected: {devices[selected_index][1]} [{devices[selected_index][0]}]")

    label = tk.Label(root, textvariable=selected_device_var, font=("Helvetica", 14), pady=20)
    label.pack()

    instruction_label = tk.Label(root, text="Use gestures to navigate:\n- 'Thumbs up' for next\n- 'Thumbs down' for previous\n- 'Stop' to select", font=("Helvetica", 10))
    instruction_label.pack()

    def update_gui():
        """Update the GUI to show the currently selected device."""
        selected_device_var.set(f"Selected: {devices[selected_index][1]} [{devices[selected_index][0]}]")
    

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

        # Add more gestures as needed
        return None

    def run_camera():
        """Run the camera loop for gesture detection with MediaPipe."""
        nonlocal selected_index  # Ensure we can modify the outer scope variable
        cap = cv2.VideoCapture(0)  # Use the primary camera
        last_gesture_time = 0 
        with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture video.")
                    break
                
                # Convert frame to RGB for MediaPipe
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)
                
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        # Draw landmarks on the hand
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                        # Detect gesture
                        current_time = time.time()
                        if current_time - last_gesture_time >= 2: 
                            gesture = detect_gesture(hand_landmarks.landmark)
                            if gesture:
                                last_gesture_time = current_time
                                if gesture == "Thumbs up":
                                    selected_index = (selected_index + 1) % len(devices)
                                    print(f"Selected next device: {devices[selected_index][1]}")
                                    update_gui()
                                elif gesture == "Thumbs down":
                                    selected_index = (selected_index - 1) % len(devices)
                                    print(f"Selected previous device: {devices[selected_index][1]}")
                                    update_gui()
                                elif gesture == "Stop":
                                    print(f"Device selected: {devices[selected_index][1]}")
                                    selected_device[0] = devices[selected_index][0]
                                    selected_device[1] = devices[selected_index][1]
                                    selection_event.set()
                                    cap.release()
                                    cv2.destroyAllWindows()
                                    root.quit()
                                    return

                cv2.imshow("Gesture Detection", frame)
                if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
                    break

        cap.release()
        cv2.destroyAllWindows()

    # Run the camera loop in a separate thread
    threading.Thread(target=run_camera, daemon=True).start()

    # Wait for the selection event or GUI close
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()

    # Wait for the selection event from the camera thread
    selection_event.wait()
    root.destroy()
    # Show a welcome screen after the device is selected
    if selected_device[1]:  # Use name of the selected device
        root = tk.Tk()
        root.title("Welcome Screen")
        root.geometry("400x200")

        welcome_label = tk.Label(root, text=f"Welcome!\nDevice selected:\n{selected_device[1]}", font=("Helvetica", 14), pady=20)
        welcome_label.pack()

        def close_welcome_screen():
            root.destroy()

        # Auto-close the window after 3 seconds
        root.after(3000, close_welcome_screen)

        root.mainloop()

    return selected_device[0]  # Return the selected device's MAC address

if __name__ == "__main__":
    selected_device = bluetooth_login()
    if selected_device:
        print(f"Successfully selected device with MAC address: {selected_device}")
    else:
        print("No device selected.")

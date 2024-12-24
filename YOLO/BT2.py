import threading
import bluetooth
import cv2
import os
import tkinter as tk
from tkinter import StringVar, messagebox
import mediapipe as mp
import time

# Load MediaPipe for gesture detection
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

REGISTERED_USERS_FILE = "registered_users.txt"

def load_registered_users(file_path=REGISTERED_USERS_FILE):
    """Load registered MAC addresses from a file."""
    try:
        with open(file_path, 'r') as file:
            mac_addresses = {line.strip() for line in file.readlines()}
        return mac_addresses
    except FileNotFoundError:
        print(f"File {file_path} not found. No registered users.")
        return set()

def save_registered_user(device_mac, file_path=REGISTERED_USERS_FILE):
    """Save a new MAC address to the registered users file."""
    with open(file_path, 'a') as file:
        file.write(f"{device_mac}\n")
    print(f"Device with MAC address {device_mac} has been registered.")

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

    # Index for tracking the currently selected device
    selected_index = 0
    selected_device = [None, None]  # Mutable container for selected MAC and name
    selection_event = threading.Event()

    # Create GUI
    root = tk.Tk()
    root.title("Bluetooth Device Selection")
    root.geometry("400x200")

    selected_device_var = StringVar()
    label = tk.Label(root, textvariable=selected_device_var, font=("Helvetica", 14), pady=20)
    label.pack()

    def update_gui():
        """Update the GUI to show the currently selected device."""
        if devices:
            selected_device_var.set(f"Selected: {devices[selected_index][1]} [{devices[selected_index][0]}]")
        else:
            selected_device_var.set("No devices available.")

    update_gui()

    def detect_gesture(landmarks):
        """Detect gestures based on hand landmarks."""
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

        if (
            index_tip.y < index_base.y and
            middle_tip.y < middle_base.y and
            ring_tip.y < ring_base.y and
            pinky_tip.y < pinky_base.y
        ):
            return "Stop"

        if thumb_tip.y > thumb_ip.y and index_tip.y > index_base.y and middle_tip.y > middle_base.y:
            return "Thumbs down"

        if thumb_tip.y < thumb_ip.y and thumb_tip.y < index_base.y and middle_tip.y > middle_base.y:
            return "Thumbs up"

        return None

    def run_camera():
        nonlocal selected_index
        cap = cv2.VideoCapture(0)
        last_gesture_time = 0 
        with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Failed to capture video.")
                    break

                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb_frame)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
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
                if cv2.waitKey(1) & 0xFF == 27:
                    break

        cap.release()
        cv2.destroyAllWindows()

    threading.Thread(target=run_camera, daemon=True).start()
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
    if selected_device[0] and selected_device[0] not in registered_users:
        root = tk.Tk()
        root.withdraw()
        if messagebox.askyesno("Register Device", f"Do you want to register the device '{selected_device[1]}' with MAC {selected_device[0]}?"):
            save_registered_user(selected_device[0])
            registered_users.add(selected_device[0])
        root.destroy()

        
    selection_event.wait()
    root.destroy()
    if selected_device[0]:
        print(f"Welcome! Device selected: {selected_device[1]}")
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
        return selected_device[0]
    else:
        print("No device selected.")
        return None

#if __name__ == "__main__":
    #selected_device = bluetooth_login()
    #if selected_device:
        #print(f"Successfully logged in with device MAC address: {selected_device}")
    #else:
        #print("No device selected or registered.")

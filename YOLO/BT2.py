import threading
import bluetooth
import cv2
from ultralytics import YOLO
import tkinter as tk
from tkinter import StringVar

# Load your gesture detection model
gesture_model = YOLO('Versions/Hands.pt')

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

    def run_camera():
        """Run the camera loop for gesture detection."""
        nonlocal selected_index  # Ensure we can modify the outer scope variable
        cap = cv2.VideoCapture(1)  # Start the camera feed

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Failed to capture video. Exiting.")
                break

            # Detect gestures using YOLO model
            results = gesture_model(frame)  # Run YOLO inference
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls)  # Class ID
                    label = gesture_model.model.names[cls]  # Gesture label
                    print(f"Detected gesture: {label}")

                    # Handle gestures for navigation
                    if label == "Thumbs up":
                        selected_index = (selected_index + 1) % len(devices)
                        print(f"Selected next device: {devices[selected_index][1]}")
                        update_gui()  # Update the GUI with the new selection
                    elif label == "Thumbs Down":
                        selected_index = (selected_index - 1) % len(devices)
                        print(f"Selected previous device: {devices[selected_index][1]}")
                        update_gui()  # Update the GUI with the new selection
                    elif label == "Stop":
                        print(f"Device selected: {devices[selected_index][1]}")
                        selected_device[0] = devices[selected_index][0]  # MAC address
                        selected_device[1] = devices[selected_index][1]  # Name
                        selection_event.set()  # Notify the main thread of the selection
                        cap.release()
                        cv2.destroyAllWindows()
                        root.quit()  # Close the main GUI immediately
                        return

            # Annotate and display the video feed with YOLO results
            annotated_frame = results[0].plot()
            cv2.imshow("Gesture Detection", annotated_frame)

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

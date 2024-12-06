import bluetooth
import socket
import threading
import time

def loading_animation(event):
    """Displays a loading animation until the event is set."""
    while not event.is_set():
        for frame in ["|", "/", "-", "\\"]:
            print(f"\rScanning for Bluetooth devices... {frame}", end="")
            time.sleep(0.2)
    print("\rScan complete.                  ")  # Clear loading line

def scan_bluetooth_devices():
    """Scans for nearby Bluetooth devices and allows the user to select one."""
    print("Starting Bluetooth scan...")
    scan_complete_event = threading.Event()
    loading_thread = threading.Thread(target=loading_animation, args=(scan_complete_event,))
    loading_thread.start()

    try:
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
        scan_complete_event.set()  # Stop the loading animation
        loading_thread.join()      # Wait for the animation thread to finish

        if not nearby_devices:
            print("No Bluetooth devices found.")
            return None

        print(f"Found {len(nearby_devices)} devices:")
        devices=[]
        for i, (addr, name) in enumerate(nearby_devices):
            device_name = name if name else "Unknown Device"
            print(f"{i + 1}: {addr} - {device_name}")
            devices.append({"index": i + 1, "mac": addr, "name": device_name})

        return send_and_receive_data(devices)
      
    except Exception as e:
        scan_complete_event.set()  # Ensure the loading animation stops on error
        loading_thread.join()
        print("An error occurred during Bluetooth scanning:", str(e))
        return None

def send_and_receive_data(devices, host='127.0.0.1', port=65432):
    """Sends the list of device names to the C# application, waits for a response, and sends back the selected MAC address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Connecting to {host}:{port}...")
            s.connect((host, port))

            # Send the names of the devices
            device_names = "\n".join([device["name"] for device in devices])
            #device_names = "\n".join([device for device in devices])
            print(f"Sending device names: {device_names}")
            s.sendall(device_names.encode())
            print("Sent list of device names to C# application.")
            return listen_and_send_mac(devices)

            
    except socket.error as e:
        print(f"Socket error occurred: {e}")
    except Exception as e:
        print("An error occurred:", str(e))

def listen_and_send_mac(devices, host='127.0.0.1', port=65432):
    """
    Listens for a device index from a C# application and sends back the corresponding MAC address.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        try:
            server.bind((host, port))
            server.listen(1)
            print(f"Listening for connections on {host}:{port}...")

            conn, addr = server.accept()
            with conn:
                print(f"Connection established with {addr}")

                # Receive the selected device index from C#
                data = conn.recv(1024).decode().strip()
                if not data:
                    print("No data received.")
                    return
                
                try:
                    selected_index = int(data)
                    print(f"Received index: {selected_index}")
                except ValueError:
                    print("Invalid index received.")
                    return

                # Find the corresponding device
                selected_device = next((d for d in devices if d["index"] == selected_index), None)
                if not selected_device:
                    print("Invalid index: No matching device found.")
                    return

                # Send the MAC address back to C#
                mac_address = selected_device["mac"]
                conn.sendall(mac_address.encode())
                print(f"Sent MAC address: {mac_address} back to C#.")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    devices = scan_bluetooth_devices()
  

import face_recognition
import os
import cv2
from functions import capture_user_face
import socket

def socketConn(host='127.0.0.1', port=12345):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            try:
                server.bind((host, port))
                server.listen(1)
                print(f"Listening for connections on {host}:{port}...")

                conn, addr = server.accept()
                with conn:
                    print(f"Connection established with {addr}")

                    
                    data = conn.recv(1024).decode().strip()
                    if not data:
                        print("No data received.")
                        return
                    
                    try:
                        flag = int(data)
                        if flag == 1:
                            print("C# accepted the connection.")
                            return 1
                        else:
                            print("C# rejected the connection.")
                            return 0
                    except ValueError:
                        print("Invalid flag received.")
                        return
                    
            except Exception as e:
                print(f"An error occurred: {e}")
                return
def send_name(message,host="127.0.0.1", port=12346):
    try:
        # Create a TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            # Connect to the C# server
            client_socket.connect((host, port))
            print(f"Connected to {host}:{port}")
            # Send the string message
            client_socket.sendall(message.encode('utf-8'))
            print(f"Sent message: {message}")
            
            
    except Exception as e:
        print(f"Error: {e}")

def recognize_user_face(captured_face_path, faces_folder="user_faces"):

    captured_image = face_recognition.load_image_file(captured_face_path)
    captured_encodings = face_recognition.face_encodings(captured_image)

    if not captured_encodings:
        print("No face detected in the captured image.")
        return None

    captured_encoding = captured_encodings[0]

    for filename in os.listdir(faces_folder):
        file_path = os.path.join(faces_folder, filename)

        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        existing_image = face_recognition.load_image_file(file_path)
        existing_encodings = face_recognition.face_encodings(existing_image)

        if not existing_encodings:
            print(f"No face detected in file: {filename}")
            continue

        existing_encoding = existing_encodings[0]

        match = face_recognition.compare_faces([existing_encoding], captured_encoding)

        if match[0]:
            print(f"Match found! The captured face matches {filename}.")
            return filename.split('.')[0]  # Return the name without file extension

    print("No match found in the existing faces.")
    return None

if __name__ == "__main__":
    flag=socketConn()
    #flag=1
    if flag == 1:
        captured_face_path = capture_user_face()

        if not captured_face_path:
            print("No face was captured.")
        else:
            matched_face = recognize_user_face(captured_face_path)
            #send_name(matched_face)
            video_capture = cv2.VideoCapture(1)

            while True:
                ret, frame = video_capture.read()
                if not ret:
                    break

                face_locations = face_recognition.face_locations(frame)

                if len(face_locations) > 0:
                    top, right, bottom, left = face_locations[0]

                    # Draw a rectangle around the detected face
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                    # Display the recognized name if matched
                    if matched_face:
                        cv2.putText(
                            frame,
                            matched_face,
                            (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 255, 0),
                            2,
                        )
                    else:
                        cv2.putText(
                            frame,
                            "Unknown",
                            (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.9,
                            (0, 0, 255),
                            2,
                        )

                # Show the video frame with the name overlay
                cv2.imshow("Face Recognition", frame)

                # Break the loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            video_capture.release()
            cv2.destroyAllWindows()

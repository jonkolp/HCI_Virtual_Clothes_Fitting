import face_recognition
import os
import cv2
from functions import capture_user_face
import time

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

def Face():
    captured_face_path = capture_user_face()

    if not captured_face_path:
        print("No face was captured.")
        return None  # Return None if no face is captured
    else:
        matched_face = recognize_user_face(captured_face_path)

        video_capture = cv2.VideoCapture(0)

        # Start the timer
        start_time = time.time()

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
                    return None
                

            # Show the video frame with the name overlay
            cv2.imshow("Face Recognition", frame)

            # Check if 5 seconds have passed or 'q' is pressed
            if (time.time() - start_time > 5) or (cv2.waitKey(1) & 0xFF == ord('q')):
                break

        video_capture.release()
        cv2.destroyAllWindows()

        return 1 

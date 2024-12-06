import cv2
import face_recognition
import os

def capture_user_face_and_save():
    if not os.path.exists('user_faces'):
        os.makedirs('user_faces')

    video_capture = cv2.VideoCapture(0)

    user_name = input("Enter your name: ")

    print("Capturing face... Please look at the camera.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)

        if len(face_locations) > 0:
            top, right, bottom, left = face_locations[0]
            face_image = frame[top:bottom, left:right]
            
            face_file_path = f"user_faces/{user_name}.jpg"
            cv2.imwrite(face_file_path, face_image)
            print(f"Face saved as {face_file_path}")
            break

    video_capture.release()
    cv2.destroyAllWindows()

    return face_file_path



def capture_user_face():
    if not os.path.exists('user_faces'):
        os.makedirs('user_faces')

    video_capture = cv2.VideoCapture(0)


    print("Capturing face... Please look at the camera.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)

        if len(face_locations) > 0:
            top, right, bottom, left = face_locations[0]
            face_image = frame[top:bottom, left:right]
            
            face_file_path = "user_faces/temp/temp.jpg"
            cv2.imwrite(face_file_path, face_image)
            print(f"Face saved as {face_file_path}")
            break

    video_capture.release()
    cv2.destroyAllWindows()

    return face_file_path



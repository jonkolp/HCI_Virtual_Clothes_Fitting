import cv2
import face_recognition
import os

def get_camera(preferred=0, fallback=1):
    cap = cv2.VideoCapture(preferred)
    if not cap.isOpened() or not cap.read()[0]:
        cap.release()
        cap = cv2.VideoCapture(fallback)
    return cap

def capture_user_face_and_save():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    faces_dir = os.path.join(base_dir, 'user_faces')
    os.makedirs(faces_dir, exist_ok=True)

    video_capture = get_camera(preferred=0, fallback=1)

    user_name = input("Enter your name: ")
    print("Capturing face... Please look at the camera.")

    face_file_path = None
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) > 0:
            top, right, bottom, left = face_locations[0]
            face_image = frame[top:bottom, left:right]
            
            face_file_path = os.path.join(faces_dir, f"{user_name}.jpg")
            cv2.imwrite(face_file_path, face_image)
            print(f"Face saved as {face_file_path}")
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return face_file_path


def capture_user_face():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, 'user_faces', 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    video_capture = get_camera(preferred=1, fallback=0)
    print("Capturing face... Please look at the camera.")

    face_file_path = None
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        face_locations = face_recognition.face_locations(frame)
        if len(face_locations) > 0:
            top, right, bottom, left = face_locations[0]
            face_image = frame[top:bottom, left:right]
            
            face_file_path = os.path.join(temp_dir, "temp.jpg")
            cv2.imwrite(face_file_path, face_image)
            print(f"Face saved as {face_file_path}")
            break

    video_capture.release()
    cv2.destroyAllWindows()
    return face_file_path



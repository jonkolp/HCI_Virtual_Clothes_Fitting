from functions import capture_user_face_and_save
def register_face():
    file_path = capture_user_face_and_save()
    if file_path:
        print(f"Face image saved at: {file_path}")
    else:
        print("No face was captured.")
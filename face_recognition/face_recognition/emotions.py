import cv2
from deepface import DeepFace

def detect_emotions_from_camera():
    # Initialize the camera
    cap = cv2.VideoCapture(0)

    # Load OpenCV's pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture video frame")
                break

            # Convert frame to grayscale for face detection
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                # Extract the face from the frame
                face_img = frame[y:y + h, x:x + w]

                try:
                    # Analyze the face using DeepFace
                    results = DeepFace.analyze(face_img, actions=['emotion'], enforce_detection=False)

                    # Ensure results is a list and access the first element
                    if isinstance(results, list) and len(results) > 0:
                        result = results[0]  # Get the first result in the list
                        emotion = result["dominant_emotion"]

                        # Draw a rectangle around the face
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Put the emotion text above the face rectangle
                        cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                except Exception as e:
                    print(f"Error analyzing face: {e}")

            # Display the frame in a window
            cv2.imshow("Emotion Detection", frame)

            # Break the loop if the user presses 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # Release the camera and close all OpenCV windows
        cap.release()
        cv2.destroyAllWindows()

# Run the function
if __name__ == "__main__":
    detect_emotions_from_camera()

import cv2
import numpy as np
import matplotlib.pyplot as plt
from gaze_tracking import GazeTracking
from PIL import ImageGrab
import csv
from deepface import DeepFace
from collections import Counter
def Monitor():
# Initialize GazeTracking
    gaze = GazeTracking()
    webcam = cv2.VideoCapture(0)

    # Open a CSV file for writing gaze points
    with open('gaze_points.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(['X', 'Y'])

        # Create a list to store gaze points
        gaze_points = []
        emotions = []  # List to store detected emotions

        # Load OpenCV's pre-trained face detection model
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        while True:
            # Capture frame from the webcam
            ret, frame = webcam.read()
            if not ret:
                print("Failed to capture video frame")
                break

            # Analyze the frame with GazeTracking
            gaze.refresh(frame)

            # Get pupil coordinates
            left_pupil = gaze.pupil_left_coords()
            right_pupil = gaze.pupil_right_coords()

            # If valid coordinates, store the average position
            if left_pupil and right_pupil:
                avg_x = (left_pupil[0] + right_pupil[0]) / 2
                avg_y = (left_pupil[1] + right_pupil[1]) / 2
                gaze_points.append((avg_x, avg_y))

                # Write the point to the CSV file
                writer.writerow([avg_x, avg_y])

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

                        # Store the emotion
                        emotions.append(emotion)

                        # Draw a rectangle around the face
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                        # Put the emotion text above the face rectangle
                        cv2.putText(frame, emotion, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                except Exception as e:
                    print(f"Error analyzing face: {e}")

            # Annotate the frame
            frame = gaze.annotated_frame()
            text = ""

            if gaze.is_blinking():
                text = "Blinking"
            elif gaze.is_right():
                text = "Looking right"
            elif gaze.is_left():
                text = "Looking left"
            elif gaze.is_center():
                text = "Looking center"

            cv2.putText(frame, text, (90, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (147, 58, 31), 2)

            cv2.putText(frame, f"Left pupil: {left_pupil}", (90, 130), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)
            cv2.putText(frame, f"Right pupil: {right_pupil}", (90, 165), cv2.FONT_HERSHEY_DUPLEX, 0.9, (147, 58, 31), 1)

            cv2.imshow("Gaze Tracking and Emotion Detection", frame)

            # Break loop on ESC key
            if cv2.waitKey(1) == 27:
                break

    # Release resources
    webcam.release()
    cv2.destroyAllWindows()

    # Generate heatmap from gaze points
    if gaze_points:
        # Extract x and y coordinates
        x_points, y_points = zip(*gaze_points)

        # Create a heatmap
        heatmap, xedges, yedges = np.histogram2d(x_points, y_points, bins=(64, 36))

        # Apply Gaussian smoothing
        heatmap = cv2.GaussianBlur(heatmap, (9, 9), 0)

        # Capture a screenshot of the current screen
        screenshot = ImageGrab.grab()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)
        screenshot = cv2.flip(screenshot, 1)

        # Plot the heatmap over the screenshot
        plt.figure(figsize=(10, 6))
        plt.imshow(screenshot, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], alpha=0.5)
        plt.imshow(heatmap.T, origin='lower', cmap='jet', alpha=0.5, extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
        plt.colorbar(label='Intensity')
        plt.title('Gaze Heatmap')
        plt.xlabel('X-axis (pixels)')
        plt.ylabel('Y-axis (pixels)')

        # Save the heatmap
        plt.savefig('gaze_heatmap_with_screenshot.png')
        plt.show()

    # Generate a report with the majority emotion
    if emotions:
        emotion_count = Counter(emotions)
        majority_emotion = emotion_count.most_common(1)[0][0]

        with open('emotion_report.txt', 'w') as report_file:
            report_file.write(f"Majority Emotion Detected: {majority_emotion}\n")
            report_file.write("Emotion Distribution:\n")
            for emotion, count in emotion_count.items():
                report_file.write(f"{emotion}: {count}\n")

        print("Emotion report saved as 'emotion_report.txt'.")
Monitor()
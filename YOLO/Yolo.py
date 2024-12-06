from ultralytics import YOLO
import cv2
import os
import subprocess
import threading

base_model = YOLO('Versions/yolo11s.pt')  # Pre-trained YOLOv8 base model
custom_model = YOLO('Versions/Hands.pt')  # Your custom-trained model
mediapipe_running = False
mediapipe_process = None 


def run_yolo_and_trigger_mediapipe():
    """Detect objects and trigger Mediapipe program."""
    def stop_mediapipe():
   
        global mediapipe_process
        if mediapipe_process is not None:  # Stop Mediapipe only if it's running
            mediapipe_process.terminate()
            mediapipe_process = None
            print("Mediapipe stopped.")
    def run_mediapipe():
        """Function to run Mediapipe in a separate process."""
        global mediapipe_process
        global mediapipe_running
        if mediapipe_process is None:
            mediapipe_running = True
            mediapipe_process = subprocess.Popen(["python", "Mediapipe.py"])
        mediapipe_running = False


    
    cap = cv2.VideoCapture(1)  # Start video capture
    trigger_object = "Thumbs up"  # Define the object to trigger Mediapipe
    trigger_object2 = "Up"
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Failed to capture video. Exiting.")
            break
        
        # Run YOLO detection using the base model
        base_results = base_model(frame)  # Inference with base model
        
        # Function to check detections and trigger Mediapipe
        def check_detections(results, model_name):
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls)  # Class ID
                    label = model_name[cls]  # Class name
                    print(f"Detected by {model_name}: {label}")
                    
                    # Trigger Mediapipe if the specific object is detected
                    if label == "Thumbs up":
                        if not mediapipe_running:  # Launch Mediapipe if not already running
                            threading.Thread(target=run_mediapipe, daemon=True).start()
                            #return True
                    if label == "Up":
                        print(f"MAIN")
                        cap.release()
                        cv2.destroyAllWindows()
                        subprocess.run(["python", "main2.py"])
                    if label == "Stop":
                        print(f"Closing Progaram")
                        cap.release()
                        cv2.destroyAllWindows()
                        subprocess.run(["python", "emotions.py"])
                        return "exit"
                    if label=="Right":
                        print(f"Closing Mediapipe for: {label} (Detected by {model_name})")
                        stop_mediapipe() 

            return False

        # Check detections from base model first
        if check_detections(base_results, base_model.names):
            break  # Stop if trigger is detected by base model
        
        # If no object is detected by base model, then run custom model detection
        custom_results = custom_model(frame)  # Inference with custom model
        if check_detections(custom_results, custom_model.names):
            break  # Stop if trigger is detected by custom model

        #Show video feed with detections from both models (optional)
        annotated_base_frame = base_results[0].plot()
        annotated_custom_frame = custom_results[0].plot()
        if check_detections(custom_results, custom_model.names) == "exit":
            print("Exiting program due to 'Thumbs down' gesture.")
            exit()
        
        combined_frame = cv2.hconcat([annotated_base_frame, annotated_custom_frame])
        cv2.imshow("YOLO Detection", combined_frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break

    cap.release()
    cv2.destroyAllWindows()

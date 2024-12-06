from BT2 import bluetooth_login
from Yolo import run_yolo_and_trigger_mediapipe
from detect import Face
from ultralytics import YOLO
import cv2

if __name__ == "__main__":
    print("Starting the system...")
    custom_model = YOLO('Versions/Hands.pt')
    flag = 0 
    cap = cv2.VideoCapture(1)  # Start video capture
    trigger_object = "Thumbs up"  # Define the object to trigger Mediapipe
    trigger_object2 = "Thumbs Down"
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Failed to capture video. Exiting.")
            break

        def check_detections(results, model_name):
            global  flag
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls)  # Class ID
                    label = model_name[cls]  # Class name
                    print(f"Detected by {model_name}: {label}")
                    
                    # Trigger Mediapipe if the specific object is detected
                    if label == trigger_object:
                        flag=1
                        print("Bluetooth")
                    if label == trigger_object2:
                        flag=2
                        print("Face")
                    if label == "Stop":
                        cap.release()
                        cv2.destroyAllWindows()
                        return flag

            return 0
        
        custom_results = custom_model(frame)  # Inference with custom model
        if check_detections(custom_results, custom_model.names):
            break  # Stop if trigger is detected by custom model

        annotated_custom_frame = custom_results[0].plot()
        if check_detections(custom_results, custom_model.names) == "exit":
            print("Exiting program due to 'Thumbs down' gesture.")
            exit()
        
        cv2.imshow("YOLO Detection",  annotated_custom_frame)

        if cv2.waitKey(1) & 0xFF == 27:  # Press 'Esc' to exit
            break

    cap.release()
    cv2.destroyAllWindows()
    if(flag==1):
        mac_address = bluetooth_login()
        if not mac_address:
            print("Exiting due to unsuccessful login.")
        else:
            print("Login successful. Starting YOLO detection.")
            
            # Step 2: YOLO Object Detection and Mediapipe Trigger
            run_yolo_and_trigger_mediapipe()
    elif(flag==2):
        enter=Face()
        if(enter==1):
            run_yolo_and_trigger_mediapipe()
        else:
            print("no face")


import cv2
import mediapipe as mp
import socket
import time  
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Initialize Socket Server
HOST = 'localhost'  # Localhost
PORT = 5000         # Port
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Server listening on {HOST}:{PORT}...")
conn, addr = server_socket.accept()
print(f"Connection established with {addr}")

last_sent_time = 0  
cooldown_seconds = 2 

def is_four_fingers_raised(hand_landmarks):
    fingers = [False] * 5 
    landmarks = hand_landmarks.landmark

    
    fingers[1] = landmarks[8].y < landmarks[6].y  # Index
    fingers[2] = landmarks[12].y < landmarks[10].y  # Middle
    fingers[3] = landmarks[16].y < landmarks[14].y  # Ring
    fingers[4] = landmarks[20].y < landmarks[18].y  # Pinky

    return sum(fingers) == 4  

def get_wrist_position(hand_landmarks):
    wrist = hand_landmarks.landmark[0]  
    return wrist.x, wrist.y
cap = cv2.VideoCapture(0)
if not cap.isOpened() or not cap.read()[0]:
    cap.release()
    cap = cv2.VideoCapture(1)

try:
   while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            wrist_x, wrist_y = get_wrist_position(hand_landmarks)

            # Check if gesture is detected for switching models
            current_time = time.time()
            if is_four_fingers_raised(hand_landmarks) and current_time - last_sent_time >= cooldown_seconds:
                message = f"SWITCH_MODEL,{wrist_x:.2f},{wrist_y:.2f}"
                conn.sendall(message.encode('utf-8'))
                last_sent_time = current_time
            else:
                # Send wrist position continuously without gesture
                message = f"TRACK_POSITION,{wrist_x:.2f},{wrist_y:.2f}"
                conn.sendall(message.encode('utf-8'))

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("MediaPipe Hand Detection", frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

finally:
    cap.release()
    server_socket.close()
    print("Server closed.")
    cv2.destroyAllWindows()

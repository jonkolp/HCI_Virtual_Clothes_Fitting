import cv2
import mediapipe as mp
import numpy as np
from dollarpy import Recognizer, Template, Point
import os
import random


swip_right = Template('swip_right', [
Point(35,391, 1),
Point(25,375, 1),
Point(13,372, 1),
Point(7,371, 1),
Point(41,387, 1),
Point(43,387, 1),
Point(45,385, 1),
Point(45,383, 1),
Point(43,381, 1),
Point(39,384, 1),
Point(39,384, 1),
Point(38,386, 1),
Point(42,398, 1),
Point(57,398, 1),
Point(66,398, 1),
Point(90,400, 1),
Point(108,407, 1),
Point(91,378, 1),
Point(60,374, 1),
Point(73,384, 1),
Point(78,401, 1),
Point(77,400, 1),
Point(62,377, 1),
Point(63,359, 1),
Point(50,318, 1),
Point(45,300, 1),
Point(37,276, 1),
Point(40,266, 1),
Point(37,273, 1),
Point(38,270, 1),
Point(15,276, 1),
Point(7,283, 1),
Point(12,301, 1),
Point(3,301, 1),
Point(-7,301, 1),
Point(-21,306, 1),
Point(-31,332, 1),
Point(-36,345, 1),
Point(-45,350, 1),
Point(-36,345, 1),
Point(-35,345, 1),
Point(-41,342, 1),
Point(-46,364, 1),
Point(-66,356, 1),
Point(-81,344, 1),
Point(-99,339, 1),
Point(-104,338, 1),
Point(-103,338, 1),
Point(-96,334, 1),
Point(-92,339, 1),
Point(-101,342, 1),
Point(-96,346, 1),
Point(-93,355, 1),
Point(-77,365, 1),
Point(-58,364, 1),
Point(-61,370, 1),
Point(-64,378, 1),
Point(-65,374, 1),
Point(-64,364, 1),
Point(-62,367, 1),
Point(-53,367, 1),
Point(-62,360, 1),
Point(-64,348, 1),
Point(-63,349, 1),
Point(-62,369, 1),
Point(-67,373, 1),
Point(-67,395, 1),
Point(-67,400, 1),
Point(-59,396, 1),
Point(-57,399, 1),
Point(-57,399, 1),
])
swip_left = Template('swip_left', [
Point(274,446, 1),
Point(280,423, 1),
Point(238,488, 1),
Point(230,508, 1),
Point(232,522, 1),
Point(238,531, 1),
Point(242,534, 1),
Point(236,534, 1),
Point(234,538, 1),
Point(245,537, 1),
Point(230,526, 1),
Point(225,524, 1),
Point(248,523, 1),
Point(251,520, 1),
Point(245,522, 1),
Point(252,522, 1),
Point(249,522, 1),
Point(248,523, 1),
Point(247,524, 1),
Point(253,523, 1),
Point(251,523, 1),
Point(241,523, 1),
Point(236,523, 1),
Point(232,523, 1),
Point(229,524, 1),
Point(231,524, 1),
Point(230,522, 1),
Point(230,521, 1),
Point(231,518, 1),
Point(233,518, 1),
Point(246,529, 1),
Point(246,529, 1),
Point(248,528, 1),
Point(247,528, 1),
Point(247,528, 1),
Point(247,527, 1),
Point(257,528, 1),
Point(277,523, 1),
Point(272,521, 1),
Point(270,521, 1),
Point(269,532, 1),
Point(254,536, 1),
Point(259,536, 1),
Point(268,522, 1),
Point(270,522, 1),
Point(276,515, 1),
Point(284,496, 1),
Point(285,501, 1),
Point(303,495, 1),
Point(289,499, 1),
Point(264,507, 1),
Point(245,511, 1),
Point(242,513, 1),
Point(221,517, 1),
Point(226,523, 1),
Point(232,523, 1),
Point(233,525, 1),
Point(231,525, 1),
Point(228,523, 1),
Point(229,510, 1),
Point(223,503, 1),
Point(225,484, 1),
Point(232,466, 1),
Point(238,472, 1),
Point(238,473, 1),
Point(240,450, 1),
Point(263,375, 1),
Point(272,337, 1),
Point(227,335, 1),
Point(217,339, 1),
Point(217,303, 1),
Point(216,339, 1),
Point(219,302, 1),
Point(211,311, 1),
Point(201,398, 1),
Point(195,397, 1),
Point(178,346, 1),
Point(172,366, 1),
Point(171,383, 1),
Point(162,321, 1),
Point(167,353, 1),
Point(173,426, 1),
Point(215,375, 1),
Point(176,375, 1),
Point(195,348, 1),
Point(229,427, 1),
Point(214,491, 1),
Point(212,497, 1),
Point(212,497, 1),
Point(216,497, 1),
Point(224,488, 1),
Point(221,495, 1),
Point(220,488, 1),
Point(220,486, 1),
Point(223,482, 1),
Point(223,481, 1),
Point(226,480, 1),
Point(226,479, 1),
Point(226,480, 1),
Point(225,480, 1),
Point(225,479, 1),
Point(218,484, 1),
Point(219,482, 1),
Point(219,480, 1),
Point(222,480, 1),
Point(222,482, 1),
Point(218,486, 1),
Point(220,486, 1),
Point(228,480, 1),
Point(228,481, 1),
Point(229,481, 1),
Point(229,481, 1),
Point(234,477, 1),
Point(242,475, 1),
Point(237,476, 1),
Point(232,476, 1),
Point(230,476, 1),
Point(229,476, 1),
])
recognizer = Recognizer([swip_right,swip_left])


framecnt=0

# Define paths to your folders
shirts_folder = 'clothes/shirt'  
pants_folder = 'clothes/pants'    
sleeves_folder = 'clothes/sleeves'   
hoodies_folder = 'clothes/hoodies' 

shirts =  []
sleeve =  []
hoodies = []

def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        if os.path.isfile(img_path): 
            img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if img is not None:  
                print(img)
                images.append(img)
    return images


shirts = load_images_from_folder(shirts_folder)
sleeves = load_images_from_folder(sleeves_folder)
hoodies = load_images_from_folder(hoodies_folder)






print("---------------------------------------------------")
print(sleeves)
print("---------------------------------------------------")

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

shirt_image = cv2.imread('T.png', cv2.IMREAD_UNCHANGED)
hoodie_image = cv2.imread('H.png', cv2.IMREAD_UNCHANGED)

switch = 0
type = 0




def recognize_gesture(captured_points):
    global switch  
    # Recognize gesture
    result = recognizer.recognize(captured_points)
    if result[0] == "swip_left":
         print(f"Recognized Gesture: {result[0]} with score: {result[1]}")
         return 2
    elif result[0] == "swip_right":
         print(f"Recognized Gesture: {result[0]} with score: {result[1]}")
         return 1
    else:
        print("No gesture recognized.")
        return False
        
       
       
def overlay_shirt(image, landmarks, scale_factor= 2.0, y_offset=90):
    global shirt_image, hoodie_image, switch

    if(type == 0):
        selected_image = shirts[switch] 
    
    if(type == 1):
        selected_image = hoodies[switch] 
    
    if(type == 2):
        selected_image = sleeves[switch] 
    
    h, w = selected_image.shape[:2]

    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

    shoulder_width = int(abs(right_shoulder.x * image.shape[1] - left_shoulder.x * image.shape[1]) * scale_factor)
    shirt_height = int(h * (shoulder_width / w))
    resized_image = cv2.resize(selected_image, (shoulder_width, shirt_height), interpolation=cv2.INTER_AREA)

    x = int((left_shoulder.x + right_shoulder.x) / 2 * image.shape[1]) - shoulder_width // 2
    y = int(left_shoulder.y * image.shape[0]) - shirt_height // 2 + y_offset

    for i in range(shirt_height):
        for j in range(shoulder_width):
            if 0 <= y + i < image.shape[0] and 0 <= x + j < image.shape[1]: 
                if resized_image.shape[2] == 4:  
                    alpha = resized_image[i, j, 3] / 255.0
                    if alpha > 0:
                        image[y + i, x + j] = (1 - alpha) * image[y + i, x + j] + alpha * resized_image[i, j, :3]
                else:
                    image[y + i, x + j] = resized_image[i, j]

Allpoints=[]



cap = cv2.VideoCapture(1)

while cap.isOpened():
    success, frame = cap.read()
     

    if not success:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    

    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        overlay_shirt(frame, results.pose_landmarks.landmark)

    cv2.imshow('Shirt Overlay', frame)

    framecnt+=1


    try:
        RGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
       
        results = pose.process(RGB)
            
        image_hight, image_width, _ = frame.shape
        x=(int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x * image_width))
        y=(int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y * image_hight))
        
        Allpoints.append(Point(x,y,1))

        if framecnt%9==0:
              framecnt=0
              result = recognize_gesture(Allpoints)
              print (result)
              if result == 2:
                 if(type == 2):
                    type = 0
                 else :  
                    type += 1
              elif result == 1:
                 if (type == 0):
                    if(len(shirts) == switch):
                        switch = 0
                 elif (type == 1):
                    if(len(hoodies) == switch):
                        switch = 0
                 elif (type == 2):
                    if(len(sleeves) == switch):
                        switch = 0
                 else :  
                    switch += 1
                  

                

              Allpoints.clear()  
        
       
        
    except:
            print ('Camera Error')
    

    if cv2.waitKey(5) & 0xFF == 27:  # Press 'Esc' to exit
        break

cap.release()
cv2.destroyAllWindows()
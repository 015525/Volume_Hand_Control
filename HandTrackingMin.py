import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)

myhands = mp.solutions.hands

hands = myhands.Hands()
mpdraw = mp.solutions.drawing_utils

ctime = 0
ptime = 0

while True:
    success, img = cap.read()

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handlms in results.multi_hand_landmarks:
            for id, lm in enumerate(handlms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if id == 0:
                    cv2.circle(img, (cx, cy), 25, (255, 0, 255), cv2.FILLED)  # 25 is the radius
            mpdraw.draw_landmarks(img, handlms, myhands.HAND_CONNECTIONS)

    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255),
                3)  # first 3 is scale, second is thickness

    cv2.imshow("image", img)
    cv2.waitKey(1)
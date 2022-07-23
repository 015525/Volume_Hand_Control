import cv2
import mediapipe as mp
import time
from HandTrackingModule import HandDetector


cap = cv2.VideoCapture(0)
ctime = 0
ptime = 0
handDetector = HandDetector()
while True:
    success, img = cap.read()
    img = handDetector.findHands(img)
    lmlist = handDetector.find_position(img)
    if len(lmlist) != 0 :
        print(lmlist[4])

    ctime = time.time()
    fps = 1 / (ctime - ptime)
    ptime = ctime

    cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255),
                3)  # first 3 is scale, second is thickness

    cv2.imshow("image", img)
    cv2.waitKey(1)
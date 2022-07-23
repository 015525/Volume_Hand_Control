import time
import numpy as np
import cv2
import HandTrackingModule as hm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

######################
wcam, hcam = 720, 480
######################

cap = cv2.VideoCapture(0)
cap.set(3, wcam)
cap.set(4, hcam)

pTime = 0

detector = hm.HandDetector(max_num_hands=1, min_detection_confidence=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
vol_range = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(-5.0, None)
vol_min, vol_max = vol_range[0], vol_range[1]

while True :
    success, img= cap.read()
    img = detector.findHands(img, draw=False)
    lmlist = detector.find_position(img, draw=False)

    if len(lmlist) > 8 :
        #print(lmlist[4], lmlist[8])

        #x1,y1 =

        x1, x2 = int(lmlist[4][1]), int(lmlist[8][1])
        y1, y2 = int(lmlist[4][2]), int(lmlist[8][2])
        cv2.circle(img, (x1, y1), 10, (255,0,0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255,0,255), 3)

        cx,cy = (x1+x2)//2, (y1+y2)//2
        cv2.circle(img, (cx,cy), 10, (255,0,0),cv2.FILLED)

        length = math.hypot( x2-x1 , y2-y1 )
        #print(length)

        if length < 50 :
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
        elif length > 250 :
            cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

        #another way to get the range
        vol_val = np.interp(length, [50,250], [vol_min, vol_max])

        '''
        vol_val = ((length/250) * (vol_max-vol_min)) + vol_min
        print(vol_val)
        if vol_val>vol_max :
            vol_val=vol_max
        elif vol_val<vol_min :
            vol_val = vol_min

        if length<=50:
            length=0
        '''


        # another way to get the range
        rec_val = np.interp(length, [50,250], [295, 95])
        '''
        rec_val = 295 - ((length/250) * (295-95))
        if rec_val<95 :
            rec_val = 95
        print(rec_val)
        '''


        cv2.rectangle(img, (20,300), (60, 90), (255,0,255), 3)
        cv2.rectangle(img, (25, 295), (55, int(rec_val)), (255, 0, 255), cv2.FILLED)
        volume.SetMasterVolumeLevel(vol_val, None)

        vol_per = np.interp(length, [50,250], [0, 100])
        cv2.putText(img, f'{int(vol_per)} %', (10, 350), cv2.FONT_HERSHEY_PLAIN, 2 , (255, 0, 0), 3)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS : {int(fps)}', (10,50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0),3)
    cv2.imshow("Image",img)
    cv2.waitKey(1)
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
locked = True

rec_val = 295
vol_per = 0

while True :
    success, img= cap.read()
    img = detector.findHands(img, draw=False)
    lmlist = detector.find_position(img, draw=False)

    if len(lmlist) > 8 :
        #print(lmlist[4], lmlist[8])

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



        #lockers
        x1L, y1L = int(lmlist[16][1]), int(lmlist[16][2])
        x2L, y2L = int(lmlist[0][1]), int(lmlist[0][2])
        lock_length = math.hypot(x2L-x1L, y2L-y1L)
        #cv2.circle(img, (x1L, y1L), 10, (255, 0, 0), cv2.FILLED)

        #closure
        x1C, y1C = int(lmlist[10][1]), int(lmlist[10][2])
        close_length = math.hypot(x1 - x1C, y1 - y1C)
        #print(close_length)

        if close_length < 25 :
            break

        #print(lock_length)
        if lock_length < 100 :
            locked = True
            #print(locked)
        else :
            locked  = False

        if not locked :
            # another way to get the range
            rec_val = np.interp(length, [50, 250], [295, 95])
            '''
            rec_val = 295 - ((length/250) * (295-95))
            if rec_val<95 :
                rec_val = 95
            print(rec_val)
            '''
            volume.SetMasterVolumeLevel(vol_val, None)
            vol_per = np.interp(length, [50,250], [0, 100])
            #print(str(vol_val)+" "+str(vol_min)+" "+ str(vol_max))
            #vol_per = 100 - ((vol_val/vol_min) * 100)
            cv2.rectangle(img, (20, 300), (60, 90), (255, 0, 255), 3)
            cv2.rectangle(img, (25, 295), (55,  int(rec_val)), (255, 0, 255), cv2.FILLED)
            cv2.putText(img, f'{int(vol_per)} %', (10, 350), cv2.FONT_HERSHEY_PLAIN, 2 , (255, 0, 0), 3)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS : {int(fps)}', (10,50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0),3)
    cv2.imshow("Image",img)
    ch = cv2.waitKey(1)
    if ch == 27 or ch == ord('q') or ch == ord('Q'):
        break

cap.release()
cv2.destroyAllWindows()
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 17:13:59 2020

@author: Harshwardhan
"""

import cv2
import numpy as np
import imutils
from time import sleep
from collections import deque
from keyboard import press_and_release

def nothing(x):
    pass
 
        
cap = cv2.VideoCapture(0)

#Sleep for 2 seconds to let camera initialize properly.
sleep(2)

cv2.namedWindow("Tuning")
cv2.createTrackbar("H_min", "Tuning", 32, 255, nothing)
cv2.createTrackbar("S_min", "Tuning", 97, 255, nothing)
cv2.createTrackbar("V_min", "Tuning", 0, 255, nothing)
cv2.createTrackbar("H_max", "Tuning", 63, 255, nothing)
cv2.createTrackbar("S_max", "Tuning", 255, 255, nothing)
cv2.createTrackbar("V_max", "Tuning", 255, 255, nothing)

while True:

     _, frame = cap.read()
     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

     l_h = cv2.getTrackbarPos("H_min", "Tuning")
     l_s = cv2.getTrackbarPos("S_min", "Tuning")
     l_v = cv2.getTrackbarPos("V_min", "Tuning")

     u_h = cv2.getTrackbarPos("H_max", "Tuning")
     u_s = cv2.getTrackbarPos("S_max", "Tuning")
     u_v = cv2.getTrackbarPos("V_max", "Tuning")
     
     colour_lower = np.array([l_h, l_s, l_v])
     colour_upper = np.array([u_h, u_s, u_v])
     
     mask = cv2.inRange(hsv, colour_lower, colour_upper)
     
     cv2.imshow("frame", frame)     
     cv2.imshow("mask", mask)
     key = cv2.waitKey(1)
     if key == 27:
         cv2.destroyAllWindows()
         break


pts = deque(maxlen = 20)

#Counts the minimum no. of frames to be detected where direction change occurs
counter = 0
#Change in direction is stored in dX, dY
(dX, dY) = (0, 0)
#Variable to store direction string
direction = ''

sleep(2)

while True:
    _ , frame = cap.read()
    frame = cv2.flip(frame,1)
    frame = imutils.resize(frame, width = 600)
    blurred_frame = cv2.GaussianBlur(frame, (5,5), 0)
    hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv_converted_frame, colour_lower, colour_upper)
    mask = cv2.erode(mask, None, iterations = 2)
    mask = cv2.dilate(mask, None, iterations = 2)

    cnts,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    center = None

    if(len(cnts) > 0):
        c = max(cnts, key = cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        #Proceed only if size is considerable
        if radius > 10:
            #Draw circles around the object as well as its centre
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,255,255), -1)
            pts.appendleft(center)

    for i in range(1, len(pts)):
        if(pts[i-1] == None or pts[i] == None):
            continue

        if counter >= 10 and i == 1 and pts[-10] is not None:
            #Calculate the distance between the current frame and 10th frame before
            dX = pts[-10][0] - pts[i][0]
            dY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ('', '')

            #If distance is greater than 100 pixels, considerable direction change has occured.
            if np.abs(dX) > 100:
                dirX = 'Left' if np.sign(dX) == 1 else 'Right'

            if np.abs(dY) > 80:
                dirY = 'Up' if np.sign(dY) == 1 else 'Down'

            direction = dirX if dirX != '' else dirY

        #Draw a trailing red line to depict motion of the object.
        thickness = int(np.sqrt(20 / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
        

    #Write the detected direction on the frame.
    cv2.putText(frame, direction, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
    if direction != '' :
        press_and_release(direction)

    cv2.imshow('Tracker', frame)
    counter += 1

    if(cv2.waitKey(1) == 27):
        break
cap.release()
cv2.destroyAllWindows()

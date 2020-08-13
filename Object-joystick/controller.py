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



#Used in deque structure to store no. of given buffer points
buffer = 20

#Points deque structure storing 'buffer' no. of object coordinates
pts = deque(maxlen = buffer)

#Counts the minimum no. of frames to be detected where direction change occurs
counter = 0
#Change in direction is stored in dX, dY
(dX, dY) = (0, 0)
#Variable to store direction string
direction = ''

sleep(2)

#Loop until OpenCV window is not closed
while True:
    #Store the readed frame in frame, ret defines return value
    _ , frame = cap.read()
    #Flip the frame to avoid mirroring effect
    frame = cv2.flip(frame,1)
    #Resize the given frame to a 600*600 window
    frame = imutils.resize(frame, width = 600)
    #Blur the frame using Gaussian Filter of kernel size 5, to remove excessivve noise
    blurred_frame = cv2.GaussianBlur(frame, (5,5), 0)
    #Convert the frame to HSV, as HSV allow better segmentation.
    hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)

    #Create a mask for the frame, showing green values
    mask = cv2.inRange(hsv_converted_frame, colour_lower, colour_upper)
    #Erode the masked output to delete small white dots present in the masked image
    mask = cv2.erode(mask, None, iterations = 2)
    #Dilate the resultant image to restore our target
    mask = cv2.dilate(mask, None, iterations = 2)

    #Find all contours in the masked image
    cnts,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #Define center of the ball to be detected as None
    center = None

    #If any object is detected, then only proceed
    if(len(cnts) > 0):
        #Find the contour with maximum area
        c = max(cnts, key = cv2.contourArea)
        #Find the center of the circle, and its radius of the largest detected contour.
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        #Calculate the centroid of the ball, as we need to draw a circle around it.
        M = cv2.moments(c)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        #Proceed only if a ball of considerable size is detected
        if radius > 10:
            #Draw circles around the object as well as its centre
            cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
            cv2.circle(frame, center, 5, (0,255,255), -1)
            #Append the detected object in the frame to pts deque structure
            pts.appendleft(center)

    #Using numpy arange function for better performance. Loop till all detected points
    for i in np.arange(1, len(pts)):
        #If no points are detected, move on.
        if(pts[i-1] == None or pts[i] == None):
            continue

        #If atleast 10 frames have direction change, proceed
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

            #Set direction variable to the detected direction
            direction = dirX if dirX != '' else dirY

        #Draw a trailing red line to depict motion of the object.
        thickness = int(np.sqrt(buffer / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
        

    #Write the detected direction on the frame.
    cv2.putText(frame, direction, (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)
    if direction != '' :
        press_and_release(direction)

    #Show the output frame.
    cv2.imshow('Window- Direction Detection', frame)
    key = cv2.waitKey(1) & 0xFF
    #Update counter as the direction change has been detected.
    counter += 1

    #If q is pressed, close the window
    if(key == 27):
        break
#After all the processing, release webcam and destroy all windows
cap.release()
cv2.destroyAllWindows()
import numpy as np
import cv2
import time

# 初始化摄像头
cap = cv2.VideoCapture(0)
cv2.namedWindow('0', cv2.WINDOW_NORMAL)
cv2.resizeWindow('0', 300, 300)

c_points = []

def init(seconds):
    start_time = time.time()
    while True:
        current_time = time.time()
        if current_time - start_time > seconds:
            break
        ret, img = cap.read()
        img = img[140:450, 250:640]
        cv2.rectangle(img, (105, 59), (285, 239), (0, 255, 0), 2)
        for i in range(3):
            for j in range(3):
                cv2.circle(img, (134 + j * 62, 88 + i * 62), 5, (0, 0, 255), -1)
                c_points.append([134 + j * 62, 88 + i * 62])
        cv2.imshow('0', img)
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break

while (True):
    ret, img = cap.read()
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    upper_blue = np.array([0, 43, 46])
    lower_blue = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
        # 找最大轮廓，提取质心
    cv2.imshow('1', mask)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    center = None
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        cv2.circle(img, (center[0],center[1]), 8, (0,0,255), 3)
        print("cent_x=",center[0])
        print("cent_y=",640-center[1])
    cv2.imshow('0', img)
    if cv2.waitKey(1) & 0xFF == ord('x'):
            break
    
import numpy as np
import cv2
import time
import serial
cv2.namedWindow('0', cv2.WINDOW_NORMAL)
cv2.resizeWindow('0',600,600)
cap = cv2.VideoCapture(0)
c_points = []
black_points = []
white_points = []
def init(seconds):
    start_time = time.time()
    while(True):
        current_time = time.time()
        if current_time - start_time > seconds:
            break
        ret, img = cap.read()  #read camera
        img = img[140:450, 250:640]
        cv2.rectangle(img, (105,59), (285,239), (0,255,0), 2)
        cv2.line(img, (68,158), (68,474), (0,255,0), 3)
        cv2.line(img, (28,158), (28,474), (0,255,0), 3)
        cv2.line(img, (323,158), (323,474), (0,255,0), 3)
        cv2.line(img, (363,158), (363,474), (0,255,0), 3)
        for i in range(5):
            cv2.circle(img, (48,20+70*i), 3, (0,0,255), 3)
            black_points.append([48, 20+70*i])
            cv2.circle(img, (343,20+70*i), 3, (0,0,255), 3)
            white_points.append([343, 20+70*i])
        for i in range(3):
            for j in range(3):
                cv2.circle(img, \
                        (134+j*62, 88+i*62), \
                        5, (0, 0, 255), -1)
                c_points.append([134+j*62, 88+i*62]  )
                cv2.imshow('0', img)
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break

init(10)

"-------------UART-------------"
port = '/dev/ttyAMA0'   # 串口设备路径
baudrate = 115200         # 波特率
ser = serial.Serial(port, baudrate)
start=bytearray([0xDD])
over=bytearray([0xEE])
def send_data(data):
    data_1 = data[0]
    data_2 = data[1]
    data = bytearray([data_1, data_2])
    if ser.isOpen():
        ser.write(start)
        ser.write(data)
        print(data)
        ser.write(over)
    else:
        print("Communication Error")
"------------------------------------"
"------------CLICK AND SEND----------------"
cnt = 0
position = None
rout = [0] * 2
def mouse(event, x, y, flags, param):
    global position, cnt, rout
    img = param
    if event == cv2.EVENT_LBUTTONDOWN:
        if cnt % 2 == 1:
            for i in range(9):
                c_x = c_points[i][0]
                c_y = c_points[i][1]
                if abs(x - c_x) < 20 and abs(y - c_y) < 20:
                    position = (c_x, c_y, i)
                    break
            if position:
                rout[1] = i + 1
                print(rout)

                send_data(rout)
                rout = [0] * 2
        else:
            if x < 55:
                for j in range(5):
                    if abs(black_points[j][1] - y) < 10:
                        print([2, j]) #[black, num]
                        break
                rout[0] = j + 10
            elif x > 330:
                for j in range(5):
                    if abs(white_points[j][1] - y) < 10:
                        print([1, j]) #[white, num]
                        break
                rout[0] = j + 15

        cnt += 1
"--------------------------------"
while(True):
    ret, img = cap.read()
    img = img[140:450, 250:640]
    for i in range(5):
        cv2.circle(img, (48,20+70*i), 3, (0,0,255), 3)
        cv2.circle(img, (343,20+70*i), 3, (0,0,255), 3)
    cv2.setMouseCallback('0', mouse, img)
    cv2.imshow('0', img)
    if cv2.waitKey(1) & 0xFF == ord('x'):
            break
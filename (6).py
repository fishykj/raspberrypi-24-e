import numpy as np
import cv2
import time
import serial

def nothing(*arg):
    pass

cv2.namedWindow('0', cv2.WINDOW_NORMAL)
cv2.resizeWindow('0', 300, 300)
cv2.namedWindow('black', cv2.WINDOW_NORMAL)
cv2.resizeWindow('black', 300, 300)
cv2.namedWindow('white', cv2.WINDOW_NORMAL)
cv2.resizeWindow('white', 300, 300)
cv2.createTrackbar('b_min', 'black', 38, 255, nothing)
cv2.createTrackbar('b_max', 'black', 255, 255, nothing)
cv2.createTrackbar('w_min', 'white', 186, 255, nothing)
cv2.createTrackbar('w_max', 'white', 255, 255, nothing)

cap = cv2.VideoCapture(0)
cv2.namedWindow('0', cv2.WINDOW_NORMAL)
cv2.resizeWindow('0', 300, 300)

c_points = []
black_points = []
white_points = []
cnt_white = 0
cnt_black = 0
def init(seconds):
    start_time = time.time()
    while True:
        current_time = time.time()
        if current_time - start_time > seconds:
            break
        ret, img = cap.read()
        img = img[140:450, 250:640]
        cv2.rectangle(img, (105, 59), (285, 239), (0, 255, 0), 2)
        cv2.line(img, (68,0), (68,474), (0,255,0), 3)
        cv2.line(img, (28,0), (28,474), (0,255,0), 3)
        cv2.line(img, (323,0), (323,474), (0,255,0), 3)
        cv2.line(img, (363,0), (363,474), (0,255,0), 3)
        for i in range(5):
            cv2.circle(img, (48,20+70*i), 3, (0,0,255), 3)
            black_points.append([48, 20+70*i])
            cv2.circle(img, (343,20+70*i), 3, (0,0,255), 3)
            white_points.append([343, 20+70*i])
        for i in range(3):
            for j in range(3):
                cv2.circle(img, (134 + j * 62, 88 + i * 62), 5, (0, 0, 255), -1)
                c_points.append([134 + j * 62, 88 + i * 62])
        cv2.imshow('0', img)
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break

init(5)
def mouse_white(event, x, y, flags, param):
    global cnt_white
    if event == cv2.EVENT_LBUTTONDOWN:
        if cnt_white >= 40:
            cnt_white = 0
        else:
            cnt_white += 2
def mouse_black(event, x, y, flags, param):
    global cnt_black
    if event == cv2.EVENT_LBUTTONDOWN:
        if cnt_black >= 40:
            cnt_black = 0
        else:
            cnt_black += 2

port = '/dev/ttyAMA0'   # 串口设备路径
baudrate = 115200         # 波特率
ser = serial.Serial(port, baudrate, timeout=1)
def receive_data(data_byte):
    start_time = time.time()
    data = None
    while time.time() - start_time < 0.05:
        if ser.in_waiting >= data_byte:
            data = ser.read(data_byte)
    if data:
        hex_data = data.hex()
        return hex_data
    else:
        return False
last = []
current = []
while True:
    flag = 0
    ret, img = cap.read()
    img = img[120:470, 250:640]
    board = [0 for _ in range(9)]
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = cv2.medianBlur(img_gray, 5)

    b_min = cv2.getTrackbarPos('b_min', 'black')
    b_max = cv2.getTrackbarPos('b_max', 'black')
    w_min = cv2.getTrackbarPos('w_min', 'white')
    w_max = cv2.getTrackbarPos('w_max', 'white')
    # 白色二值化
    _, img_thresh_white = cv2.threshold(img_gray, \
    w_min, w_max, cv2.THRESH_BINARY)

    # 黑色二值化
    _, img_thresh_black = cv2.threshold(img_gray, \
    b_min, b_max, cv2.THRESH_BINARY)

    cv2.imshow('white', img_thresh_white)
    cv2.imshow('black', img_thresh_black)
    cv2.imshow('0', img)
    radius = 5  # 半径
    #board
    for i in range(9):
        x = c_points[i][0]
        y = c_points[i][1]
        is_white = False
        is_black = False
        for dx in range(-radius, radius+1):
            for dy in range(-radius, radius+1):
                if 0 <= y + dy < img_thresh_white.shape[0] and \
                0 <= x + dx < img_thresh_white.shape[1]:
                    if img_thresh_white[y + dy, x + dx] == 255:
                        is_white = True
                    if img_thresh_black[y + dy, x + dx] == 0:
                        is_black = True
        if is_white:
            board[i] = 1
        if is_black:
            board[i] = 2
    #print(board)
    if receive_data(1):
        print(receive_data(1))
        if len(current) == 0:
            current = board.copy()
            print(current)
        else:
            last = current.copy()
            current = board.copy()
            if last.count(0) == current.count(0):
                for i in range(9):
                    if last[i] != 0 and current[i] == 0:
                        former = i
                    elif last[i] == 0 and current[i] != 0:
                        latter = i
                print("from" + str(former) + "to" + str(latter))

    print(last)
    print(current)
    cv2.imshow('0', img)

    if cv2.waitKey(1) & 0xFF == ord('x'):
        break

cap.release()
cv2.destroyAllWindows()
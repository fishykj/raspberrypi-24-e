import numpy as np
import cv2
import time
import serial
import math
def nothing(*arg):
    pass
cv2.namedWindow('0', cv2.WINDOW_NORMAL)
cv2.resizeWindow('0', 300, 300)
cv2.namedWindow('black', cv2.WINDOW_NORMAL)
cv2.resizeWindow('black', 300, 300)
cv2.namedWindow('white', cv2.WINDOW_NORMAL)
cv2.resizeWindow('white', 300, 300)
cv2.createTrackbar('b_min', 'black', 66, 255, nothing)
cv2.createTrackbar('b_max', 'black', 255, 255, nothing)
cv2.createTrackbar('w_min', 'white', 175, 255, nothing)
cv2.createTrackbar('w_max', 'white', 255, 255, nothing)

cap = cv2.VideoCapture(0)
cv2.namedWindow('0', cv2.WINDOW_NORMAL)
cv2.resizeWindow('0', 300, 300)

c_points = []
black_points = []
white_points = []
def init(seconds):
    start_time = time.time()
    while True:
        current_time = time.time()
        if current_time - start_time > seconds:
            break
        ret, img = cap.read()
        img = img[140:450, 250:640]
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

init(3)
flag = 0
"--------------CALCULATE--------------"
def evaluate(board):
    global flag
    # 评估当前棋盘状态
    for row in board:
        if row[0] == row[1] == row[2]:
            if row[0] == 2:
                return 10
            elif row[0] == 1:
                return -10
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col]:
            if board[0][col] == 2:
                return 10
            elif board[0][col] == 1:
                return -10
    if board[0][0] == board[1][1] == board[2][2]:
        if board[0][0] == 2:
            return 10
        elif board[0][0] == 1:
            return -10
    if board[0][2] == board[1][1] == board[2][0]:
        if board[0][2] == 2:
            return 10
        elif board[0][2] == 1:
            return -10
    return 0
def is_moves_left(board):
    for row in board:
        if 0 in row:
            return True
    return False
def minimax(board, depth, is_max, alpha, beta):
    score = evaluate(board)
    if score == 10:
        return score - depth
    if score == -10:
        return score + depth
    if not is_moves_left(board):
        return 0
    if is_max:
        best = -math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    board[i][j] = 2
                    best = max(best, minimax(board, depth + 1, not is_max, alpha, beta))
                    board[i][j] = 0
                    alpha = max(alpha, best)
                    if beta <= alpha:
                        break
        return best
    else:
        best = math.inf
        for i in range(3):
            for j in range(3):
                if board[i][j] == 0:
                    board[i][j] = 1
                    best = min(best, minimax(board, depth + 1, not is_max, alpha, beta))
                    board[i][j] = 0
                    beta = min(beta, best)
                    if beta <= alpha:
                        break
        return best
def find_best_move(board):
    global flag, cnt
    best_val = -math.inf
    best_move = (-1, -1)
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                board[i][j] = 2
                move_val = minimax(board, 0, False, -math.inf, math.inf)
                board[i][j] = 0
                if move_val > best_val:
                    best_move = (i, j)
                    best_val = move_val
    h = best_move[0]
    l = best_move[1]
    print(flag)
    if flag == 0:
        send_data([cnt//2+10, h*3+l+1])
    else:
        cnt -= 2
        send_data([cnt//2+10, h*3+l+1])
        flag = 0
    return best_move
"---------------------------------------"

"------------------UART----------------"
port = '/dev/ttyAMA0'   # 串口设备路径
baudrate = 115200         # 波特率
ser = serial.Serial(port, baudrate, timeout=1)
start=bytearray([0xDD])
over=bytearray([0xEE])
cnt = 0
def send_data(data):
    global cnt
    print(cnt)
    data_1 = data[0]
    data_2 = data[1]
    data = bytearray([data_1, data_2])

    if ser.isOpen() and cnt % 2 == 1 and cnt != 0:
        ser.write(start)
        ser.write(data)
        ser.write(over)
        print(data)
    elif ser.isOpen() and cnt == 0:
        print("send data ok")
        ser.write(start)
        ser.write(bytearray([10, 5]))
        ser.write(over)

def receive_data(data_byte):
    global cnt
    start_time = time.time()
    data = None
    while time.time() - start_time < 0.02:
        if ser.in_waiting >= data_byte:
            data = ser.read(data_byte)
            print(data)
    if data == b'\xaa':
        cnt += 1
        print("receive data ok")
        hex_data = data.hex()
        return hex_data
    else:
        return False
"---------------------------------"

last = []
current = []
step = 0
flag = 0
while True:
    #flag = 0
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
    radius = 5
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
    if receive_data(1) and cnt != 0:
        if len(current) == 0:
            current = board.copy()
            print(current)
        else:
            last = current.copy()
            current = board.copy()
            print(last)
            print(current)
        if last.count(0) == current.count(0):

            former = latter = None
            for i in range(9):
                if last[i] != 0 and current[i] == 0:
                    former = i
                elif last[i] == 0 and current[i] != 0:
                    latter = i
            if former != None and latter != None:
                print("from" + str(former) + "to" + str(latter))
                send_data([latter+1, former+1])
                flag = 1
        else:
            board = []
            for i in range(3):
                board.append(current[3*i: 3*i+3])
            print(board)
            best_move = find_best_move(board)
            print("The best move is:", best_move)
    elif cnt == 0:
        send_data([10, 5])
        cnt += 1
    cv2.imshow('0', img)
    if cv2.waitKey(1) & 0xFF == ord('x'):
        break
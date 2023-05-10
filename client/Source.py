# Client

from socket import *
import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

def Connect(PORT):
    server= socket(AF_INET,SOCK_STREAM)
    server.connect(('172.20.10.9',PORT))
    return server

def T_Thread(server,Online):
    cam = cv2.VideoCapture(0)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 99]
    while True:
        status,frame=cam.read()
        _, frame = cv2.imencode('.jpg', frame, encode_param)
        frame = np.array(frame)
        stringData = frame.tobytes()
        server.sendall((str(len(stringData))).encode().ljust(16) + stringData)
        
        if not Online.empty():
            online = Online.get()
            if online == 1:
                print('Paused')
                while True:
                    if Online.get() == 1:
                        print('Resume')
                        break
            elif online == 0:      
                print('break')
                break
            
def R_Thread(server,Q,Online):
    while True:
        data = server.recv(8)
        Data = int.from_bytes(data,byteorder='little')
        
        if Data == 0:
            Online.put(0)
            break
        elif Data == 1:
            BUZZER()

def BUZZER():
    print("Beep Beep")
    buzzer=18
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(buzzer,GPIO.OUT)
    GPIO.setwarnings(False)
    
    pwm=GPIO.PWM(buzzer,262)
    pwm.start(50.0)
    time.sleep(1.5)
    
    pwm.stop()
    GPIO.cleanup()
    


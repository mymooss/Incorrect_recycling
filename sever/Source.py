# Server

from socket import *
import cv2
import numpy as np
import os
import torch      

global Server , client
Server = None
client = None

def Create(PORT):
    global Server
    Server = socket(AF_INET,SOCK_STREAM)
    Server.bind(('',PORT))
    Server.listen(2)
    
def Accept():
    global Server , client
    client, addr = Server.accept()
    return client

def recvall(sock, count):
	buf = b''
	while count:
		newbuf = sock.recv(count)
		if not newbuf :
			return None
		buf += newbuf
		count -= len(newbuf)
	return buf

def R_Thread(client,Q,Online):
    model = torch.hub.load('ultralytics/yolov5','custom', path='C:/Users/subeen/Desktop/doge/yolov5/runs/train/exp2/weights/best.pt', force_reload=True)
    class_names = model.names

    frameWidth = 480
    frameHeight = 320
    val=1
    
    while True:
        length = recvall(client, 16)
        stringData = recvall(client, int(length))
        data = np.frombuffer(stringData, dtype='uint8')
        frame = cv2.imdecode(data, cv2.IMREAD_COLOR)
        img = cv2.resize(frame, (frameWidth, frameHeight))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        results = model([img_rgb], size=256)
        
        frameWidth = 480
        frameHeight = 320
        
        bboxes = results.xyxy[0].numpy()  
        for bbox in bboxes:
            box, score, cl = bbox[:4], bbox[4], int(bbox[5])
            x1, y1, x2, y2 = box
            top = max(0, int(y1))
            left = max(0, int(x1))
            right = min(img.shape[1], int(x2))
            bottom = min(img.shape[0], int(y2))
            if bbox[4]>=0.56: 
                cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(img, '{0} {1:.2f}'.format(class_names[cl], score), 
                            (left, top - 12),cv2.FONT_HERSHEY_SIMPLEX,0.6, (0, 255, 0), 1, cv2.LINE_AA)
                if bbox[3]>(frameHeight/2) and 0<bbox[2]<((frameWidth/3)-3):
                    if not bbox[5] == 0:
                        print("캔이 아님")
                        client.send(val.to_bytes(2,byteorder='little'))

                if bbox[3]>(frameHeight/2) and ((frameWidth/3)+3)<bbox[2]<((frameWidth/3)*2-3):
                    if not bbox[5] == 1:
                        print("유리가 아님")
                        client.send(val.to_bytes(2,byteorder='little'))

                if bbox[3]>(frameHeight/2) and ((frameWidth/3)*2+3)<bbox[2]<frameWidth:
                    if not bbox[5] == 2:
                        print("플라스틱이 아님")
                        client.send(val.to_bytes(2,byteorder='little'))
                        
                print(bbox)
        
        
        cv2.imshow('RecivedFrame', img)
        Q.put(img)
        #self.FrameQ.put(frame)
        cv2.waitKey(1)
        
        if not Online.empty():
            print('Server_R_Thread_OFF')
            break


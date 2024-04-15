import serial
from threading import Thread 
import cv2
import time
test = False  
  
# A thread that produces data 
def producer(): 
    print('Start thread 1')
    ser = serial.Serial('/dev/ttyUSB1',baudrate=9600)
    global test
    for i in range(10):
        for k in [0,90,180]:
            command(ser,k)
            time.sleep(3)
    
    test = True
    print("test= ",test)
    print("Complete 1")
    
def command(ser, angle: int):
    ser.write(f'{angle}\r'.encode('utf-8'))

          
# A thread that consumes data 
def consumer(cap: cv2.VideoCapture): 
    print('Start thread 2')
    
    global test
    k=0
    while True: 
        k+=1
        ret,frame = cap.read()
        cv2.imwrite(str(k)+'.jpg', img=frame)
        if test == True:
            break
        time.sleep(0.01)
    
    test = False
    print("test= ",test)
    print("Complete 2")
    
cap = cv2.VideoCapture(3)
t1 = Thread(target = consumer,args=(cap,)) 
t2 = Thread(target = producer) 
t1.start() 
t2.start()

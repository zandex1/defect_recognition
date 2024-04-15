from threading import Thread 
import cv2
import time
test = False  
  
# A thread that produces data 
def producer(): 
    global test
    for i in range(100):
        time.sleep(0.5)
    
    test = True
    print("test= ",test)
    print("Complete 1")
    
          
# A thread that consumes data 
def consumer(cap: cv2.VideoCapture): 
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
    
cap = cv2.VideoCapture(0)
t1 = Thread(target = consumer,args=(cap,)) 
t2 = Thread(target = producer) 
t1.start() 
t2.start() 
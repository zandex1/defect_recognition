import cv2

def create_camera():
    global cap
    cap = cv2.VideoCapture(0)
    
def get_cap():
    global cap
    return cap
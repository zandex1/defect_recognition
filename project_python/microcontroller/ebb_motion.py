import numpy as np
import time
import ebb_serial_my as ebb_serial_my
import cv2 as cv
import sys

def doABMove(port_name, delta_a, delta_b, duration):
    """
    Issue command to move A/B axes as: "XM,<move_duration>,<axisA>,<axisB><CR>".\n
    Then, <Axis1> moves by <AxisA> + <AxisB>, and <Axis2> as <AxisA> - <AxisB>
    """
    if port_name is not None:
        str_output = 'XM,{0},{1},{2}\r'.format(duration, delta_a, delta_b)
        ebb_serial_my.command(port_name, str_output)

def my_pos(port_name):
    result = ebb_serial_my.usb_query('QS\r') # Query global step position
    result_list = result.strip().split(",")
    a_pos, b_pos = int(result_list[0]), int(result_list[1])

    x_pos_inch = (a_pos + b_pos) / (4 * ebb_serial_my.params.native_res_factor)
    y_pos_inch = (a_pos - b_pos) / (4 * ebb_serial_my.params.native_res_factor)
    if ebb_serial_my.options.resolution == 2:  # Low-resolution mode
        x_pos_inch *= 2
        y_pos_inch *= 2

    x_pos_mm = x_pos_inch * 25.4
    y_pos_mm = y_pos_inch * 25.4

    print(f"{x_pos_mm:0.3f}, {y_pos_mm:0.3f}")

def doTimedPause(port_name, n_pause):
    if port_name is not None:
        while n_pause > 0:
            if n_pause > 750:
                td = 750
            else:
                td = n_pause
                if td < 1:
                    td = 1  # don't allow zero-time moves
            ebb_serial_my.command(port_name, 'SM,{0},0,0\r'.format(td))
            n_pause -= td

def QueryPRGButton(port_name):
    if port_name is not None:
        return ebb_serial_my.query(port_name, 'QB\r')

def sendDisableMotors(port_name):
    if port_name is not None:
        ebb_serial_my.command(port_name, 'EM,0,0\r')

def sendEnableMotors(port_name, res):
    if res < 0:
        res = 0
    if res > 5:
        res = 5
    if port_name is not None:
        ebb_serial_my.command(port_name, 'EM,{0},{0}\r'.format(res))
        # If res == 0, -> Motor disabled
        # If res == 1, -> 16X microstepping
        # If res == 2, -> 8X microstepping
        # If res == 3, -> 4X microstepping
        # If res == 4, -> 2X microstepping
        # If res == 5, -> No microstepping

def PBOutConfig(port_name, pin, state):
    # Enable an I/O pin. Pin: {0,1,2, or 3}. State: {0 or 1}.
    # Note that B0 is used as an alternate pause button input.
    # Note that B1 is used as the pen-lift servo motor output.
    # Note that B3 is used as the EggBot engraver output.
    # For use with a laser (or similar implement), pin 3 is recommended

    if port_name is not None:
        # Set initial Bx pin value, high or low:
        str_output = 'PO,B,{0},{1}\r'.format(pin, state)
        ebb_serial_my.command(port_name, str_output)
        # Configure I/O pin Bx as an output
        str_output = 'PD,B,{0},0\r'.format(pin)
        ebb_serial_my.command(port_name, str_output)

def PBOutValue(port_name, pin, state):
    # Set state of the I/O pin. Pin: {0,1,2, or 3}. State: {0 or 1}.
    # Set the pin as an output with OutputPinBConfigure before using this.
    if port_name is not None:
        str_output = 'PO,B,{0},{1}\r'.format(pin, state)
        ebb_serial_my.command(port_name, str_output)

def queryVoltage(port_name):
    # Query the EBB motor power supply input voltage.
    if port_name is not None:
        version_status = ebb_serial_my.min_version(port_name, "2.2.3")
        if not version_status:
            return True # Unable to read version, or version is below 2.2.3.
                        # In these cases, issue no voltage warning.
        else:
            raw_string = (ebb_serial_my.query(port_name, 'QC\r'))
            split_string = raw_string.split(",", 1)
            split_len = len(split_string)
            if split_len > 1:
                voltage_value = int(split_string[1])  # Pick second value only
            else:
                return True  # We haven't received a reasonable voltage string response.
                # Ignore voltage test and return.
            # Typical reading is about 300, for 9 V input.
            if voltage_value < 250:
                return False
    return True

def limit_stop_y(ser): 
          
        global flag_limit_Y     
          
        a=ebb_serial_my.query(ser,"PI,C,6\r") # read pin PC6    
       
        try:       
         #print(a) 
         if  int(a[3]):
              flag_limit_Y=True           
          #return int(a[3])     
        except:    
           flag_limit_X=False
           flag_limit_Y=False
    
           #ser = ebb_serial_my.testPort("COM15")
           #sendEnableMotors(ser,0)
           #limit_stop_btn_config(ser)
           #heatup_moves(ser) 
           print ("ERROR Y")           
           return 0      
                
def limit_stop_x(ser): 
        global flag_limit_X
        
        b=ebb_serial_my.query(ser,"PI,A,2\r") # read pin PD4
        try:        
        
            #return int(b[3])     
            if  int(b[3]):
                flag_limit_X=True         
        except:
           
           #ser = ebb_serial_my.testPort("COM15")
           #sendEnableMotors(ser,0)
           #limit_stop_btn_config(ser)
           #heatup_moves(ser) 
           print ("ERROR X")
           return 0

def limit_stop_btn_config(ser):
        ebb_serial_my.query(ser,"PD,C,6,1\r") # config pin PC6 as input
        ebb_serial_my.query(ser,"PD,A,2,1\r") # config pin PC7 as input
        
def state_ZERO_XY(ser,pen_up_delay_ms):   #поднять палец и отправить в HOME      
              global flag_limit_Y     
              global flag_limit_X
              #sendPenUp(ser, pen_up_delay_ms)
              
              while (flag_limit_Y==False) :
                 limit_stop_y(ser)
                 #print("flag_limit_Y=",flag_limit_Y) 
                 doABMove(ser,-30,0,15)
              
              while (flag_limit_Y==True)  and (flag_limit_X==False) :
                 limit_stop_x(ser)
                 #print("flag_limit_X=",flag_limit_X) 
                 doABMove(ser,0,-30,15)
              
              flag_limit_X=False
              flag_limit_Y=False 
              doTimedPause(ser,300)

def reset_controller():
     print (ebb_serial_my.query(ser,"CS\r"))
     # print (ebb_serial_my.query(ser,"R\r")) 
     # sendEnableMotors(ser,1)
      #limit_stop_btn_config(ser)                                 
       
def ebb_stop():
     ebb_serial_my.query(ser,"ES\r")
     
def ebb_clear():
     ebb_serial_my.query(ser,"CS\r")     
     
def ebb_reset():
     print(ebb_serial_my.query(ser,"R\r"))  

def long_pause(seconds):
    for i in range(seconds*2):
          doTimedPause(ser,500)        

def grid_prepare(ser,X_len,Y_len, X_grid,Y_grid,hor_vert):

   number_of_image=1
   cap = cv.VideoCapture("/dev/video2")
   cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
   cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
   #long_pause(5)
   basename = "img"
   d_x=0
   d_y=0
   global arr_out
   global flag_touch_push
   #my_pos(ser)
   
   heatup_moves(ser)   
   long_pause(1)        
   state_ZERO_XY(ser,100) 
   
   #pmf_state_Zero(ser)
   long_pause(1)
   i=0
   
   d_x1=0
   d_y1=0
   d_y2=0
   d_x2=0
   
   X_stp = X_len/X_grid                      
   Y_stp = Y_len/Y_grid
   arr=[[[0, 0]] * X_grid for i in range(Y_grid)]
   
   for y in range(Y_grid):     
       for x in range(X_grid):
           a= int((x*X_stp)+(X_stp/2))
           b =int((y*Y_stp)+(Y_stp/2))
           arr[y][x] = [a,b]
   print (arr)
  
   if hor_vert==1: 
        arr = np.rot90(arr, 1)   #rotating
        arr = arr[::-1]
   
   for x in range(1,Y_grid,2):  #переворот строки через строку (змейка)
       arr[x]=arr[x][::-1]

   #print(arr)
   #print("________")
   
   arr_out=[[0,0]]*(X_grid*Y_grid)
   arr_out=sum(arr,[])
  
   #print (arr_out)      
   start_x=0
   start_y=0
   delta_x=X_len/X_grid
   delta_y=Y_len/Y_grid
   
   for x in range(0,Y_grid):
       
       if x != 0:
          start_x=start_x+delta_x
       else:
            start_x=0

       for y in range(0,X_grid):
           
           d_x1=arr[x][y][0]
           d_y1=arr[x][y][1]
           
           d_x=d_x1-d_x2
           d_y=d_y1-d_y2
          
           print(d_x,d_y)
           
           doABMove(ser,d_y,d_x,500)
          
           #cv.imshow('frame', frame)
           doTimedPause(ser,500)

           if not cap.isOpened():
                    sys.exit("Cannot open camera")
           ret, frame = cap.read()
           if not ret:
                    sys.exit("Cannot receive frame")
                    break
                
           cv.imshow('frame', frame)
           writeStatus = cv.imwrite(str(start_x)+"_"+str(start_y) + ".jpg", img=frame)
           if writeStatus is True:
                 print("image written")
           else:
                sys.exit("Cannot save frame")

           ##doTimedPause(ser,50)
        
           number_of_image = number_of_image + 1
           if x ==0 or x%2==0:
            start_y= start_y+delta_y
           else:
            start_y= start_y-delta_y
         
           #cv.destroyAllWindows()
           #doTimedPause(ser,50)
           d_x2=d_x1
           d_y2=d_y1
       if x == 0 or x%2==0:
         start_y=Y_len-delta_y
       if x!=0 and x%2!=0:
         start_y = 0
       #print(start_x,start_y)

   state_ZERO_XY(ser,100)
   print("Scaning finish succsefully")

def main1(ser):

   X_len=input()
   X_len=int(X_len)
   Y_len=input()
   Y_len=int(Y_len)
   X_grid=input()
   X_grid=int(X_grid)
   Y_grid=input()
   Y_grid=int(Y_grid)
   hor_vert=input() # Поворот на 90 градусов
   hor_vert=int(hor_vert)
   grid_prepare(ser,X_len,Y_len,X_grid,Y_grid,hor_vert)

def heatup_moves(ser):
   
    MAX_SPEED = 25000  # steps/s
       
    DY = 1620*6
    DX = 2120*6
    DT = 4000
    dist = max(DX, DY)
    speed = int(dist * 1000 / DT)
    assert speed < MAX_SPEED, 'Too fast!'
    time.sleep(1)
    
    sendEnableMotors(ser,   1)

if __name__ == "__main__":
   
   arr_out =[]  

   flag_touch_push=False
   flag_limit_X=False
   flag_limit_Y=False   
   ser = ebb_serial_my.testPort("/dev/ttyACM0")
   sendEnableMotors(ser,   1)
   print(ser)
   if ser:
       main1(ser)
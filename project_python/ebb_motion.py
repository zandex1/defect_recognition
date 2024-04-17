#import rs
import threading
import numpy as np
import math
import time
import ebb_serial_my as ebb_serial_my
import cv2 as cv
import collections as coll
import binascii
import copy
import sys

def doABMove(port_name, delta_a, delta_b, duration):
    # Issue command to move A/B axes as: "XM,<move_duration>,<axisA>,<axisB><CR>"
    # Then, <Axis1> moves by <AxisA> + <AxisB>, and <Axis2> as <AxisA> - <AxisB>
    
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


def doLowLevelMove(port_name, ri1, steps1, delta_r1, ri2, steps2, delta_r2):
    # A "pre-computed" XY movement of the form
    #  "LM,RateTerm1,AxisSteps1,DeltaR1,RateTerm2,AxisSteps2,DeltaR2<CR>"
    # See http://evil-mad.github.io/EggBot/ebb.html#LM for documentation.
    # Important: Requires firmware version 2.5.1 or higher.
    if port_name is not None:
        if ((ri1 == 0 and delta_r1 == 0) or steps1 == 0) and ((ri2 == 0 and delta_r2 == 0) or steps2 == 0):
            return
        str_output = 'LM,{0},{1},{2},{3},{4},{5}\r'.format(ri1, steps1, delta_r1, ri2, steps2, delta_r2)
        ebb_serial_my.command(port_name, str_output)


def doXYMove(port_name, delta_x, delta_y, duration):
    # duration is an integer in the range from 1 to 16777215, giving time in milliseconds
    # delta_x and delta_y are integers, each in the range from -16777215 to 16777215, giving movement distance in steps
    # The minimum speed at which the EBB can generate steps for each motor is 1.31 steps/second. The maximum
    # speed is 25,000 steps/second.
    # Move X/Y axes as: "SM,<move_duration>,<axis1>,<axis2><CR>"
    # Typically, this is wired up such that axis 1 is the Y axis and axis 2 is the X axis of motion.
    # On EggBot, Axis 1 is the "pen" motor, and Axis 2 is the "egg" motor.
    if port_name is not None:
        str_output = 'SM,{0},{1},{2}\r'.format(duration,delta_y,delta_x)
        ebb_serial_my.command(port_name, str_output)


def moveDistLM(rin, delta_rin, time_ticks):
    # Calculate the number of motor steps taken using the LM command,
    # with rate factor r, delta factor delta_r, and in a given number
    # of 40 us time_ticks. Calculation is for one axis only.

    # Distance moved after n time ticks is given by (n * r + (n^2 - n)*delta_r/2) / 2^31

    n = int(time_ticks)  # Ensure that the inputs are integral.
    r = int(rin)
    delta_r = int(delta_rin)

    if n == 0:
        return 0
    else:
        np = (n * n - n) >> 1  # (n^2 - n)/2 is always an integer.
        s = (n * r) + delta_r * np
        s = s >> 31
        return s


def moveTimeLM(ri, steps, delta_r):
    # Calculate how long, in 40 us ISR intervals, the LM command will take to move one axis.

    # First: Distance in steps moved after n time ticks is given by
    #  the formula: distance(time n) = (10 * r + (n^2 - n)*delta_r/2) / 2^31.
    # Use the quadratic formula to solve for possible values of n,
    # the number of time ticks needed to travel the through distance of steps.
    # As this is a floating point result, we will round down the output, and
    # then move one time step forward until we find the result.

    r = float(ri)
    d = float(delta_r)
    steps = abs(steps)  # Distance to move is absolute value of steps.

    if steps == 0:
        return 0  # No steps to take, so takes zero time.

    if delta_r == 0:
        if ri == 0:
            return 0  # No move will be made if ri and delta_r are both zero.

        # Else, case of no acceleration.
        # Simple to get actual movement time:
        # T (seconds) = (AxisSteps << 31)/(25 kHz * RateTerm)

        f = int(steps) << 31
        t = f / r
        t2 = int(math.ceil(t))
        return t2
    else:
        factor1 = (d / 2.0) - r
        factor2 = r * r - d * r + (d * d / 4.0) + (2 * d * 2147483648.0 * steps)

        if factor2 < 0:
            factor2 = 0
        factor2 = math.sqrt(factor2)
        root1 = int(math.floor((factor1 + factor2) / d))
        root2 = int(math.floor((factor1 - factor2) / d))

    if root1 < 0 and root2 < 0:
        return -1  # No plausible roots -- movement time must be greater than zero.

    if root1 < 0:
        time_ticks = root2  # Pick the positive root
    elif root2 < 0:
        time_ticks = root1  # Pick the positive root
    elif root2 < root1:  # If both are valid, pick the smaller value.
        time_ticks = root2
    else:
        time_ticks = root1

    # Now that we have an floor estimate for the time:
    # calculate how many steps occur in the estimated time.
    # Then, using that head start, calculate the
    # exact number of time ticks needed.

    dist = 0
    continue_loop = True
    while continue_loop:
        time_ticks += 1

        dist = moveDistLM(ri, delta_r, time_ticks)

        if 0 < dist < steps:
            pass
        else:
            continue_loop = False

    if dist == 0:
        time_ticks = 0

    return time_ticks


def QueryPenUp(port_name):
    if port_name is not None:
        pen_status = ebb_serial_my.query(port_name, 'QP\r')
        if pen_status[0] == '0':
            return False
        else:
            return True


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


def sendPenDown(port_name, pen_delay):
    if port_name is not None:
        str_output = 'SP,0,{0}\r'.format(pen_delay)
        ebb_serial_my.command(port_name, str_output)


def sendPenUp(port_name, pen_delay):
    if port_name is not None:
        str_output = 'SP,1,{0}\r'.format(pen_delay)
        ebb_serial_my.command(port_name, str_output)


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


def TogglePen(port_name):
    if port_name is not None:
        ebb_serial_my.command(port_name, 'TP\r')


def setPenDownPos(port_name, servo_max):
    if port_name is not None:
        ebb_serial_my.command(port_name, 'SC,5,{0}\r'.format(servo_max))
        # servo_max may be in the range 1 to 65535, in units of 83 ns intervals. This sets the "Pen Down" position.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenDownRate(port_name, pen_down_rate):
    if port_name is not None:
        ebb_serial_my.command(port_name, 'SC,12,{0}\r'.format(pen_down_rate))
        # Set the rate of change of the servo when going down.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenUpPos(port_name, servo_min):
    if port_name is not None:
        ebb_serial_my.command(port_name, 'SC,4,{0}\r'.format(servo_min))
        # servo_min may be in the range 1 to 65535, in units of 83 ns intervals. This sets the "Pen Up" position.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setPenUpRate(port_name, pen_up_rate):
    if port_name is not None:
        ebb_serial_my.command(port_name, 'SC,11,{0}\r'.format(pen_up_rate))
        # Set the rate of change of the servo when going up.
        # http://evil-mad.github.io/EggBot/ebb.html#SC


def setEBBLV(port_name, ebb_lv):
    # Set the EBB "Layer" Variable, an 8-bit number we can read and write.
    # (Unrelated to our plot layers; name is an historical artifact.)
    if port_name is not None:
        ebb_serial_my.command(port_name, 'SL,{0}\r'.format(ebb_lv))


def queryEBBLV(port_name):
    # Query the EBB "Layer" Variable, an 8-bit number we can read and write.
    # (Unrelated to our plot layers; name is an historical artifact.)
    if port_name is not None:
        value = ebb_serial_my.query(port_name, 'QL\r')
        try:
            ret_val = int(value)
            return value
        except:
            return None


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
         #print(b) 
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
        
        
def state_ZERO_XY(ser):   #поднять палец и отправить в HOME      
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
       
def pmf_state_Zero_grid(ser):  #выход на нуль сетки ПМФа
                            
            doABMove(ser,3750,8150,1000)
            doTimedPause(ser,1000)        #pause 1s
            
def pmf_state_Zero(ser):  #выход на нуль сетки ПМФа
            #doABMove(ser,3800,6220,1000)
            doABMove(ser,2100,6220,1000)                
            doTimedPause(ser,1000)        #pause 1s
                       
def rect_test1(ser,DX,DY,DT,sleep,pen_down_delay_ms): 
     
    sendPenDown(ser, pen_down_delay_ms)
    doTimedPause(ser,sleep)               
    
    for i in range(0,DX,int (DX/10)):
           doABMove(ser, 0,int (DX/10),100)                      
    doTimedPause(ser,sleep)                          
                                
                                
                                
    for i in range(0,DX,int (DX/10)):
           doABMove(ser, int (DX/10),0,100)                      
    doTimedPause(ser,sleep)                                       
                              
                              
                              
    for i in range(0,DX,int (DX/10)):
           doABMove(ser, 0,int (-DX/10),100)                      
    doTimedPause(ser,sleep)                                    
                              
                            
    for i in range(0,DX,int (DX/10)):
           doABMove(ser, int (-DX/10),0,100)                      
                                     
def rect_test2(ser,DX,DY,DT,sleep,pen_down_delay_ms): 
        
    doTimedPause(ser,700) 
    TogglePen(ser) 
    doTimedPause(ser,700) 
    TogglePen(ser)
    doTimedPause(ser,700)
    
    
    for i in range(0,DX,DX/10):
           doABMove(ser, 0,DX/10,100)                      
         
    doTimedPause(ser,700) 
#    TogglePen(ser) 
#    doTimedPause(ser,700) 
#    TogglePen(ser)
#    doTimedPause(ser,700)
#   
    for i in range(0,DX,DX/10):
           doABMove(ser, DY/10,0,100)                      
    doTimedPause(ser,700) 
#    TogglePen(ser)
#    doTimedPause(ser,700)
#    TogglePen(ser)
#    doTimedPause(ser,700)             
#                            
    for i in range(0,DX,DX/10):
               doABMove(ser, 0,-DX/10,100)                      
    doTimedPause(ser,700) 
#    TogglePen(ser)
#    doTimedPause(ser,700)                                  
#    TogglePen(ser)   
#    doTimedPause(ser,700)                      
#    
    
    for i in range(0,DX,DX/10):
               doABMove(ser, -DY/10,0,100)                      
    doTimedPause(ser,700) 
#    TogglePen(ser)
#    doTimedPause(ser,700)                                
#    TogglePen(ser)                          
#    doTimedPause(ser,700)
#   

       
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

def byk_byk(ser, pen_down_delay_ms):
    sendPenDown(ser, pen_down_delay_ms)
    time.sleep(0.3)    
    sendPenUp(ser, pen_down_delay_ms)
    time.sleep(0.3)             

def long_pause(seconds):
    for i in range(seconds*2):
          doTimedPause(ser,500)        

def servo_timeout(port_name, timeout_ms, state=None):
    # Set the EBB servo motor timeout.
    # The EBB will cut power to the pen-lift servo motor after a given
    # time delay since the last X/Y/Z motion command.
    # It can also optionally set an immediate on/off state.
    # 
    # The time delay timeout_ms is given in ms. A value of 0 will
    # disable the automatic power-off feature.
    #
    # The state parameter is given as 0 or 1, to turn off or on
    # servo power immediately, respectively.
    #
    # This feature requires EBB hardware v 2.5.0 and firmware 2.6.0
    #
    # Reference: http://evil-mad.github.io/EggBot/ebb.html#SR
    #
    if port_name is not None:
        version_status = ebb_serial_my.min_version(port_name, "2.6.0")
        if not version_status:
            return      # Unable to read version, or version is below 2.6.0.
        else:
            if state is None:
                str_output = 'SR,{0}\r'.format(timeout_ms)
            else:
                str_output = 'SR,{0},{1}\r'.format(timeout_ms, state)
            ebb_serial_my.command(port_name, str_output)


def grid_prepare(ser,X_len,Y_len, X_grid,Y_grid,hor_vert):

   number_of_image=1
   cap = cv.VideoCapture('/dev/video3')
   cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
   cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
   basename = "img"
   d_x=0
   d_y=0
   global arr_out   
   global flag_touch_push
  # my_pos(ser)
  
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
   
   X_stp = (X_len/(X_grid))                      
   Y_stp = (Y_len/(Y_grid))
   arr=[[[0, 0]] * X_grid for i in range(Y_grid)]
   
   for y in range(Y_grid):     
       for x in range(X_grid):
           a= int((x*X_stp)+(X_stp/2))
           b =int((y*Y_stp)+(Y_stp/2))
           arr[x][y] = [a,b]
   #print (arr)
  
   if hor_vert==1: 
        arr = np.rot90(arr, 1)   #rotating
        arr = arr[::-1]
   
   
   for x in range(1,X_grid,2):  #переворот строки через строку (змейка)
       arr[x]=arr[x][::-1]

 #  print(arr)
 #  print("________")
   
   arr_out=[[0,0]]*(X_grid*Y_grid)
   arr_out=sum(arr,[])
  
 #  print (arr_out)      
   start_x=0
   start_y=0
   delta_x=X_len/X_grid
   delta_y=Y_len/Y_grid
     
   for x in range(0,X_grid):
       
       if x != 0:
          start_x=start_x+delta_x
       else:
            start_x=0

       for y in range(0,Y_grid):
           
           d_x1=arr[x][y][0]
           d_y1=arr[x][y][1]
           
           d_x=d_x1-d_x2
           d_y=d_y1-d_y2
          
           print(d_x,d_y)
           
           
           

           if not cap.isOpened():
                    sendEnableMotors(ser,0)
                    sys.exit("Cannot open camera")
           ret, frame = cap.read()
           if not ret:
                    sendEnableMotors(ser,0)
                    sys.exit("Cannot receive frame")
                    break
           
           writeStatus = cv.imwrite(str(start_x)+"_"+str(start_y)+ ".jpg", img=frame)
           if writeStatus is True:
                 print("image written")
           else:
                sys.exit("Cannot save frame")

           doABMove(ser,d_y,d_x,500)
          
           #cv.imshow('frame', frame)
           doTimedPause(ser,1000)
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


   state_ZERO_XY(ser,100)
   
   sendEnableMotors(ser,0)
   print("Scaning finish succsefully")
    
 
def test_while():
    while 1:
           a=29000
           b=20000
           setPenUpPos(ser, a)
           setPenDownPos(ser,b)
           
           sendPenDown(ser,1000)
           sendPenUp(ser, 1000)
           time.sleep(0.1)

def main1(ser):

   X_len=input()
   X_len=int(X_len)
   Y_len=input()
   Y_len=int(Y_len)
   X_grid=input()
   X_grid=int(X_grid)
   Y_grid=input()
   Y_grid=int(Y_grid)
   hor_vert=input()
   hor_vert=int(hor_vert)
   grid_prepare(ser,X_len,Y_len,X_grid,Y_grid,hor_vert)
    
    ##th1 = threading.Thread(name='ebb', target=grid_prepare, args=(ser,X_len,Y_len,X_grid,Y_grid,hor_ver))

    ##th1.start()

def heatup_moves(ser):
    MAX_SPEED = 25000  # steps/s
       
    DY = 1620*6
    DX = 2120*6
    DT = 4000
    dist = max(DX, DY)
    speed = int(dist * 1000 / DT)
    assert speed < MAX_SPEED, 'Too fast!'
    setPenUpPos(ser, 20000)
    setPenDownPos(ser, 29000)
    time.sleep(1)
    
    sendEnableMotors(ser,   1)
    print("Отладка")
                # If res == 0, -> Motor disabled
                # If res == 1, -> 16X microstepping
                # If res == 2, -> 8X microstepping
                # If res == 3, -> 4X microstepping
                # If res == 4, -> 2X microstepping
                # If res == 5, -> No microstepping    
#    doABMove(ser,0,1000,1000)   
#    doABMove(ser,1000,0,1000)
#    doABMove(ser,0,-1000,1000)   
#    doABMove(ser,-1000,0,1000)
                
#    while 1:
#        print (time.strftime("WORK TIME:" + "%H" ":" + "%M" + ":" + "%S"))
#        long_pause(1)        
#        state_ZERO_XY(ser,pen_up_delay_ms) 
#        pmf_state_Zero_grid(ser)
#        long_pause(1)
#        
#        
#       for i in range(10):    
#        
#           rect_test1(ser,DX,DY,DT,sleep,pen_down_delay_ms)
#         
#            # rect_test2(ser,DX,DY,DT,sleep,pen_down_delay_ms)
             
#    while 1:
#        long_pause(1)        
#        state_ZERO_XY(ser,pen_up_delay_ms) 
#        pmf_state_Zero(ser)
#        long_pause(1)
#        i= not (i)
#        grid_prepare(ser,17150,12880,8,8 ,i)
        
if __name__ == "__main__":
   
   arr_out =[]  
   x_ebb=0
   y_ebb=0
   err_x=0
   err_y=0
   
   
   flag_touch_push=False
   flag_limit_X=False
   flag_limit_Y=False   
   ser = ebb_serial_my.testPort("/dev/ttyACM0")
   sendEnableMotors(ser,0)
   print(ser)
   if ser:
       main1(ser) 

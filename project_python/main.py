from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import cv2
from PIL import Image, ImageTk
import os
import util
import time
from threading import Thread

import ebb_motion as ebb_command
import ebb_serial_my as ebb_serial

from settings import Settings
from open_project import OpenProejct
from create_project import CreateProject


class MainWindow:
    def __init__(self):
        self.main_window = Tk()
        width= self.main_window.winfo_screenwidth() 
        height= self.main_window.winfo_screenheight()
        #setting tkinter window size
        self.main_window.geometry("%dx%d" % (width, height)) 
        self.main_window.title('Гланое окно')
        
        self.alignment_enable = True
        self.scanning_enable = False
        self.recognition_enable = False
        ebb_command.main()
        self.x_now=0
        self.y_now=0
        
        self.state = False
        self.ser = ebb_serial.testPort('/dev/ttyACM0')
        
        self.menubar = Menu(self.main_window,background='white', foreground='black', activebackground='white', activeforeground='black')
        self.file = Menu(self.menubar,tearoff=0, background='white', foreground='black')
        self.file.add_command(label='Создать', command=self.create_project)
        self.file.add_command(label='Открыть', command='')
        self.file.add_command(label='Настройки', command=self.open_settings)
        self.menubar.add_cascade(label='Файл', menu=self.file)
        self.main_window.config(menu=self.menubar)
        
        self.notebook = ttk.Notebook()
        self.notebook.grid(row=0,column=0)
        
        self.alignment = ttk.Frame(self.notebook)
        self.scanning = ttk.Frame(self.notebook)
        self.recognition = ttk.Frame(self.notebook)
                    
        self.webcam_label = Label(self.alignment)
        self.webcam_label.grid(row=0, column=0, rowspan=6, columnspan=6)
        
        self.b_to_ZERO =  Button(self.alignment, text='Вернуть на стартовую позицию', command=self.to_Zero)
        self.b_move_up =  Button(self.alignment, text='Вверх', command=self.move_up)
        self.b_move_down =  Button(self.alignment, text='Вниз', command=self.move_down)
        self.b_move_left =  Button(self.alignment, text='Влево', command=self.move_left)
        self.b_move_right =  Button(self.alignment, text='Вправо', command=self.move_right)
        self.b_scanning = Button(self.alignment, text='Сканирование', command = self.test)#self.start_scaninng)
        
        self.l_x_cord = Label(self.alignment,text=f'X= {self.x_now} Y= {self.y_now}')
        self.e_value = Entry(self.alignment)
        
        self.b_to_ZERO.grid(row=0, column=7, columnspan=3)
        self.l_x_cord.grid(row=1,column=7)
        self.e_value.grid(row=2, column=7, columnspan=3)
        self.b_move_up.grid(row=3, column=8)
        self.b_move_left.grid(row=4, column=7)
        self.b_move_down.grid(row=4, column=8)
        self.b_move_right.grid(row=4, column=9)
        self.b_scanning.grid(row=5, column=7, columnspan=3)
        
        self.add_webcam(self.webcam_label)
        
        # добавляем фреймы в качестве вкладок
        self.notebook.add(self.alignment, text="Юстировка")
        self.notebook.add(self.scanning, text="Сканирование")
        self.notebook.add(self.recognition, text='Распознавание')
        
        """self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)"""

    def test(self):
        ebb_command.my_pos(self.ser)
        
    def thred_scan(self):
        t1 = Thread(target=self.capture, args=(self))
        t2 = Thread(target=self.start_scaninng, args=(self))
        t1.start()
        t2.start()
        showinfo('Complete','Сканирование окончено')
    
    def capture(self):
        k=0
        while True:
            k+=1
            ret, frame = self.cap.read()
            cv2.imwrite(str(k)+'.jpg', img=frame)
            if self.state==True:
                break
            time.sleep(0.01)
        
        self.state == False
        showinfo('Complete','Сканирование окончено')
        

    def start_scaninng(self):
        y=0
        ebb_command.sendEnableMotors(self.ser, 1)
        
        while y<=self.y_now:
            ebb_command.doABMove(self.ser, self.x_now, 0, 15)
            #ebb_command.doTimedPause(self.ser, 1000)
            time.sleep(3)
            ebb_command.doABMove(self.ser, 0, 10, 15)
            y+=10
            #ebb_command.doTimedPause(self.ser, 1000)
            time.sleep(3)
            
            ebb_command.doABMove(self.ser, self.x_now*-1, 0, 15)
            #ebb_command.doTimedPause(self.ser, 1000)
            time.sleep(3)
            
            ebb_command.doABMove(self.ser, 0, 10, 15)
            y+=10
            #ebb_command.doTimedPause(self.ser, 1000) 
            time.sleep(3)

        ebb_command.state_ZERO_XY(self.ser)   
        ebb_command.sendEnableMotors(self.ser, 0)    
        self.state = True

    def to_Zero(self):
        ebb_command.sendEnableMotors(self.ser, 1)
        ebb_command.state_ZERO_XY(self.ser)
        ebb_command.sendEnableMotors(self.ser, 0)
        self.x_now=0
        self.y_now=0
        self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        
    def move_right(self):
        if self.x_now + int(self.e_value.get()) <=100000:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, int(self.e_value.get()), 0, 10000)
            time.sleep(2)
            #ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.x_now += int(self.e_value.get())
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        elif self.x_now!=100000:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, (100000-self.x_now), 0, 10000)
            time.sleep(2)
            
            #ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.x_now = 100000
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        else:
            showerror(title='Ошибка', message='Конец по оси Х')
    
    def move_left(self):
        if self.x_now - int(self.e_value.get())>=0:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, int(self.e_value.get())*-1, 0, 10000)
            time.sleep(2)
            
            #ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.x_now -=int(self.e_value.get())
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        elif self.x_now != 0:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0-self.x_now, 0, 10000)
            time.sleep(2)
            
            #ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.x_now = 0
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        else:
            showerror(title='Ошибка', message='Конец по оси Х')
    
    def move_up(self):
        if self.y_now - int(self.e_value.get())>=0:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0, int(self.e_value.get())*-1, 10000)
            time.sleep(2)
            
            #ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)   
            self.y_now -=int(self.e_value.get())
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        elif self.y_now !=0:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0, 0-self.y_now, 10000)
            time.sleep(2)
            
            #ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.y_now = 0
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        else:
            showerror(title='Ошибка', message='Конец по оси Y')
    
    def move_down(self):
        if self.y_now + int(self.e_value.get())<=20000:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0, int(self.e_value.get()), 10000)
            time.sleep(2)
            
            #ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.y_now +=int(self.e_value.get())
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        elif self.y_now != 20000:
            ebb_command.sendEnableMotors(self.ser, 1)
            ebb_command.doABMove(self.ser, 0, 20000-self.y_now, 10000)
            time.sleep(2)
            
            #ebb_command.doTimedPause(self.ser, 1000) 
            ebb_command.sendEnableMotors(self.ser, 0)
            self.y_now = 20000
            self.l_x_cord['text'] = f'X= {self.x_now} Y= {self.y_now}'
        else: 
            showerror(title='Ошибка', message='Конец по оси Y')
                
    def add_webcam(self, label):

        self.cap = util.get_cap()
        
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        frame = cv2.line(frame, (650,160),(650,520),(0,0,255),3)
        frame = cv2.line(frame, (470,340),(830,340),(0,0,255),3)
        if self.notebook.select() == '.!notebook.!frame':
            self.most_recent_capture_arr = frame
            img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
            self.most_recent_capture_pil = Image.fromarray(img_)
            imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
            self._label.imgtk = imgtk
            self._label.configure(image=imgtk)
        #elif self.notebook.select() == '.!notebook.!frame1':
              

        self._label.after(20, self.process_webcam)

    def create_project(self):
        createproject = CreateProject()
    
    def open_settings(self):
        settings = Settings()
    
    def start(self):
        self.main_window.mainloop()
        
if __name__ == "__main__":
    util.create_camera()
    app = MainWindow()
    app.start()
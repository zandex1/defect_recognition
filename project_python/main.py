from tkinter import *
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import os
import util

class MainWindow:
    def __init__(self):
        self.main_window = Tk()
        self.main_window.geometry("1200x520+350+100")
        self.main_window.title('Гланое окно')
        
        self.alignment_enable = True
        self.scanning_enable = False
        self.recognition_enable = False
        
        
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
        self.webcam_label.grid()
                
        
        self.add_webcam(self.webcam_label)
        
        # добавляем фреймы в качестве вкладок
        self.notebook.add(self.alignment, text="Юстировка")
        self.notebook.add(self.scanning, text="Сканирование")
        self.notebook.add(self.recognition, text='Распознавание')
        
        """self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)"""

    def add_webcam(self, label):

        self.cap = util.get_cap()
        
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()
        if self.notebook.select() == '.!notebook.!frame':
            self.most_recent_capture_arr = frame
            img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
            self.most_recent_capture_pil = Image.fromarray(img_)
            imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
            self._label.imgtk = imgtk
            self._label.configure(image=imgtk)
            print('ttt')
        #elif self.notebook.select() == '.!notebook.!frame1':
              

        self._label.after(20, self.process_webcam)

    def create_project(self):
        createproject = CreateProject()
    
    def open_settings(self):
        settings = Settings()
    
    def start(self):
        self.main_window.mainloop()

class OpenProejct:
    def __init__(self) -> None:
        pass

class CreateProject:
    def __init__(self) -> None:
        top = Toplevel()
        self.frame = Frame(top)
        
        var = StringVar()
        entry = Entry(top, textvariable=var)
        #entry.pack(padx=60,pady=50)
        
        
        #self.frame.pack(padx=10,pady=10)
    
class FileBrowser:
    def __init__(self) -> None:
        pass

class Settings:
    def __init__(self) -> None:
        settings_window = Toplevel()
        settings_window.geometry("1200x520+350+100")
        settings_window.title('Настройки')
        #self.frame = Frame(settings_window)
        
        
        self.notebook_settings = ttk.Notebook(settings_window)
        self.notebook_settings.grid(row=0, column=0)
        
        # Усилитель видеопроцессора
        self.settings_videoprocessor = ttk.Frame(self.notebook_settings)
        self.settings_stand = ttk.Frame(self.notebook_settings)
        
        self.l_brightnes = Label(self.settings_videoprocessor, text='Яркость')
        self.s_brightnes = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_brightnes = Entry(self.settings_videoprocessor)
        
        self.l_brightnes.grid(row=0, column=0)
        self.s_brightnes.grid(row=0, column=1) 
        self.e_brightnes.grid(row=0, column=2)
        
        self.l_contrast = Label(self.settings_videoprocessor, text='Контрастность')
        self.s_contrast = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_contrast = Entry(self.settings_videoprocessor)
        
        self.l_contrast.grid(row=1, column=0)
        self.s_contrast.grid(row=1, column=1) 
        self.e_contrast.grid(row=1, column=2)
        
        self.l_shade = Label(self.settings_videoprocessor, text='Оттенок')
        self.s_shade = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_shade = Entry(self.settings_videoprocessor)
        
        self.l_shade.grid(row=2, column=0)
        self.s_shade.grid(row=2, column=1) 
        self.e_shade.grid(row=2, column=2)
        
        self.l_saturation = Label(self.settings_videoprocessor, text='Насыщенность')
        self.s_saturation = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_saturation = Entry(self.settings_videoprocessor)
        
        self.l_saturation.grid(row=3, column=0)
        self.s_saturation.grid(row=3, column=1) 
        self.e_saturation.grid(row=3, column=2)
        
        self.l_clarity = Label(self.settings_videoprocessor, text='Четкость')
        self.s_clarity = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_clarity = Entry(self.settings_videoprocessor)
        
        self.l_clarity.grid(row=4, column=0)
        self.s_clarity.grid(row=4, column=1) 
        self.e_clarity.grid(row=4, column=2)
        
        self.l_gamma = Label(self.settings_videoprocessor, text='Гамма')
        self.s_gamma = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_gamma = Entry(self.settings_videoprocessor)
        
        self.l_gamma.grid(row=5, column=0)
        self.s_gamma.grid(row=5, column=1) 
        self.e_gamma.grid(row=5, column=2)
        
        self.l_white_balance = Label(self.settings_videoprocessor, text='Баланс белого')
        self.s_white_balance = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_white_balance = Entry(self.settings_videoprocessor)
        
        self.l_white_balance.grid(row=6, column=0)
        self.s_white_balance.grid(row=6, column=1) 
        self.e_white_balance.grid(row=6, column=2)
        
        self.l_gain = Label(self.settings_videoprocessor, text='Усиление')
        self.s_gain = Scale(self.settings_videoprocessor, from_=0, to=100, orient='horizontal')
        self.e_gain = Entry(self.settings_videoprocessor)
        
        self.l_gain.grid(row=7, column=0)
        self.s_gain.grid(row=7, column=1) 
        self.e_gain.grid(row=7, column=2)
        
        self.b_return_to_common = Button(self.settings_videoprocessor, text='По умолчанию')
        
        self.b_return_to_common.grid(row=8, column=1)
        
        # Управление стендом
        self.l_selected_camera = Label(self.settings_stand, text='Камера')
        self.cb_selected_camera = ttk.Combobox(self.settings_stand,values=['/dev/video0','/dev/video1'])
        
        self.l_selected_camera.grid(row=0, column=0)
        self.cb_selected_camera.grid(row=0, column=2)
        
        self.l_selected_COM = Label(self.settings_stand, text='COM порт')
        self.cb_selected_COM = ttk.Combobox(self.settings_stand,values=['/dev/video0','/dev/video1'])
        
        self.l_selected_COM.grid(row=1, column=0)
        self.cb_selected_COM.grid(row=1, column=2)
        
        self.l_scale = Label(self.settings_stand, text='Масштаб')
        self.s_scale = Scale(self.settings_stand, from_=0, to=100, orient='horizontal')
        self.e_scale = Entry(self.settings_stand)
        
        self.l_scale.grid(row=2, column=0)
        self.s_scale.grid(row=2, column=1) 
        self.e_scale.grid(row=2, column=2)
        
        self.l_focus = Label(self.settings_stand, text='Фокус')
        self.s_focus = Scale(self.settings_stand, from_=0, to=100, orient='horizontal')
        self.e_focus = Entry(self.settings_stand)
        
        self.l_focus.grid(row=3, column=0)
        self.s_focus.grid(row=3, column=1) 
        self.e_focus.grid(row=3, column=2)
        
        self.l_shutter = Label(self.settings_stand, text='Выдержка')
        self.s_shutter = Scale(self.settings_stand, from_=0, to=100, orient='horizontal')
        self.e_shutter = Entry(self.settings_stand)
        
        self.l_shutter.grid(row=4, column=0)
        self.s_shutter.grid(row=4, column=1) 
        self.e_shutter.grid(row=4, column=2)
        
        self.l_speed_aperture = Label(self.settings_stand, text='Диафрагма')
        self.s_speed_aperture = Scale(self.settings_stand, from_=0, to=100, orient='horizontal')
        self.e_speed_aperture = Entry(self.settings_stand)
        
        self.l_speed_aperture.grid(row=5, column=0)
        self.s_speed_aperture.grid(row=5, column=1) 
        self.e_speed_aperture.grid(row=5, column=2)
        
        # добавляем фреймы в качестве вкладок
        self.notebook_settings.add(self.settings_videoprocessor, text="Усилитель видеопроцессора")
        self.notebook_settings.add(self.settings_stand, text="Управление стендом")
        
        self.webcam_label = Label(settings_window)
        self.webcam_label.grid(row=0, column=1)
                
        self.add_webcam(self.webcam_label)
    
    def start(self):
        self.frame.mainloop()   
    
    def add_webcam(self, label):

        self.cap = util.get_cap()
        
        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

        
if __name__ == "__main__":
    util.create_camera()
    app = MainWindow()
    app.start()
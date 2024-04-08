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
        
        self.menubar = Menu(self.main_window,background='white', foreground='black', activebackground='white', activeforeground='black')
        self.file = Menu(self.menubar,tearoff=0, background='white', foreground='black')
        self.file.add_command(label='Создать', command='')
        self.file.add_command(label='Открыть', command='')
        self.file.add_command(label='Настройки', command='')
        self.menubar.add_cascade(label='Файл', menu=self.file)
        self.main_window.config(menu=self.menubar)
        
        self.notebook = ttk.Notebook()
        self.notebook.pack(expand=True, fill=BOTH)
        
        self.alignment = ttk.Frame(self.notebook)
        self.scanning = ttk.Frame(self.notebook)
        self.recognition = ttk.Frame(self.notebook)
                    
        self.webcam_label = util.get_img_label(self.alignment)
        self.webcam_label.grid()
                
        
        self.add_webcam(self.webcam_label)
        
        self.alignment.pack(fill=BOTH, expand=True)
        self.scanning.pack(fill=BOTH, expand=True)
        self.recognition.pack(fill=BOTH, expand=True)
        
        # добавляем фреймы в качестве вкладок
        self.notebook.add(self.alignment, text="Юстировка")
        self.notebook.add(self.scanning, text="Сканирование")
        self.notebook.add(self.recognition, text='Распознавание')
        """self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)"""

    def add_webcam(self, label):

        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

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

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_pil.copy()

    def start(self):
        self.main_window.mainloop()



if __name__ == "__main__":
    app = MainWindow()
    app.start()
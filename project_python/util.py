from tkinter import *
from tkinter import ttk
from tkinter import messagebox

def get_button(window: Tk | ttk.Frame | Toplevel, text: str, color:str, command, fg: str)->Button:
    """Создание кнопки

    Args:
        window (Tk | Frame | Toplevel): Окно к которому прикрепить
        text (str): Текст кнопки
        color (str): Цвет заднего фона
        command (function): Указание на функцию которая должна быть выполнена при нажатии на нее
        fg (str): Цвет текста.

    Returns:
        Button: Кнопка
    """
    button = Button(
        window,
        text=text,
        activebackground="black",
        activeforeground="white",
        fg=fg,
        bg=color,
        command=command,
        height=2,
        width=20,
        font=('Helvetica bold', 20)
    )
    
    return button

def get_img_label(window: Tk | ttk.Frame | Toplevel)->Label:
    """Создать поля для вывода изображение

    Args:
        window (Tk | Frame | Toplevel): Окно к которому прикрепить

    Returns:
        Label: Поле для вывода изображения
    """
    label = Label(window)
    label.grid(row=0,column=0)
    return label

def get_text_label(window: Tk | ttk.Frame | Toplevel, text: str)->Label:
    """Создаёт поле для вывода текста

    Args:
        window (Tk | Frame | Toplevel): Окно к которому прикрепить
        text (str): Текст поля

    Returns:
        Label: Поле для вывода текста
    """
    label = Label(window, text=text)
    label.config(font=("sans-serif",21), justify="left")
    return label

def get_entry_text(window: Tk | ttk.Frame | Toplevel)->Text:
    """Создает поле для ввода текста

    Args:
        window (Tk | Frame | Toplevel): Окно к которому прикрепить

    Returns:
        Text: Поле для ввода текста
    """
    inputtxt = Text(window,
                       height=2,
                       width=15,
                       font=("Arial",32))
    return inputtxt

def msg_box(title:str, description:str):
    """ MessageBox

    Args:
        title (str): Название окна
        description (str): Описание окна
        
    Выведет информационное сообщение
    """
    messagebox.showinfo(title, description)
    
def get_scale(window:Tk | ttk.Frame | Toplevel,start: int, end: int)->Scale:
    """Создать слайдер

    Args:
        window (Tk | Frame | Toplevel): Окно к которому прикрепить
        start (int): Стартовое значение
        end (int): Еонечное значение

    Returns:
        Scale: Горизонтальный слайдер
    """
    slider =  Scale(
        window,
        from_=start,
        to=end,
        orient='horizontal'
    )
    
    return slider
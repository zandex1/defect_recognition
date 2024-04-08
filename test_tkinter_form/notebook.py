from tkinter import *
from tkinter import ttk
 
root = Tk()
root.title("METANIT.COM")
root.geometry("250x200") 
 
# создаем набор вкладок
notebook = ttk.Notebook()
notebook.pack(expand=True, fill=BOTH)
 
# создаем пару фреймвов
frame1 = ttk.Frame(notebook)
frame2 = ttk.Frame(notebook)

button = ttk.Label(frame1, text="hello")
button.grid(row=2,column=2)

frame1.pack(fill=BOTH, expand=True)
frame2.pack(fill=BOTH, expand=True)
 
# добавляем фреймы в качестве вкладок
notebook.add(frame1, text="Python")
notebook.add(frame2, text="Java")
 
root.mainloop()
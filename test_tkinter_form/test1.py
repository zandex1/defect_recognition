import tkinter as tk

window = tk.Tk()
window.title("Okno")

def validate(new_value):                                                  # +++
    return new_value == "" or new_value.isnumeric()                       # +++

que = tk.Label(window, text="Введите цифры")

vcmd = (window.register(validate), '%P')                                  # +++
ans = tk.Entry(window, validate='key', validatecommand=vcmd)              # +++

que.grid(row=0, column=0, sticky="e")
ans.grid(row=0, column=1)
ans.focus()

window.mainloop()
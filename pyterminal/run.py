from tkinter import Tk
from .MainWindow import MainWindow

def window():
    window = Tk()
    window.minsize(400, 150)
    interface = MainWindow(window)

    interface.mainloop()

if __name__ == '__main__':
    window()
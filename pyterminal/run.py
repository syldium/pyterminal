from tkinter import Tk
from .MainWindow import MainWindow


def window() -> None:
    w = Tk()
    w.minsize(400, 150)
    interface = MainWindow(w)

    interface.mainloop()


if __name__ == '__main__':
    window()

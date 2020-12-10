from .LogicTerminalWidget import LogicTerminalWidget
from tkinter import BOTH, Frame, Tk


class MainWindow(Frame):
    """Terminal emulator window."""

    def __init__(self, windows: Tk, **kwargs):
        Frame.__init__(self, windows, **kwargs)
        self.master.title("Python terminal emulator")
        self.pack(fill=BOTH, expand=True)

        self.terminal = LogicTerminalWidget(self)
        self.terminal.pack(fill=BOTH, expand=True)

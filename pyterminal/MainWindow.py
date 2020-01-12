from .TerminalWidget import TerminalWidget
from tkinter import BOTH, Frame

"""
Terminal emulator window.
"""
class MainWindow(Frame):

    def __init__(self, windows, **kwargs):
        Frame.__init__(self, windows, **kwargs)
        self.master.title("Python terminal emulator")
        self.pack(fill=BOTH, expand=True)

        self.terminal = TerminalWidget(self)
        self.terminal.pack(fill=BOTH, expand=True)
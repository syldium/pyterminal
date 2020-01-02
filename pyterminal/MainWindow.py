from .CmdProcessor import CmdProcessor
from tkinter import BOTH, END, Entry, Frame, X
from tkinter.scrolledtext import ScrolledText
from .helpers import getCmdInvite

"""
Terminal emulator window.
"""
class MainWindow(Frame):

    def __init__(self, windows, **kwargs):
        Frame.__init__(self, windows, **kwargs)
        self.master.title("Python terminal emulator")
        self.pack(fill=BOTH)

        self.text_options = {"state": "disabled",
                             "bg": "black",
                             "fg": "white",
                             "insertbackground": "#08c614",
                             "selectbackground": "#fcfcfc"}

        self.logWidget = ScrolledText(self, **self.text_options)
        self.logWidget.pack(expand=True, fill=BOTH)
        self.logWidget.bind("<1>", lambda e: self.logWidget.focus_set())
        self.logWidget.tag_config("invite", foreground="#4E9A06", selectbackground="#4E9A06", selectforeground="black")

        self.cmdEntry = Entry(self)
        self.cmdEntry.pack(expand=False, fill=X)
        self.cmdEntry.bind("<Return>", self.doCMD)
        self.cmdEntry.bind("<Command-a>", lambda e: self.cmdEntry.select_range(0, "end"))

        self.cmdProcessor = CmdProcessor(self.write, self.endHook)
        self.write(getCmdInvite(), "invite")

    def write(self, message, tag):
        self.logWidget.config(state="normal")
        self.logWidget.insert("end", message, tag)
        self.logWidget.see("end")
        self.logWidget.config(state="disabled")

    def doCMD(self, event=None):
        self.cmdProcessor.start_thread(self.cmdEntry.get())
        self.cmdEntry.config(state="disabled")
    
    def endHook(self):
        self.cmdEntry.config(state="normal")
        self.cmdEntry.delete(0, END)
        self.write(getCmdInvite(), "invite")
from .CmdProcessor import CmdProcessor
from .helpers import getCmdInvite
from tkinter import BOTH, END, Entry, Frame, X
from tkinter.scrolledtext import ScrolledText

"""
Custom widget composed of a ScrolledText and an Entry.
"""
class TerminalWidget(Frame):

    def __init__(self, parent, cmdProcessor = None, getPrompt = None):
        Frame.__init__(self, parent)

        self.history = [] # Stored commands of the current session
        self.historyPos = 0 # Current position in the history

        # Set the command processor
        if cmdProcessor is None:
            cmdProcessor = CmdProcessor(self.write, self.endHook)
        self.processor = cmdProcessor

        # Set the getter of the command prompt
        if getPrompt is None:
            getPrompt = getCmdInvite
        self.getPrompt = getPrompt

        parent.master.bind("<Control-c>", self.processor.sigint) # Bind the key combination to exit
        parent.master.bind("<Up>", lambda e: self.browseHistory(-1))
        parent.master.bind("<Down>", lambda e: self.browseHistory(1))

        self.createWidgets()
        self.write(self.getPrompt(), "invite")
    
    def doCmd(self, event = None):
        """Executes the command entered."""
        self.historyPos += 1
        if self.processor.parse(self.cmdEntry.get()):
            self.cmdEntry.config(state="disabled")
    
    def endHook(self):
        """When a command finishes."""
        self.cmdEntry.config(state="normal")
        self.cmdEntry.delete(0, END)
        self.write(self.getPrompt(), "invite")

    def browseHistory(self, direction):
        """Browse through the command history and use the selected command."""
        newPosition = self.historyPos + direction
        if not -1 < newPosition < len(self.history):
            return

        self.historyPos = newPosition
        cmd = self.history[self.historyPos]
        self.cmdEntry.delete(0, END)
        self.cmdEntry.insert(0, cmd)

    def onKeyRelease(self, event = None):
        """Update the history when a key is released."""
        try:
            self.history[self.historyPos] = self.cmdEntry.get()
        except IndexError:
            self.history.insert(self.historyPos, self.cmdEntry.get())

    def write(self, message, tag):
        """Write something in the logs."""
        self.logWidget.config(state="normal")
        self.logWidget.insert("end", message, tag)
        self.logWidget.see("end")
        self.logWidget.config(state="disabled")

    def createWidgets(self):
        """Create a ScrolledText and Entry widgets."""
        self.text_options = {"state": "disabled",
             "bg": "black",
             "fg": "white",
             "insertbackground": "#08c614",
             "selectbackground": "#fcfcfc"}

        self.logWidget = ScrolledText(self, **self.text_options)
        self.logWidget.tag_config("invite", foreground="#4E9A06", selectbackground="#4E9A06", selectforeground="black")
        self.logWidget.pack(expand=True, fill=BOTH)

        self.cmdEntry = Entry(self)
        self.cmdEntry.bind('<KeyRelease>', self.onKeyRelease)
        self.cmdEntry.bind("<Return>", self.doCmd)
        self.cmdEntry.pack(expand=False, fill=X)
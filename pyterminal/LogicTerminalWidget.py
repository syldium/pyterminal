from .CmdProcessor import CmdProcessor
from .TerminalWidget import TerminalWidget

"""
Implement terminal logic.
"""
class LogicTerminalWidget(TerminalWidget):

    def __init__(self, parent, cmdProcessor = None, getPrompt = None):
        TerminalWidget.__init__(self, parent, getPrompt)

        # Set the command processor
        if cmdProcessor is None:
            cmdProcessor = CmdProcessor(self.write, self.prompt)
        self.processor = cmdProcessor

        self.history = [] # Stored commands of the current session
        self.historyPos = 0 # Current position in the history

        self.bind("<Control-c>", self.processor.sigint) 
        self.bind("<Return>", self.enter)
        self.bind("<Up>", lambda e: self.browseHistory(-1))
        self.bind("<Down>", lambda e: self.browseHistory(1))
        self.bind('<KeyRelease>', self.onKeyRelease)

    def enter(self, e):
        """The <Return> key press handler"""
        if self.processor.isRunning():
            return
        self.historyPos += len(self.history)
        self.processor.parse(self.read_last_line())
    
    def browseHistory(self, direction):
        """Browse through the command history and use the selected command."""
        newPosition = self.historyPos + direction
        if not -1 < newPosition < len(self.history):
            return "break"

        self.historyPos = newPosition
        cmd = self.history[self.historyPos]
        self.delete("committed_text", "end-1c")
        self.insert("committed_text", cmd)
        return "break"
    
    def onKeyRelease(self, event = None):
        if not self.processor.isRunning():
            try:
                self.history[self.historyPos] = self.read_last_line()
            except IndexError:
                self.history.insert(self.historyPos, self.read_last_line())
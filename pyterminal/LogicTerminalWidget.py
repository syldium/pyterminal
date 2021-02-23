# -*- coding: utf-8 -*-
from tkinter import Frame, Event
from typing import Callable, List

from .CmdProcessor import CmdProcessor
from .TerminalWidget import TerminalWidget


class LogicTerminalWidget(TerminalWidget):
    """Implement terminal logic."""

    def __init__(self, parent: Frame, cmd_processor: CmdProcessor = None, get_prompt: Callable[[], str] = None):
        TerminalWidget.__init__(self, parent, get_prompt)

        # Set the command processor
        self.processor = cmd_processor or CmdProcessor(self.write, self.prompt)
        
        self.history: List[str] = []  # Stored commands of the current session
        self.historyPos = 0  # Current position in the history

        self.bind("<Control-c>", self.processor.sigint)
        self.bind("<Return>", self.enter)
        self.bind("<Up>", lambda e: self.browse_history(-1))
        self.bind("<Down>", lambda e: self.browse_history(1))
        self.bind('<KeyRelease>', self.on_key_release)

    def enter(self, event: Event = None):
        """The <Return> key press handler"""
        if self.processor.is_running():
            return
        self.historyPos += len(self.history)
        self.processor.parse(self.read_last_line())

    def browse_history(self, direction: int) -> str:
        """Browse through the command history and use the selected command."""
        new_position = self.historyPos + direction
        if not -1 < new_position < len(self.history):
            return "break"

        self.historyPos = new_position
        cmd = self.history[self.historyPos]
        self.delete("committed_text", "end-1c")
        self.insert("committed_text", cmd)
        return "break"

    def on_key_release(self, event: Event = None) -> None:
        if not self.processor.is_running():
            try:
                self.history[self.historyPos] = self.read_last_line()
            except IndexError:
                self.history.insert(self.historyPos, self.read_last_line())

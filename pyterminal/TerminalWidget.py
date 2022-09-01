# -*- coding: utf-8 -*-
from hashlib import md5
from pathlib import Path
from typing import Callable, Dict

from .helpers import get_cmd_invite
from tkinter import END, RIGHT, LEFT, Frame, Event
from tkinter.scrolledtext import ScrolledText

import sys

class TerminalWidget(ScrolledText):
    """Custom widget based on the ScrolledText widget.
    Original: https://gist.github.com/olisolomons/e90d53191d162d48ac534bf7c02a50cd
    """

    def __init__(self, parent: Frame, get_prompt: Callable[[], Path] = None):
        ScrolledText.__init__(self, parent, **self.get_text_options())

        self.console_tags = []

        # Set the getter of the command prompt
        self.get_prompt = get_prompt or get_cmd_invite

        # Make edits that occur during on_text_change not cause it to trigger again
        def on_modified(event: Event):
            flag = self.edit_modified()
            if flag:
                self.after(10, self.on_text_change(event))
            self.edit_modified(False)

        self.bind("<<Modified>>", on_modified)

        self.committed_hash = None
        self.committed_text_backup = ""
        self.commit_all()

        self.mark_set("prompt_end", 1.0)

        # Aspects des �l�ments du prompt
        self.tag_config("prompt_user", foreground="#5FD300", 
                        selectbackground="#5FD300", selectforeground="black")
        self.tag_config("prompt_host", foreground="#4E9A06", 
                        selectbackground="#4E9A06", selectforeground="black")
        self.tag_config("prompt_cwd", foreground="#EA2E00", 
                        selectbackground="#EA2E00", selectforeground="black")
        self.tag_config("prompt_@", foreground="white", 
                        selectbackground="white", selectforeground="black")
        self.tag_config("prompt_:", foreground="white", 
                        selectbackground="white", selectforeground="black")
        self.tag_config("prompt_$", foreground="white", 
                        selectbackground="white", selectforeground="black")

#         self.prompt()

    def prompt(self, cwd: str) -> None:
        """Insert a prompt"""
        self.mark_set("prompt_end", 'end-1c')
        self.mark_gravity("prompt_end", LEFT)
        u, h, d = self.get_prompt(Path(cwd))
        
        if sys.platform == "win32":
            self.write(d, "prompt_cwd")
            self.write(">", "prompt_$")
        else:
            self.write(u, "prompt_user")
            self.write("@", "prompt_@")
            self.write(h, "prompt_host")
            self.write(":", "prompt_:")
            self.write(d, "prompt_cwd")
            self.write("$", "prompt_$")
        
        self.write(" ", "log")
        self.mark_gravity("prompt_end", RIGHT)

    def commit_all(self) -> None:
        """Mark all text as committed"""
        self.commit_to('end-1c')

    def commit_to(self, pos: str) -> None:
        """Mark all text up to a certain position as committed"""
        if self.index(pos) in (self.index("end-1c"), self.index("end")):
            # don't let text become un-committed
            self.mark_set("committed_text", "end-1c")
            self.mark_gravity("committed_text", LEFT)
        else:
            # if text is added before the last prompt, update the stored position of the tag
            for i, (tag_name, _, _) in reversed(list(enumerate(self.console_tags))):
                if "prompt" in tag_name:
                    tag_ranges = self.tag_ranges(tag_name)
                    self.console_tags[i] = (tag_name, tag_ranges[-2], tag_ranges[-1])
                    break

        # update the hash and backup
        self.committed_hash = self.get_committed_text_hash()
        self.committed_text_backup = self.get_committed_text()

    def get_committed_text_hash(self) -> bytes:
        """Get the hash of the committed area - used for detecting an attempt to edit it"""
        return md5(self.get_committed_text().encode()).digest()

    def get_committed_text(self) -> str:
        """Get all text marked as committed"""
        return self.get(1.0, "committed_text")

    def write(self, string: str, tag_name: str, pos: str = 'end-1c', **kwargs):
        """Write some text to the console"""

        # get position of the start of the text being added
        start = self.index(pos)

        # insert the text
        self.insert(pos, string)
        self.see(END)

        # commit text
        self.commit_to(pos)

        # color text
        self.tag_add(tag_name, start, pos)
        self.tag_config(tag_name, **kwargs)

        # save color in case it needs to be re-coloured
        self.console_tags.append((tag_name, start, self.index(pos)))

    def on_text_change(self, event: Event = None):
        """If the text is changed, check if the change is part of the committed text, and if it is revert the change"""
        if self.get_committed_text_hash() != self.committed_hash:
            # revert change
            self.mark_gravity("committed_text", RIGHT)
            self.replace(1.0, "committed_text", self.committed_text_backup)
            self.mark_gravity("committed_text", LEFT)

            # re-apply colours
            for tag_name, start, end in self.console_tags:
                self.tag_add(tag_name, start, end)

    def read_last_line(self) -> str:
        """Read the user input, i.e. everything written after the committed text"""
        return self.get("committed_text", "end-1c")

    def consume_last_line(self) -> str:
        """Read the user input as in read_last_line, and mark it is committed"""
        line = self.read_last_line()
        self.commit_all()
        return line

    def get_text_options(self) -> Dict[str, str]:
        return {"bg": "black",
                "fg": "white",
                "insertbackground": "#08c614",
                "selectbackground": "#fcfcfc"}

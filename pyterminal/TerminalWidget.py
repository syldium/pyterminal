from hashlib import md5
from .helpers import getCmdInvite
from tkinter import END, RIGHT, LEFT
from tkinter.scrolledtext import ScrolledText

"""
Custom widget based on the ScrolledText widget.
Use of https://gist.github.com/olisolomons/e90d53191d162d48ac534bf7c02a50cd
"""
class TerminalWidget(ScrolledText):

    def __init__(self, parent, getPrompt = None):
        ScrolledText.__init__(self, parent, **self.getTextOptions())

        self.console_tags = []

        # Set the getter of the command prompt
        if getPrompt is None:
            getPrompt = getCmdInvite
        self.getPrompt = getPrompt

        # Make edits that occur during on_text_change not cause it to trigger again
        def on_modified(event):
            flag = self.edit_modified()
            if flag:
                self.after(10, self.on_text_change(event))
            self.edit_modified(False)
        self.bind("<<Modified>>", on_modified)

        self.committed_hash = None
        self.committed_text_backup = ""
        self.commit_all()

        self.mark_set("prompt_end", 1.0)

        self.tag_config("prompt", foreground="#4E9A06", selectbackground="#4E9A06", selectforeground="black")

        self.prompt()
    
    def prompt(self):
        """Insert a prompt"""
        self.mark_set("prompt_end", 'end-1c')
        self.mark_gravity("prompt_end", LEFT)
        self.write(self.getPrompt(), "prompt")
        self.write(" ", "log")
        self.mark_gravity("prompt_end", RIGHT)

    def commit_all(self):
        """Mark all text as committed"""
        self.commit_to('end-1c')

    def commit_to(self, pos):
        """Mark all text up to a certain position as committed"""
        if self.index(pos) in (self.index("end-1c"), self.index("end")):
            # don't let text become un-committed
            self.mark_set("committed_text", "end-1c")
            self.mark_gravity("committed_text", LEFT)
        else:
            # if text is added before the last prompt, update the stored position of the tag
            for i, (tag_name, _, _) in reversed(list(enumerate(self.console_tags))):
                if tag_name == "prompt":
                    tag_ranges = self.tag_ranges("prompt")
                    self.console_tags[i] = ("prompt", tag_ranges[-2], tag_ranges[-1])
                    break

        # update the hash and backup
        self.committed_hash = self.get_committed_text_hash()
        self.committed_text_backup = self.get_committed_text()

    def get_committed_text_hash(self):
        """Get the hash of the committed area - used for detecting an attempt to edit it"""
        return md5(self.get_committed_text().encode()).digest()

    def get_committed_text(self):
        """Get all text marked as committed"""
        return self.get(1.0, "committed_text")

    def write(self, string, tag_name, pos='end-1c', **kwargs):
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

        # save color in case it needs to be re-colured
        self.console_tags.append((tag_name, start, self.index(pos)))

    def on_text_change(self, event):
        """If the text is changed, check if the change is part of the committed text, and if it is revert the change"""
        if self.get_committed_text_hash() != self.committed_hash:
            # revert change
            self.mark_gravity("committed_text", RIGHT)
            self.replace(1.0, "committed_text", self.committed_text_backup)
            self.mark_gravity("committed_text", LEFT)

            # re-apply colours
            for tag_name, start, end in self.console_tags:
                self.tag_add(tag_name, start, end)

    def read_last_line(self):
        """Read the user input, i.e. everything written after the committed text"""
        return self.get("committed_text", "end-1c")

    def consume_last_line(self):
        """Read the user input as in read_last_line, and mark it is committed"""
        line = self.read_last_line()
        self.commit_all()
        return line

    def getTextOptions(self):
        return {"bg": "black",
             "fg": "white",
             "insertbackground": "#08c614",
             "selectbackground": "#fcfcfc"}
from subprocess import Popen, PIPE
from threading import Thread

"""
Execute commands separately.
"""
class CmdProcessor:

    def __init__(self, writer, hook):
        self.command = "" # Actual command
        self.popen = None # Reference to the Popen object
        self.running = False # Is a command running
        self.writer = writer # stdout
        self.onEnd = hook # Will be triggered when a command is completed
        self.working_dir = "."

    def show(self, message):
        """Inserts message into the Text wiget"""
        self.writer(message, "log")

    def parse(self, command):
        self.show(" " + command + "\n")
        if "cd " in command:
            vals = command.split(" ")
            if vals[1][0] == "/":
                self.working_dir = vals[1]
            else:
                self.working_dir = self.working_dir + "/" + vals[1]
            self.show("\n")
            self.onEnd()
            return False
        else:
            self.start_thread(command)
            return True

    def start_thread(self, command):
        """Run a new command"""
        self.stop() # Make sure everything is empty
        self.running = True
        self.command = command
        Thread(target=self.process).start() # Start new process
    
    def process(self):
        while self.running:
            self.execute()
    
    def execute(self):
        try:
            # self.popen is a Popen object
            self.popen = Popen(self.command.split(), stdout=PIPE, bufsize=1, cwd=self.working_dir)
            lines_iterator = iter(self.popen.stdout.readline, b"")

            # poll() return None if the process has not terminated
            # otherwise poll() returns the process's exit code
            while self.popen.poll() is None:
                for line in lines_iterator:
                    self.show(line.decode())
            self.show("\n")
            print("Process `" + self.command  + "` terminated")
        except FileNotFoundError:
            self.show("Unknown command: " + self.command + "\n\n")                          
        except IndexError:
            self.show("No command entered\n\n")

        self.stop()
        self.onEnd()

    def stop(self):
        if self.popen:
            try:
                self.popen.kill()
            except ProcessLookupError:
                pass 
        self.running = False
# -*- coding: utf-8 -*-
import os
from pathlib import Path
import signal
import sys
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
import select
from typing import Optional, Callable, Any

if sys.platform == "win32":
    import msvcrt

class CmdProcessor:
    """Execute commands separately."""

    def __init__(self, writer: Callable[[str, str], Any], hook: Callable[[str], Any]):
        self.command = ""  # Actual command
        self.popen: Optional[Popen] = None  # Reference to the Popen object
        self.running = False  # Is a command running
        self.writer = writer  # stdout
        self.onEnd = lambda :hook(self.working_dir)  # Will be triggered when a command is completed
        self.working_dir = os.getcwd() #"."
        self.encoding = "cp437"#sys.stdout.encoding
        self.onEnd()

    def show(self, message: str) -> None:
        """Inserts message into the Text widget"""
        self.writer(message, "log")

    def parse(self, command: str) -> bool:
        self.start_thread(command)
        return True

    def start_thread(self, command: str) -> None:
        """Run a new command"""
        self.stop()  # Make sure everything is empty
        self.running = True
        self.command = command
        Thread(target=self.process).start()  # Start new process

    def process(self) -> None:
        while self.running:
            self.execute()

    def execute(self) -> None:
        if not self.command.strip():
            pass
        argv = self.command.split()
        argc = len(argv)
        executable = argv[0]
        stdin = sys.stdin.fileno()
        print("cwd", os.getcwd())
        if executable == "cd":
            if argc == 1:
                path = Path.home()
            else:
                path = os.path.abspath(os.path.join(self.working_dir, argv[1]))
            if os.path.exists(path):
                self.working_dir = path
            else:
                self.show("No such file or directory\n")
        elif sys.platform == "win32" and os.path.isdir(self.command):
            self.working_dir = os.path.abspath(self.command)
            
        else:
            try:
                self.popen = Popen(
                    self.command,
                    cwd=self.working_dir,
                    shell=True,
                    stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                    bufsize=1,
                    preexec_fn=os.setsid,
                    # universal_newlines=True,
                    # encoding=self.encoding,
                )
                
                with self.popen.stdout as pipe:
                    for line in iter(pipe.readline, b''):
                        self.show(line.decode(self.encoding))
                
                
#                 lines_iterator = iter(self.popen.stdout.readline, b"")
#     
#                 # poll() return None if the process has not terminated
#                 # otherwise poll() returns the process's exit code
#                 while self.popen.poll() is None:
#                     for line in lines_iterator:
#                         print(line.decode('unicode_escape').encode().decode("utf-8"))
#                         self.show(line)#.decode(self.encoding))

                    if sys.platform == "win32":
                        if msvcrt.kbhit(): 
                            self.popen.communicate(os.read(stdin, 1024))
                             
                    else:
                        # Ne fonctionne as sous Windows car stdin n'est pas un socket :
                        r, _, _ = select.select([sys.stdin], [], [], 0.2)
                        if sys.stdin in r:
                            self.popen.communicate(os.read(stdin, 1024))    
                        
                print("Process `" + self.command + "` terminated")
                
            except FileNotFoundError:
                self.show("Unknown command: " + self.command + "\n")
                
            except PermissionError:
                self.show("Access denied: " + self.command + "\n")
                
            except IndexError:
                self.show("No command entered\n")
                
            
    #         except:
    #             self.show("Unknown error (" + self.command + ")\n")
            
            
        self.stop()
        self.onEnd()

    def sigint(self, event=None) -> None:
        if self.popen:
            print("Sending keyboard interrupt signal")
            if sys.platform == "linux":
                os.killpg(self.popen.pid, signal.SIGINT)
            else:
                os.killpg(self.popen.pid, signal.CTRL_C_EVENT)

    def stop(self) -> None:
        if self.popen:
            try:
                self.popen.kill()
            except ProcessLookupError:
                pass
        self.running = False

    def is_running(self) -> bool:
        return self.running

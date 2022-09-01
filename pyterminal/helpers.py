# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Tuple

try:
    from getpass import getuser
    from socket import gethostname

except ModuleNotFoundError:  # Windows issues with pwd
    print("Warning: Unable to retrieve current connection information, use placeholders.")
    getuser = lambda: "user"
    gethostname = lambda: "hostname"


def get_cmd_invite(cwd: Path) -> Tuple[str, str, str]:
    working_directory = str(cwd)
    if cwd.is_relative_to(Path.home()):
        working_directory = '~' / cwd.relative_to(Path.home())
    return getuser(), gethostname(), working_directory

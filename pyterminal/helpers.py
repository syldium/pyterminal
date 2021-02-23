try:
    from getpass import getuser
    from socket import gethostname

except ModuleNotFoundError:  # Windows issues with pwd
    print("Warning: Unable to retrieve current connection information, use placeholders.")
    getuser = lambda: "user"
    gethostname = lambda: "hostname"



def get_cmd_invite(cwd: str) -> str:
    return getuser() + "@" + gethostname() + ":"+cwd+"$"

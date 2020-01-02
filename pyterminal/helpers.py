from getpass import getuser
from socket import gethostname

def getCmdInvite():
    return getuser() + "@" + gethostname() + "$"
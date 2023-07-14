

from src.core import LockFile
from src.core.Docker import Docker


def init():
    LockFile.create()
    
    docker = Docker()

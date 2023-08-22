import os

from src.core import LockFile
from src.core.Docker import Docker


def init():
    LockFile.create()
    
    os.mkdir('packages')
    docker = Docker()

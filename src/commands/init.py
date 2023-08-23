import os

from src.core import LockFile
from src.core.Docker import Docker
from src.commands.install_pkg import install_pkg


def init():
    LockFile.create()
    
    os.mkdir('packages')
    docker = Docker()
    install_pkg('latex-base')
    install_pkg('l3backend')

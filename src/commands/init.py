import os

from src.core import LockFile
from src.core.Docker import Docker
from src.commands.install_pkg import install_pkg


def init():
    # TODO: Make it possible for user to specify his own Docker image to use
    if os.path.exists('packages') or os.path.exists('.lpmconf'):
        print(f"There is already a project in this folder")
        return
    
    Docker()

    LockFile.create()
    
    if not os.path.exists('packages'):
        os.mkdir('packages')

    
    install_pkg('latex-base')
    install_pkg('l3backend')

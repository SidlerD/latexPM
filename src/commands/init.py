import json
import os
import docker

from src.core import LockFile
from src.core import Docker
from src.commands.install_pkg import install_pkg
from src.helpers.Logger import make_logger

logger = make_logger()

def init(image_name: str):
    if os.path.exists('packages') and os.path.exists('.lpmconf'):
        print(f"There is already a project in this folder")
        return
    
    try:
        image_name = Docker.get_image(image_name)
    except docker.errors.ImageNotFound as e:
        logger.error(str(e))
        return

            
    with open('.lpmconf', 'w') as conffile:
        json.dump({'docker-id': image_name}, conffile)

    LockFile.create()
    
    if not os.path.exists('packages'):
        os.mkdir('packages')

    
    # TODO: Add other packages from bundle "required"
    install_pkg('latex-base')
    install_pkg('l3backend')

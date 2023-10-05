import json
import os
import docker

from src.core import LockFile
from src.core import Docker
from src.commands.install_pkg import install_pkg
from src.commands.install import install
from src.helpers.Logger import make_logger

logger = make_logger()

def init(image_name: str):
    if not os.path.exists('packages'):
        os.mkdir('packages')
    else:
        logger.debug("Packages folder already exists")

    lockfile_image = LockFile.get_docker_image()
    if lockfile_image and image_name:
        logger.error("You passed a docker image for lpm init, but the lockfile already specifies an image")
        return
    
    if LockFile.exists():
        logger.info("Lockfile detected. Initializing from Lockfile")
        # Pull the specified image
        try:
            Docker.get_image(lockfile_image)
        except docker.errors.ImageNotFound as e:
            logger.error("Invalid docker image in lock file")
        
        # Install packages from lockfile
        install()
        return 
    
    # Lockfile does not exist    
    try:
        image_name = Docker.get_image(image_name)
    except docker.errors.ImageNotFound as e:
        logger.error(str(e))
        return

    LockFile.create(image_name)
    
    # TODO: Add other packages from bundle "required"
    install_pkg('latex-base')
    install_pkg('l3backend')

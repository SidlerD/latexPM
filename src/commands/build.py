import json
import os
import docker
import logging
from src.core import LockFile

logger = logging.getLogger('default')

def build(args: list):
    client = docker.from_env()

    # Get container for this project
    image_id = LockFile.get_docker_image()
    if not image_id:
        logger.warn("Please initialize a project first")
        return

    # Run container and mount volume (containing project files and packages-folder)
    # vol_path = f"{os.path.join(os.getcwd(), 'packages')}:/root/lpm/packages"
    vol_path = f"{os.getcwd()}:/root/lpm"
    client.containers.run(
        image=image_id, 
        command=args, # Execute passed arguments in cmd
        # detach=True,
        volumes=[vol_path], # Make files in project dir available to container, put output there too
        environment={'TEXINPUTS': '.:/root/lpm/packages//'}, # Set TEXINPUTS to include volume path
        working_dir='/root/lpm'
        # user='root'
        # remove=True # Delete container when build is over
    )
    
    # TODO: Show build process without detaching container

import os
import docker
import logging
from src.core import LockFile

logger = logging.getLogger('default')


def build(args: list):
    """Compile the project

    Args:
        args (list): Commands to execute for compiling the project. E.g. ['pdflatex', 'file.tex']
    """
    client = docker.from_env()

    # Get container for this project
    image_id = LockFile.get_docker_image()
    if not image_id:
        logger.warn("Please initialize a project first")
        return

    # Run container and mount volume (containing project files and packages-folder)
    vol_path = f"{os.getcwd()}:/root/lpm"
    client.containers.run(
        image=image_id,
        command=args,  # Execute passed arguments in cmd
        volumes=[vol_path],  # Make files in project dir available to container, put output there too
        environment={'TEXINPUTS': '.:/root/lpm/packages//'},  # Set TEXINPUTS to include volume path
        working_dir='/root/lpm',
        remove=True  # Delete container when build is over
    )

    # URGENT: Show logs

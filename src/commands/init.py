import os

import docker

from src.commands.install import install
from src.commands.install_pkg import install_pkg
from src.core import Docker, LockFile
from src.helpers.Logger import make_logger

logger = make_logger()


def init(image_name: str):
    """Initialize a new project from scratch or from lockfile if present

    Args:
        image_name (str): Docker image to use for this project. Needs to have latex installed
    """
    if not os.path.exists('packages'):
        os.mkdir('packages')
    else:
        logger.debug("Packages folder already exists")

    if LockFile.exists():
        lockfile_image = LockFile.get_docker_image()
        if image_name:
            logger.error("You passed a docker image to lpm init, but the lockfile already exists")
            return
        if not lockfile_image:
            logger.error("Lockfile does not specify a Docker image. Cannot use lockfile to initialize project")
            return

        logger.info("Lockfile detected. Initializing from Lockfile")

        # Install packages from lockfile
        install()
        return

    # Lockfile does not exist: Figure out docker image to use and pull it
    try:
        image_name = Docker.get_image(image_name)
    except docker.errors.ImageNotFound as e:
        logger.error(str(e))
        return

    LockFile.create(image_name)

    # Download from VPTAN because for some obscure reason,
    # requests.get with latex-base from CTAN just never terminates
    install_pkg('latex-base', accept_prompts=True, src='VPTAN')
    install_pkg('l3backend', accept_prompts=True)

    # Needed by graphics.sty, throws error otherwise. E.g. when installing and then using tikz
    install_pkg('graphics-cfg', accept_prompts=True)
    install_pkg('graphics-def', accept_prompts=True)

    # TODO: Possibly add other packages from bundle "required"

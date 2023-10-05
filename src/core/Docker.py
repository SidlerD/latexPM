import json
import datetime as dt
from src.helpers.Logger import make_logger
import docker

logger = make_logger()

def get_image(image_name: str) -> str:
    """If not provided, figure out a suitable docker-image. Pull image"""
    client = docker.from_env()
    
    if not image_name:
        logger.info(f"Searching for and pulling Docker image. This can take a long time")

        image_url_format = 'registry.gitlab.com/islandoftex/images/texlive:TL%d-%d-%02d-%02d-small'
        
        curr_date = dt.date.today()

        possible_image_names = []
        last_date = curr_date - dt.timedelta(days=8)
        while curr_date > last_date:
            possible_image_names.append(image_url_format % (curr_date.year, curr_date.year, curr_date.month, curr_date.day))
            possible_image_names.append(image_url_format % (curr_date.year - 1, curr_date.year, curr_date.month, curr_date.day))

            curr_date -= dt.timedelta(days=1)

        # Find name that exists
        found = False
        for image_name in possible_image_names:
            try:
                client.images.pull(image_name)
                found = True
                break
            except docker.errors.NotFound:
                pass

        if not found:
            raise docker.errors.ImageNotFound("Couldn't find a suitable Docker image to use.")
        
        logger.info(f"Using {image_name} as Docker Image")

    elif image_name:
        logger.info(f"Pulling {image_name}. This can take a long time the first time it is done")
        client.images.pull(image_name)
        logger.debug("Docker image pulled successfully")

    return image_name
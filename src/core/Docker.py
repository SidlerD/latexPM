import json
import datetime as dt
from src.helpers.Logger import make_logger
import docker

logger = make_logger()

class Docker:
    def __init__(self) -> None:
        client = docker.from_env()
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
        for name in possible_image_names:
            try:
                client.images.get(name)
                found = True
                break
            except docker.errors.ImageNotFound:
                pass

        if not found:
            logger.error("Couldn't find a suitable Docker image to use. Please edit .lpmconf and specify a image-id")
            raise Exception()
            
        logger.info(f"Using {name} as Docker Image")

        
        with open('.lpmconf', 'w') as conffile:
            json.dump({'docker-id': name}, conffile)

import json
import os
from os.path import join
import docker

class Docker:
    def __init__(self) -> None:
        """Create Dockerfile in cwd, build and run container"""
        self.name = os.path.basename(os.path.dirname(p=os.getcwd())).lower()
        self._client = docker.from_env()
        self.container = self._create_container()

    def _create_container(self):
        path = _create_Dockerfile()
        self.image, _ = self._client.images.build(path=path, tag=f"lpm/{self.name}")

        with open('.lpmconf', 'a') as conffile:
            json.dump({'docker-id': self.image.id}, conffile)
            
        return self._client.containers.run(
            image=self.image.id, 
            # command='watch "date >> /var/log/date.log"',
            detach=True
            # volumes=[f"{join(os.getcwd(), 'packages')}:/root/lpm/packages"]
        )




def _create_Dockerfile():
    with open("Dockerfile", "w") as f:
        settings = [
            'FROM ubuntu',
            'RUN apt-get update && apt-get install -y texlive-latex-base',
            'CMD ["echo", "hello"]'
        ]

        f.write('\n\n'.join(settings))

    return os.getcwd()

if __name__ == '__main__':
    Docker()
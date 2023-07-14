import os
import docker

class Docker:
    def __init__(self) -> None:
        self.name = os.path.basename(os.path.dirname(p=os.getcwd()))
        self.client = docker.from_env()
        self.container = self._create_container()

    def _create_container(self):
        path = _create_Dockerfile()
        self.image, _ = self.client.images.build(path=path, tag=f"lpm/{self.name}")
        self.client.containers.run(self.image.id)


def _create_Dockerfile():
    with open("Dockerfile", "w") as f:
        settings = [
            'FROM ubuntu',
            'CMD ["echo", "hello"]'
        ]

        f.write('\n\n'.join(settings))

    return os.getcwd()
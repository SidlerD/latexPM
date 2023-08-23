import json
import os
import docker


def build(args: list):
    client = docker.from_env()

    # Get container for this project
    if not os.path.exists('.lpmconf'):
        print('Please initialize a new project first using "lpm init"')

    with open('.lpmconf', 'r') as conffile:
        conf = json.load(conffile)
        image_id = conf['docker-id']
    
    # print(f"Executing {' '.join(args)} in container {container.id}")

    # Run container and mount volume (containing project files and packages-folder)
    # vol_path = f"{os.path.join(os.getcwd(), 'packages')}:/root/lpm/packages"
    vol_path = f"{os.getcwd()}:/root/lpm"
    container = client.containers.run(
        image=image_id, 
        command=args, # Execute passed arguments in cmd
        detach=True,
        volumes=[vol_path],
        environment={'TEXINPUTS': '.:/root/lpm/packages//'}, # Set TEXINPUTS to include volume path
        working_dir='/root/lpm',
        # remove=True # Delete container when build is over
    )

if __name__ == '__main__':
    build()
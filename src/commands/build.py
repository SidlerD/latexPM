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

if __name__ == '__main__':
    build()
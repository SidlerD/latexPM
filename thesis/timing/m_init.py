import cProfile
import os
import shutil
import sys
import time
import tempfile
from src.core import LockFile
from src.commands.init import init
import docker

client = docker.from_env()
docker_image = 'registry.gitlab.com/islandoftex/images/texlive:TL2023-2023-08-27-small'

tmp_dir = tempfile.mkdtemp()
old_cwd = os.getcwd()

filename = 'init.dat'

def _setup():
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)

    os.chdir(tmp_dir)
    try:
        client.images.remove(image=docker_image, force=True)
    except:
        print("Image already removed")

def _cleanup():
    os.chdir(old_cwd)
    shutil.rmtree(tmp_dir)
    LockFile._root = None
    # Remove pulled image
    try:
        client.images.remove(image=docker_image, force=True)
    except:
        print("Image already removed")

def _main():
    init(image_name=docker_image)

def _exec_init_n_times(n):
    for i in range(n):
        print(f"=== Iteration {i+1}/{n} of init ===")
        _setup()
        try:
            _main()
        except:
            pass
        _cleanup()

def measure(n):
    cProfile.runctx(f'_exec_init_n_times({n})', globals=globals(), locals=locals(), filename=filename)

if __name__ == '__main__':
    n = sys.argv[1] if len(sys.argv) == 2 else 30
    measure(n)
    
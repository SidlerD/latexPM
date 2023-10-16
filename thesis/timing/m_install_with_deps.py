import cProfile
import os
import shutil
import sys
import tempfile
from src.core import LockFile
from src.commands.install_pkg import install_pkg

tmp_dir = tempfile.mkdtemp()
old_cwd = os.getcwd()

filename = 'install_with_deps.dat'
pkg_to_install = 'listings'

def _setup():
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    os.chdir(tmp_dir)

def _cleanup():
    os.chdir(old_cwd)
    shutil.rmtree(tmp_dir)
    LockFile._root = None

def _main():
    install_pkg(pkg_id=pkg_to_install, accept_prompts=True)

def _exec_install_n_times(n):
    for i in range(n):
        print(f"=== Iteration {i+1}/{n} of installing {pkg_to_install} ===")
        _setup()
        try:
            _main()
        except:
            pass
        _cleanup()

def measure(n):
    cProfile.runctx(f'_exec_install_n_times({n})', globals=globals(), locals=locals(), filename=filename)

if __name__ == '__main__':
    n = sys.argv[1] if len(sys.argv) == 2 else 30
    measure(n)
    
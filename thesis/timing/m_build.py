import cProfile
import os
import shutil
import sys
import time
import tempfile
from src.core import LockFile
from src.commands.install_pkg import install_pkg
from src.commands.init import init
from src.commands.build import build

tmp_dir = tempfile.mkdtemp()
old_cwd = os.getcwd()

filename = 'install_with_deps.dat'
docker_image = 'registry.gitlab.com/islandoftex/images/texlive:TL2023-2023-08-20-small'

def _setup():
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    os.chdir(tmp_dir)

    # Initialize a project (pulls docker image to build in + required packages)
    init(image_name=docker_image)

    # Install needed package (+ dependencies)
    install_pkg(pkg_id='listings')

    # Create file that lpm will need to build
    with open('file.tex', 'w') as texfile:
        file_content = '\n'.join(
            [
                r'\documentclass{article}',
                r'\usepackage{listings}',
                r'\begin{document}',
                r'\begin{lstlisting}[language=python]',
                    r'def my_func(decision:bool, i: int):',
                    r'    return i if decision else 0',
                r'\end{lstlisting}',
                r'\end{document}'
            ])
        texfile.write(file_content)

def _cleanup():
    os.chdir(old_cwd)
    shutil.rmtree(tmp_dir)

def _main():
    build('pdflatex file.tex')
    print([e for e in os.listdir() if os.path.isfile(e)])
def _exec_build_n_times(n):
    _setup()
    for i in range(n):
        print(f"=== Iteration {i+1}/{n} of building project ===")
        try:
            _main()
        except Exception as e:
            print(f"ERROR: {str(e)}")
    _cleanup()

def measure(n):
    cProfile.runctx(f'_exec_build_n_times({n})', globals=globals(), locals=locals(), filename=filename)

if __name__ == '__main__':
    n = sys.argv[1] if len(sys.argv) == 2 else 30
    measure(n)
    
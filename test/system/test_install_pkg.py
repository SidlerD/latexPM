import os
import shutil
import unittest
from unittest.mock import patch, call
from src.commands.remove import remove
from src.models.Dependency import Dependency, DownloadedDependency
from src.core import LockFile
from src.core.lpm import lpm
from anytree import Node
import tempfile
from parameterized import parameterized


class InstallPkgTest(unittest.TestCase):

    def setUp(self):
        # Store the current working directory
        self.original_cwd = os.getcwd()

        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        # self.test_dir = os.path.abspath('testdir')
        # os.mkdir(self.test_dir)
        # os.chmod(self.test_dir, 0o755)

    def tearDown(self):
        # Change the working directory back to the original path
        os.chdir(self.original_cwd)

        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

        LockFile._root = None


    # FIXME: Test with tikz and todonotes fail because of known issue: 
    #   A package requests "epstopdf-base", but lpm can't find it on CTAN
    #   because it is in package "epstopdf-pkg"
    @parameterized.expand([
    #   [pkg_name,      text]
        ["amsmath",     '\\begin{equation*}\n  a=b\n\\end{equation*}'],
        ["listings",   '\\begin{lstlisting}\n    import numpy as np\n\\end{lstlisting}'],
        ["tikz",        '\\begin{tikzpicture}\n    \\filldraw[color=red!60, fill=red!5, very thick](-1,0) circle (1.5);\n\\end{tikzpicture}'],
        ["hyperref",    'The following link is clickable thanks to hyperref: \\url{http://stackoverflow.com/}'],
        ["multirow",    '\\begin{tabular}{c|c}\n\\multicolumn{2}{c}{spans two rows}\\\\ \n 1 & 2 \\\\ \n\\end{tabular}'],
        ["todonotes",   '\\todo{This is a todo}'],
        ["siunitx",     'Scientific number: \\num{.3e45}'],
    ])
    @patch("src.API.CTAN.input")
    @patch("src.core.PackageInstaller.input")
    def test_install_packages_and_build_file(self, pkg_name, text, install_closest_version_input, build_aliases_file_input):
        os.chdir(self.test_dir)
        self.assertFalse(os.path.exists('file.pdf'))

        install_closest_version_input.return_value = 'y'
        build_aliases_file_input.return_value = 'n'


        # Create the file that uses the package
        file_content = '\n'.join(
            [
                r'\documentclass{article}',
                '\\usepackage{%s}' % pkg_name,
                r'\begin{document}',
                text,
                r'\end{document}'
            ])
        
        with open('file.tex', 'w') as f:
            f.write(file_content)
        
        # Initialize a project with lpm
        lpm_inst = lpm()
        lpm_inst.init()

        # Install the needed package
        lpm_inst.install_pkg(pkg_name, accept_prompts=True)

        # Build the project
        lpm_inst.build(['pdflatex', 'file.tex'])
        remove(pkg_name, by_user=False)

        # Print log-file(s)
        if os.path.exists('file.log'):
            with open('file.log', 'r') as log:
                print(log.read())
        else:
            print('file.log does not exist')
            files = [file for file in os.listdir() if os.path.isfile(file)]
            log_files = [file for file in files if file.endswith('.log')]
            print(f"Files in directory: {', '.join(files)}")
            for file in log_files:
                if not os.path.exists(file):
                    continue
                with open(file, 'r') as log:
                    print(f"==== {file} =====")
                    print(log.read())

        # Check that pdf was created
        self.assertTrue(os.path.exists('file.pdf'))

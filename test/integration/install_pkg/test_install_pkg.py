import os
import shutil
import unittest
from unittest.mock import MagicMock, patch, call
from src.core import LockFile
from src.models.Dependency import Dependency, DownloadedDependency
from src.core.lpm import lpm
from anytree import Node
import tempfile

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

    @patch("src.commands.install_pkg.LockFile.read_file_as_tree") # path to actual file because mocked methods are static
    @patch("src.commands.install_pkg.LockFile.write_tree_to_file") # path to actual file because mocked methods are static
    @patch("src.commands.install_pkg.CTAN.get_name_from_id")
    @patch("src.commands.install_pkg.PackageInstaller.install_specific_package")
    @patch("src.commands.install_pkg.extract_dependencies")
    def test_circular_dependencies_warns(self, extract_dependencies_mock, install_spec_pkg_mock, CTAN_mock, LockFile_write, LockFile_read):
        """Example where pkgA is dependent on B and pkgB is dependent on A\n
            Assert that installing pkgA only installs pkgA and pkgB once, and logs an info msg"""
        depA, depB = Dependency('A', 'A'), Dependency('B', 'B')

        extract_dependencies_mock.side_effect = lambda dep: [depB] if dep.id == 'A' else [depA]
        install_spec_pkg_mock.side_effect = lambda dep: DownloadedDependency(dep, "path", "https://download")
        CTAN_mock.return_value = ""
        LockFile_read.return_value = Node('root')
        LockFile_write.return_value = None
        
        with self.assertLogs('default', level='INFO') as cm:
            lpm_inst = lpm()
            lpm_inst.install_pkg("A")
            log_msg = "already installed as requested by the user"
            # Assert correct msg has been logged
            self.assertTrue(any([log_msg in log for log in cm.output]), 0)
            # Assert pkgA and pkgB were both installed only once
            self.assertEqual(install_spec_pkg_mock.call_count, 2)
            install_spec_pkg_mock.assert_has_calls([call(depA), call(depB)], any_order=False)


    @patch("src.API.CTAN.input")
    @patch("src.core.PackageInstaller.input") 
    def test_install_listings_and_build_file(self, install_closest_version_input, build_aliases_file_input):
        install_closest_version_input.return_value = 'y'
        build_aliases_file_input.return_value = 'n'

        os.chdir(self.test_dir)
        with open('file.tex', 'w') as f:
            f.write('\n'.join([
                r'\documentclass{article}',
                r'\usepackage{listings}',
                r'\begin{document}',
                r'\begin{lstlisting}',
                r'    import numpy as np',
                r'\end{lstlisting}',
                r'\end{document}'
            ]))
        lpm_inst = lpm()
        lpm_inst.init(docker_image='registry.gitlab.com/islandoftex/images/texlive:TL2023-2023-08-20-small')
        
        lpm_inst.install_pkg('listings')

        lpm_inst.build(['pdflatex', 'file.tex'])

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
        
        
        self.assertTrue(os.path.exists('file.pdf'))

    @patch("src.API.CTAN.input")
    @patch("src.core.PackageInstaller.input") 
    def test_install_amsmath_and_build_file(self, install_closest_version_input, build_aliases_file_input):
        install_closest_version_input.return_value = 'y'
        build_aliases_file_input.return_value = 'n'

        os.chdir(self.test_dir)
        with open('file.tex', 'w') as f:
            f.write('\n'.join([
                r'\documentclass{article}',
                r'\usepackage{amsmath}',
                r'\begin{document}',
                r'\begin{equation*}',
                r'  a=b',
                r'\end{equation*}',
                r'\end{document}'
            ]))
        lpm_inst = lpm()
        lpm_inst.init(docker_image='registry.gitlab.com/islandoftex/images/texlive:TL2023-2023-08-20-small')
        
        lpm_inst.install_pkg('amsmath')

        lpm_inst.build(['pdflatex', 'file.tex'])

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
        
        
        self.assertTrue(os.path.exists('file.pdf'))

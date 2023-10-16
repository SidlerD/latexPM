import os
from os.path import join
import shutil
import unittest
from unittest.mock import patch, call, ANY
from anytree import Node
import tempfile
from parameterized import parameterized
import filecmp

from src.core import LockFile
from src.models.Dependency import Dependency, DependencyNode, DownloadedDependency
from src.core.lpm import lpm


class ProjectIsolationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.old_cwd = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmp_dir)
        
    
    @parameterized.expand([
        ['amsmath', '2.17o', '2.17n'],
        ['tabularray', '2023-03-01', '2022-11-01'],
        ['biblatex', '3.18b', '3.18a']
    ])
    def test_two_projects_use_their_own_package_version(self, pkg_id, version1, version2):
        file_name, output_file_name, log_file_name = 'file.tex', 'file.pdf', 'file.log'

        # Setup proj1 and install package
        os.mkdir('proj1')
        os.chdir('proj1')

        ## Create new project
        self._create_file_using_package(file_name, pkg_id)
        lpm_inst = lpm()
        lpm_inst.init()

        ## Install package in version1
        lpm_inst.install_pkg(pkg_id, version=version1, accept_prompts=True)

        # Setup proj2 and install package
        ## Setup directory
        LockFile._root = None
        os.chdir('..')
        os.mkdir('proj2')
        os.chdir('proj2')

        ## Create new project
        self._create_file_using_package(file_name, pkg_id)
        lpm_inst = lpm()
        lpm_inst.init()

        ## Install package in version2
        lpm_inst.install_pkg(pkg_id, version=version2, accept_prompts=True)


        # Build project1
        os.chdir('..')
        os.chdir('proj1')
        lpm_inst.build(['pdflatex', file_name])
        # Check that pdf was produced
        self.assertIn(output_file_name, os.listdir())
        # Check that correct version was used 
        with open(log_file_name, 'r') as log:
            self.assertRegex(log.read(), f'{pkg_id}.*{version1}')

        # Build project2
        os.chdir('..')
        os.chdir('proj2')
        lpm_inst.build(['pdflatex', file_name])
        # Check that pdf was produced
        self.assertIn(output_file_name, os.listdir())
        # Check that correct version was used 
        with open(log_file_name, 'r') as log:
            self.assertRegex(log.read(), f'{pkg_id}.*{version2}')

        
    def _create_file_using_package(self, file_name: str, package: str):
        file_content = '\n'.join(
            [
                r'\year=2012',
                r'\month=12',
                r'\day=24',
                r'\time=180',
                r'\documentclass{article}',
                '\\usepackage{%s}' % package,
                r'\begin{document}',
                'This is a short text that appears in every document. This file was created automatically.',
                r'\end{document}'
            ])
        
        with open(file_name, 'w') as f:
            f.write(file_content)
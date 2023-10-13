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


class ReproducibilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.old_cwd = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmp_dir)
        
    
    @parameterized.expand([
        ['amsmath', ['amsmath'], '\\begin{equation*}\n  a=b\n\\end{equation*}'],
        ['tikz', ['tikz'], '\\begin{tikzpicture}\n    \\filldraw[color=red!60, fill=red!5, very thick](-1,0) circle (1.5);\n\\end{tikzpicture}'],
        ['3 packages', ['amsmath', 'listings', 'longtable'], '\\begin{equation*}\n  a=b\n\\end{equation*}\n\\begin{lstlisting}\n    import numpy as np\n\\end{lstlisting}'], 
        ['4 packages', ['hyperref', 'siunitx', 'multirow', 'url'], '\\url{https://www.example.com}\n\\SI{42}{\\meter}\n\\href{https://www.example.com}{Example Website}']
    ])
    def test_install_packages_from_lockfile_and_build(self, test_name, packages, text):
        file_name, output_file_name, engine = 'file.tex', 'file.dvi', 'latex'

        # Setup proj1, install packages and build pdf
        os.mkdir('proj1')
        os.chdir('proj1')

        ## Create new project
        self._create_file_using_packages(file_name, packages, text)
        lpm_inst = lpm()
        lpm_inst.init(docker_image='registry.gitlab.com/islandoftex/images/texlive:TL2023-2023-08-20-small')

        ## Install packages
        for package in packages:
            lpm_inst.install_pkg(package, accept_prompts=True)

        ## Build the project
        lpm_inst.build([engine, file_name])

        ## Check that pdf was produced
        self.assertIn(output_file_name, os.listdir())

        # Setup proj2, copy lockfile and tex-file, build
        ## Setup directory
        os.chdir('..')
        os.mkdir('proj2')
        LockFile._root = None

        ## Copy Lockfile and file.tex to new project
        shutil.copy(join('proj1', file_name), join('proj2', file_name))
        shutil.copy(join('proj1', 'requirements-lock.json'), join('proj2', 'requirements-lock.json'))

        os.chdir('proj2')

        ## Assert proj empty otherwise
        self.assertEqual(len(os.listdir()), 2)

        ## Install packages from Lockfile
        lpm_inst.init()
        ## Build project
        lpm_inst.build([engine, file_name])
        ## Check that pdf was produced
        self.assertIn(output_file_name, os.listdir())

        # Compare the two projects
        os.chdir('..') 
        dirs_equal = self.are_dir_trees_equal('proj1', 'proj2')
        self.assertTrue(dirs_equal)
    
    def are_dir_trees_equal(self, dir1, dir2):
        """
        Compare two directories recursively. Files in each directory are
        assumed to be equal if their names and contents are equal.

        @param dir1: First directory path
        @param dir2: Second directory path

        @return: True if the directory trees are the same and 
            there were no errors while accessing the directories or files, 
            False otherwise.

        Taken from https://stackoverflow.com/a/6681395/10657095 and adapted
        """

        # Compare contents of directories
        dirs_cmp = filecmp.dircmp(dir1, dir2, ignore=['requirements-lock.json'])
        diff = [f for f in dirs_cmp.diff_files if not f.endswith('.log')]
        if len(dirs_cmp.left_only)>0 or len(dirs_cmp.right_only)>0 or \
            len(dirs_cmp.funny_files)>0 or len(diff)>0:
            return False
        # Compare contents of files in directories 
        # Except .log files: They can contain paths to other files, which differs between projects
        common_files = [f for f in dirs_cmp.common_files if not f.endswith('.log')]
        (_, mismatch, errors) =  filecmp.cmpfiles(
            dir1, dir2, common_files, shallow=False)
        if len(mismatch)>0 or len(errors)>0:
            return False
        # Recursively compare all subdirectories
        for common_dir in dirs_cmp.common_dirs:
            new_dir1 = os.path.join(dir1, common_dir)
            new_dir2 = os.path.join(dir2, common_dir)
            if not self.are_dir_trees_equal(new_dir1, new_dir2):
                return False
        return True


    def _create_file_using_packages(self, file_name: str, packages: list[str], text: str):
        file_content = '\n'.join(
            [
                r'\year=2012',
                r'\month=12',
                r'\day=24',
                r'\time=180',
                r'\documentclass{article}',
                '\\usepackage{%s}' % ','.join(packages),
                r'\begin{document}',
                'This is a short text that appears in every document. This file was created automatically.',
                text,
                r'\end{document}'
            ])
        
        with open(file_name, 'w') as f:
            f.write(file_content)
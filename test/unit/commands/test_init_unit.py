import filecmp
import os
from os.path import join
import shutil
import tempfile
import unittest
from unittest.mock import patch

from src.commands.init import init
from src.core import LockFile


class Test_init_unit(unittest.TestCase):
    def setUp(self) -> None:
        self.old_cwd = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmp_dir)
    

    @patch('src.commands.init.install')
    @patch('src.commands.init.install_pkg')
    @patch('src.commands.init.os.mkdir')
    @patch('src.commands.init.Docker.get_image')
    def test_creates_packages_folder(self, docker_getimg, mk_dir, install_pkg, install_all):
        docker_getimg.return_value = 'image-name'
        
        init(image_name='')

        mk_dir.assert_called_once_with('packages')
    
    @patch('src.commands.init.install')
    @patch('src.commands.init.install_pkg')
    @patch('src.commands.init.Docker.get_image')
    def test_doesnt_overwrite_folder(self, docker_getimg, install_pkg, install_all):
        os.mkdir('packages')
        file_path = join('packages', 'file.txt')
        open(file_path, 'x').close()

        init(image_name='')

        self.assertTrue(os.path.exists(file_path))
        self.assertEqual(len(os.listdir('packages')), 1)
    
    @patch('src.commands.init.install')
    @patch('src.commands.init.install_pkg')
    @patch('src.commands.init.Docker.get_image')
    def test_LF_not_changed_on_init(self, docker_getimg, install_pkg, install_all):
        docker_img_used = 'my-pulled-image'
        docker_getimg.return_value = docker_img_used
        LF_name, LF_copy_name = LockFile.get_name(), 'copy_' + LockFile.get_name()
        LockFile.create(docker_image=docker_img_used)

        self.assertIn(LF_name, os.listdir())

        # Copy lockfile
        shutil.copy(LF_name, LF_copy_name)

        # Assert that old and new lockfile are equal after init, docker image used not changed
        init(image_name='')
        self.assertTrue(filecmp.cmp(LF_name, LF_copy_name, shallow=False))
        self.assertEqual(docker_img_used, LockFile.get_docker_image())

        # Assert that old and new lockfile are equal after init with image specified
        init(image_name='my-new-pulled-image')
        self.assertTrue(filecmp.cmp(LF_name, LF_copy_name, shallow=False))
        self.assertEqual(docker_img_used, LockFile.get_docker_image())


    @patch('src.commands.init.install')
    @patch('src.commands.init.install_pkg')
    @patch('src.commands.init.Docker.get_image')
    def test_LF_not_changed_on_init_empty_LF(self, docker_getimg, install_pkg, install_all):
        docker_img_used = None
        docker_getimg.return_value = 'some-other-image'
        LF_name, LF_copy_name = LockFile.get_name(), 'copy_' + LockFile.get_name()
        LockFile.create(docker_image=docker_img_used)

        # Copy lockfile
        shutil.copy(LF_name, LF_copy_name)

        # Assert that old and new lockfile are equal after init
        with self.assertLogs('default', level='WARN') as cm:
            init(image_name='')
            
            self.assertTrue(filecmp.cmp(LF_name, LF_copy_name, shallow=False))
            self.assertEqual(docker_img_used, LockFile.get_docker_image())

            self.assertTrue(any(["does not specify a Docker image" in log for log in cm.output]))
        
        # Assert that old and new lockfile are equal after init with image specified
        with self.assertLogs('default', level='WARN') as cm:
            init(image_name='my-new-pulled-image')
            self.assertTrue(filecmp.cmp(LF_name, LF_copy_name, shallow=False))
            self.assertEqual(docker_img_used, LockFile.get_docker_image())

            self.assertTrue(any(["lockfile already exists" in log for log in cm.output]))
    
    @patch('src.commands.init.install')
    @patch('src.commands.init.install_pkg')
    @patch('src.commands.init.Docker.get_image')
    def test_init_pulls_docker_image_from_LF(self, docker_getimg, install_pkg, install_all):
        docker_img_used = 'my-image'

        LockFile.create(docker_image=docker_img_used)

        init(image_name='')

        docker_getimg.assert_called_once_with(docker_img_used)

    @patch('src.commands.init.install')
    @patch('src.commands.init.install_pkg')
    def test_init_installs_from_LF_if_present(self, install_pkg, install_all):
        # Given LF that exists
        LockFile.create(docker_image='my-docker-image')

        # When init called
        init(image_name='')

        # Then only install is called, which installs from LF
        install_all.assert_called_once()
        install_pkg.assert_not_called()
        
    @patch('src.commands.init.install')
    @patch('src.commands.init.install_pkg')
    @patch('src.commands.init.Docker.get_image')
    def test_init_installs_required_pkgs_if_no_LF(self, docker_getimg, install_pkg, install_all):
        docker_getimg.return_value = 'my-image'

        # Assert no Lockfile exists
        self.assertFalse(os.listdir())
        self.assertFalse(LockFile.exists())

        init(image_name='')
        
        # Assert install_pkg was called, not install
        install_pkg.assert_called()
        install_all.assert_not_called()
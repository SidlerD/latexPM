import os
from os.path import join
import shutil
import unittest
from unittest.mock import patch, call, ANY
from anytree import Node
import tempfile
from src.core import LockFile

from src.models.Dependency import Dependency, DependencyNode, DownloadedDependency
from src.core.lpm import lpm


class InstallAllTest(unittest.TestCase):
    def setUp(self) -> None:
        self.old_cwd = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.tmp_dir)
        
    @patch("src.commands.install.input")
    @patch("src.commands.install.FileHelper.clear_and_remove_packages_folder")
    @patch("src.commands.install.Docker")
    @patch("src.commands.install.LockFile")
    @patch("src.commands.install.PackageInstaller.install_specific_package")
    def test_install_all_gets_right_files(self, install_spec_pkg_mock, Lockfile_mock, Docker_mock, FH_clear_folder, user_input_mock):
        """Install deps from Lockfile, then check that correct folders would have been created"""
        dep_ams = Dependency("amsmath", "amsmath", "v1.2a")
        down_dep = DownloadedDependency(dep_ams, "path", "https://download/amsmath", 'required/amsmath')
        rootNode = Node('root')
        dep_node = DependencyNode(down_dep, rootNode)

        install_spec_pkg_mock.side_effect = lambda dep: DownloadedDependency(dep, "path", "https://download/amsmath")
        Lockfile_mock.read.return_value = rootNode
        Lockfile_mock.get_docker_image.return_value = 'my-image'
        Lockfile_mock.get_packages_from_file.return_value = [dep_node]
        user_input_mock.return_value = 'y'  # User agrees to packages-folder being cleared

        lpm_inst = lpm()
        lpm_inst.install()

        # Assert only one package was installed
        self.assertEqual(install_spec_pkg_mock.call_count, 1)
        install_spec_pkg_mock.assert_has_calls([call(dep_node, accept_prompts=True)])

    @patch("src.commands.install.input")
    @patch("src.commands.install.FileHelper.clear_and_remove_packages_folder")
    @patch("src.commands.install.Docker")
    @patch("src.commands.install.LockFile")
    def test_install_creates_folder_and_downloads_files(self, Lockfile_mock, Docker_mock, FH_clear_folder, user_input_mock):
        dep_ams = Dependency("amsmath", "amsmath")

        Lockfile_mock.get_packages_from_file.return_value = [dep_ams]
        user_input_mock.return_value = 'y'  # User agrees to packages-folder being cleared

        os.mkdir('packages')
        self.assertEqual(0, len(os.listdir('packages')))  # Dir empty at beginning

        lpm_inst = lpm()
        lpm_inst.install()

        installed_packages = os.listdir('packages')
        self.assertEqual(1, len(installed_packages))

        installed_files = os.listdir(os.path.join('packages', installed_packages[0]))
        self.assertTrue(any(file.endswith(".sty") for file in installed_files))  # At least one .sty file downloaded
        self.assertTrue('amsmath.sty' in installed_files)
    
    @patch("src.commands.install.Docker")
    @patch("src.commands.install.LockFile")
    @patch("src.commands.install.FileHelper.clear_and_remove_packages_folder")
    @patch("src.commands.install.input")
    def test_input_no_terminates_execution(self, user_input_mock, FH_remove_folder_mock, LF_mock, docker_mock):

        os.mkdir('packages')
        open(join('packages', 'file.txt'), 'x').close()
        user_input_mock.return_value = 'n'  # User doesn't want packages folder to be cleared
        LockFile.create('my-image')

        with self.assertLogs('default', level='INFO') as cm:
            lpm_inst = lpm()
            lpm_inst.install()

            FH_remove_folder_mock.assert_not_called()
            LF_mock.get_packages_from_file.assert_not_called()
            self.assertTrue(any(["aborted" in log for log in cm.output]))

    @patch("src.commands.install.Docker")
    @patch("src.commands.install.input")
    def test_uses_url_from_lockfile_ctan(self, user_input_mock, docker_mock):
        user_input_mock.return_value = 'y'  # Agree to clearing package folder

        lpm_inst = lpm()
        LockFile.create('registry.gitlab.com/islandoftex/images/texlive:TL2023-2023-08-20-small')

        lpm_inst.install_pkg('amsmath', accept_prompts=True)
        amsmath_installed = LockFile.find_by_id('amsmath')
        self.assertIsNotNone(amsmath_installed)
        url = amsmath_installed.dep.url

        with patch("src.helpers.DownloadHelpers.requests") as requests_mock:
            lpm_inst.install()
            requests_mock.get.assert_called_once_with(url, allow_redirects=True)
        
        # Assert that url from LF is used, not just replicated by chance
        with patch("src.helpers.DownloadHelpers.requests") as requests_mock:
            amsmath_node = LockFile.find_by_id('amsmath')
            amsmath_node.dep.url = 'https://www.myurl.com/amsmath.zip'
            LockFile.write_tree_to_file()

            lpm_inst.install()
            requests_mock.get.assert_called_once_with('https://www.myurl.com/amsmath.zip', allow_redirects=True)


    @patch("src.commands.install.Docker")
    @patch("src.commands.install.input")
    def test_uses_url_from_lockfile_vptan(self, user_input_mock, docker_mock):
        user_input_mock.return_value = 'y'  # Agree to clearing package folder

        lpm_inst = lpm()
        LockFile.create('registry.gitlab.com/islandoftex/images/texlive:TL2023-2023-08-20-small')
        
        # Install amsmath in specific version, save the download url
        lpm_inst.install_pkg('amsmath', version='2.17j', accept_prompts=True)
        amsmath_installed = LockFile.find_by_id('amsmath')
        self.assertIsNotNone(amsmath_installed)
        url = amsmath_installed.dep.url

        # Assert that valid url from LF is used
        with patch("src.helpers.DownloadHelpers.requests") as requests_mock:
            lpm_inst.install()
            requests_mock.get.assert_called_once_with(url, allow_redirects=True)

        # Assert that url from LF is used, not just built using VPTAN resulting in the same URL
        with patch("src.helpers.DownloadHelpers.requests") as requests_mock:
            amsmath_node = LockFile.find_by_id('amsmath')
            amsmath_node.dep.url = 'https://www.myurl.com/amsmath.zip'
            LockFile.write_tree_to_file()

            lpm_inst.install()
            requests_mock.get.assert_called_once_with('https://www.myurl.com/amsmath.zip', allow_redirects=True)

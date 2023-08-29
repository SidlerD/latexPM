import os
import unittest
from unittest.mock import MagicMock, patch, call
from anytree import Node
import tempfile

from src.models.Dependency import Dependency, DependencyNode, DownloadedDependency
from src.core.lpm import lpm

class InstallAllTest(unittest.TestCase):

    
    @patch("src.commands.install.input") 
    @patch("src.commands.install.FileHelper.clear_and_remove_packages_folder") 
    @patch("src.commands.install.LockFile.read_file_as_tree") # path to actual file because mocked methods are static
    @patch("src.commands.install.LockFile.write_tree_to_file") # path to actual file because mocked methods are static
    @patch("src.commands.install.PackageInstaller.install_specific_package")
    def test_install_all_gets_right_files(self, install_spec_pkg_mock, LF_write, LF_read, FH_clear_folder, user_input_mock):
        """Install deps from Lockfile, then check that correct folders would have been created"""
        dep_ams = Dependency("amsmath", "amsmath", "v1.2a")
        down_dep = DownloadedDependency(dep_ams, "path", "https://download/amsmath", 'required/amsmath')
        rootNode = Node('root')
        DependencyNode(down_dep, rootNode)

        install_spec_pkg_mock.side_effect = lambda dep: DownloadedDependency(dep, "path", "https://download/amsmath")
        LF_read.return_value = rootNode
        LF_write.return_value = None
        user_input_mock.return_value = 'y' # User agrees to packages-folder being cleared
        
        lpm_inst = lpm()
        lpm_inst.install()

        # Assert only one package was installed
        self.assertEqual(install_spec_pkg_mock.call_count, 1)
        install_spec_pkg_mock.assert_has_calls([call(down_dep)])


    @patch("src.commands.install.input") 
    @patch("src.commands.install.LockFile.get_packages_from_file")
    @patch("src.commands.install.LockFile.write_tree_to_file")
    @patch("src.helpers.DownloadHelpers.config.get_package_dir")
    def test_install_creates_folder_and_downloads_files(self, get_pkg_dir, LF_write, LF_get_packages, user_input_mock):
        dep_ams = Dependency("amsmath", "amsmath")

        LF_get_packages.return_value = [dep_ams]
        LF_write.return_value = None
        user_input_mock.return_value = 'y' # User agrees to packages-folder being cleared

        with tempfile.TemporaryDirectory() as tempdir:
            get_pkg_dir.return_value = tempdir

            self.assertEqual(0, len(os.listdir(tempdir))) # Dir empty at beginning

            lpm_inst = lpm()
            lpm_inst.install()

            installed_packages = os.listdir(tempdir)
            self.assertEqual(1, len(installed_packages))

            installed_files = os.listdir(os.path.join(tempdir, installed_packages[0]))
            self.assertTrue(any(file.endswith(".sty") for file in installed_files)) # At least one .sty file downloaded

    @patch("src.commands.install.LockFile.get_packages_from_file")
    @patch("src.commands.install.FileHelper.clear_and_remove_packages_folder") 
    @patch("src.commands.install.input") 
    def test_input_no_terminates_execution(self, user_input_mock, FH_remove_folder_mock, LF_get_packages_mock):

        user_input_mock.return_value = 'n' # User doesn't want packages folder to be cleared

        with self.assertLogs('default', level='INFO') as cm:
            lpm_inst = lpm()
            lpm_inst.install()

            FH_remove_folder_mock.assert_not_called()
            LF_get_packages_mock.assert_not_called()
            self.assertTrue(any(["aborted" in log for log in cm.output]))




        
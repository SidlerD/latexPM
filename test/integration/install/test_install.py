import os
import unittest
from unittest.mock import MagicMock, patch, call
from anytree import Node
import tempfile

from src.models.Dependency import Dependency, DependencyNode, DownloadedDependency
from src.core.lpm import lpm

class InstallAllTest(unittest.TestCase):

    @patch("src.commands.install.LockFile.read_file_as_tree") # path to actual file because mocked methods are static
    @patch("src.commands.install.LockFile.write_tree_to_file") # path to actual file because mocked methods are static
    @patch("src.commands.install.PackageInstaller.install_specific_package")
    def test_install_all_gets_right_files(self, install_spec_pkg_mock, LF_write, LF_read):
        """Install deps from Lockfile, then check that correct folders would have been created"""
        dep_ams = Dependency("amsmath", "amsmath", "v1.2a")
        rootNode = Node('root')
        DependencyNode(dep_ams, rootNode)

        install_spec_pkg_mock.side_effect = lambda dep: DownloadedDependency(dep, "path", "https://download/amsmath")
        LF_read.return_value = rootNode
        LF_write.return_value = None
        
        print('DIR:    ' + os.getcwd())
        lpm_inst = lpm()
        lpm_inst.install()

        # Assert only one package was installed
        self.assertEqual(install_spec_pkg_mock.call_count, 1)
        install_spec_pkg_mock.assert_has_calls([call(dep_ams)])


    @patch("src.commands.install.LockFile.get_packages_from_file")
    @patch("src.commands.install.LockFile.write_tree_to_file")
    @patch("src.helpers.DownloadHelpers.config.get_package_dir")
    def test_install_creates_folder_and_downloads_files(self, get_pkg_dir, LF_write, LF_get_packages):
        dep_ams = Dependency("amsmath", "amsmath")

        LF_get_packages.return_value = [dep_ams]
        LF_write.return_value = None

        with tempfile.TemporaryDirectory() as tempdir:
            get_pkg_dir.return_value = tempdir

            self.assertEqual(0, len(os.listdir(tempdir))) # Dir empty at beginning

            lpm_inst = lpm()
            lpm_inst.install()

            installed_packages = os.listdir(tempdir)
            self.assertEqual(1, len(installed_packages))

            installed_files = os.listdir(os.path.join(tempdir, installed_packages[0]))
            self.assertTrue(any(file.endswith(".sty") for file in installed_files)) # At least one .sty file downloaded
import unittest
from unittest.mock import MagicMock, patch, call
from src.core import LockFile
from src.models.Dependency import Dependency, DownloadedDependency
from src.core.lpm import lpm
from anytree import Node

class InstallPkgTest(unittest.TestCase):

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
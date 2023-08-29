import unittest
from unittest.mock import MagicMock, patch
from src.models.Dependency import DependencyNode, Dependency, DownloadedDependency
from src.core.lpm import lpm
from anytree import Node

from src.models.Version import Version

class UpgradePkgTest(unittest.TestCase):


    @patch("src.commands.upgrade_pkg.LockFile.read_file_as_tree")
    @patch("src.commands.upgrade_pkg.CTAN.get_version")
    @patch("src.commands.upgrade_pkg.CTAN.get_name_from_id")
    def test_upgrade_warns_and_returns_if_in_newest_version(self, get_name_mock, get_version_mock, read_as_tree_mock):
        root = Node('root')
        dep_version = Version("v1.2a")
        dep = Dependency('A', '', dep_version)
        down_dep = DownloadedDependency(dep, "path", "https://download/A", 'contrib/A')
        dep_node = DependencyNode(down_dep, parent=root)


        get_name_mock.return_value = ""
        get_version_mock.return_value = dep_version
        read_as_tree_mock.return_value = root
        
        with self.assertLogs('default', level='WARNING') as cm:
            lpm_inst = lpm()
            lpm_inst.upgrade_pkg('A')
            self.assertEqual(len(cm.output), 1) # Warned once
            self.assertTrue("already in newest version" in cm.output[0])

    @patch("src.commands.upgrade_pkg.LockFile.read_file_as_tree")
    @patch("src.commands.upgrade_pkg.CTAN.get_name_from_id")
    def test_upgrade_warns_if_not_installed(self, get_name_mock, read_as_tree_mock):
        get_name_mock.return_value = ""
        read_as_tree_mock.return_value = Node('root')

        with self.assertLogs('default', level='WARNING') as cm:
            lpm_inst = lpm()
            lpm_inst.upgrade_pkg('A')
            self.assertEqual(len(cm.output), 1) # Warned once
            self.assertTrue("not possible" in cm.output[0])
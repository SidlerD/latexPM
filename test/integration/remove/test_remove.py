import unittest
from unittest.mock import MagicMock, call, patch
from src.models.Dependency import DependencyNode, Dependency, DownloadedDependency
from src.core.lpm import lpm
from anytree import Node

from src.models.Version import Version

class RemoveTest(unittest.TestCase):

    @patch("src.commands.remove.delete_pkg_files")
    @patch("src.commands.remove.LockFile.write_tree_to_file")
    @patch("src.commands.remove.LockFile.find_by_id")
    def test_remove_calls_delete_pkg(self, LF_find, LF_write, delete_pkg_files_mock):
        depA, depB = Dependency('A', 'A'), Dependency('B', 'B')
        filesA, filesB = ['filea.sty', 'filea2.sty'], ['fileb.sty', 'fileb2.sty']
        downDepA, downDepB = DownloadedDependency(depA, '', '', filesA), DownloadedDependency(depB, '', '', filesB)
        depNodeA = DependencyNode(dep=downDepA)
        depNodeB = DependencyNode(dep=downDepB, parent=depNodeA)

        delete_pkg_files_mock.return_value= None
        LF_find.return_value = depNodeA
        LF_write.return_value = None

        lpm_inst = lpm()
        lpm_inst.remove('A')
        self.assertEqual(delete_pkg_files_mock.call_count, 2)
        delete_pkg_files_mock.assert_has_calls([call(depNodeA), call(depNodeB)], any_order=True)
        

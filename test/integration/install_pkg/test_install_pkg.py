import os
import shutil
import tempfile
import unittest
from unittest.mock import call, patch

from anytree import Node

from src.core import LockFile
from src.core.lpm import lpm
from src.models.Dependency import Dependency, DownloadedDependency


class InstallPkgTest(unittest.TestCase):

    def setUp(self):
        # Store the current working directory
        self.original_cwd = os.getcwd()

        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        # self.test_dir = os.path.abspath('testdir')
        # os.chmod(self.test_dir, 0o755)

    def tearDown(self):
        # Change the working directory back to the original path
        os.chdir(self.original_cwd)

        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

        LockFile._root = None

    @patch("src.commands.install_pkg.CTAN.get_package_info")
    @patch("src.commands.install_pkg.CTAN.get_name_from_id")
    @patch("src.commands.install_pkg.PackageInstaller.install_specific_package")
    @patch("src.commands.install_pkg.extract_dependencies")
    def test_circular_dependencies_warns(self, extract_dependencies_mock, install_spec_pkg_mock, CTAN_id_to_name_mock, CTAN_pkg_info_mock):
        """Example where pkgA is dependent on B and pkgB is dependent on A\n
            Assert that installing pkgA only installs pkgA and pkgB once, and logs an info msg"""
        depA, depB = Dependency('A', 'A'), Dependency('B', 'B')

        extract_dependencies_mock.side_effect = lambda dep: [depB] if dep.id == 'A' else [depA]
        
        def PackageInstaller_sideeffect(dep, accept_prompts: bool = False, src=''):
            return DownloadedDependency(dep, "path", "https://download", 'path/on/ctan')
        install_spec_pkg_mock.side_effect = PackageInstaller_sideeffect
        CTAN_id_to_name_mock.return_value = ""
        CTAN_pkg_info_mock.return_value = {'ctan': {'path': '/path/on/ctan'}}

        with self.assertLogs('default', level='INFO') as cm:
            LockFile.create('')

            lpm_inst = lpm()
            lpm_inst.install_pkg("A", accept_prompts=True)
            log_msg = "already installed as requested by the user"
            # Assert correct msg has been logged
            self.assertTrue(any([log_msg in log for log in cm.output]), 0)
            # Assert pkgA and pkgB were both installed only once
            self.assertEqual(install_spec_pkg_mock.call_count, 2)
            install_spec_pkg_mock.assert_has_calls([call(depA, accept_prompts=True), call(depB, accept_prompts=True)], any_order=False)

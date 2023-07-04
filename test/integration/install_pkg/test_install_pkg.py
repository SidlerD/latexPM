import unittest
from unittest.mock import patch
# from src.models.Dependency import Dependency
from src.models.Dependency import Dependency
from src.core.lpm import lpm
print(Dependency)



class InstallPkgTest(unittest.TestCase):

    @patch("src.commands.install_pkg.extract_dependencies")
    @patch("src.commands.install_pkg.PackageInstaller.install_specific_package")
    @patch("src.commands.install_pkg.CTAN.get_name_from_id")
    def test_circular_dependencies_warns(self, extract_dependencies_mock, install_spec_pkg_mock, CTAN_mock):
        def side_effect_extract_dependencies(dep: Dependency):
            print(dep)
            if(dep.id == 'A'):
                return [Dependency('B', "")]
            if(dep.id == 'B'):
                return [Dependency('A', "")]

        extract_dependencies_mock.side_effect = side_effect_extract_dependencies
        install_spec_pkg_mock.return_value = ""
        CTAN_mock.return_value = ""

        with self.assertLogs('default', level='WARNING') as cm:
            lpm_inst = lpm()
            lpm_inst.install_pkg("A")
            self.assertEqual(len(cm.output), 1) # Warned once
            print(cm.output[0])
            self.assertGreater(cm.output[0].find("already installed"), 0)
      
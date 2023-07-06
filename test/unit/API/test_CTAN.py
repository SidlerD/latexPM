import unittest

from src.API import CTAN


class Test_CTAN(unittest.TestCase):
    
    def setUp(self) -> None:
        self.pairs = [
            {'name': 'BibTeX Database Generator', 'id': 'bibtex-gen'},
            {'name': '12many', 'id': 'one2many'},
            {'name': 'amsmath', 'id': 'amsmath'},
            {'name': 'acro', 'id': 'acro'}
        ]
    
    def test_get_id_from_name(self):
        for pair in self.pairs:
            self.assertEqual(pair['id'], CTAN.get_id_from_name(pair['name']))
        
        # Test that it raises Exception when called with package that doesn't exist on CTAN
        self.assertRaises(Exception, CTAN.get_id_from_name, args="amsgen")
        self.assertRaises(Exception, CTAN.get_id_from_name, args="not-existing-package")

    def test_get_name_from_id(self):
        for pair in self.pairs:
            self.assertEqual(pair['name'], CTAN.get_name_from_id(pair['id']))
                
        # Test that it raises Exception when called with package that doesn't exist on CTAN
        self.assertRaises(Exception, CTAN.get_name_from_id, args="amsgen")
        self.assertRaises(Exception, CTAN.get_name_from_id, args="not-existing-package")
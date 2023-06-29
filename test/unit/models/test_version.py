import unittest
from src.models.Version import parse_version
from dateutil.parser import parse


class Test_Version(unittest.TestCase):
    
    def test_parse_version_correct_dict1(self):
        i_date, i_number = "", "1.05"
        input = {"number": i_number, "date": i_date}
        date, number = parse_version(input)

        self.assertEqual(i_number, number)
        self.assertFalse(date)  
          
    def test_parse_version_correct_dict2(self):
        i_date, i_number = "1993-08-03", "0.79"
        input = {"number": i_number, "date": i_date}
        date, number = parse_version(input)

        self.assertEqual(i_number, number)
        self.assertEqual(date, parse(i_date))
          
    def test_parse_version_correct_dict3(self):
        i_date, i_number = "", ""
        input = {"number": i_number, "date": i_date}
        date, number = parse_version(input)

        self.assertFalse(number)
        self.assertFalse(date)
        
    def test_parse_version_empty_str(self):
        input = ""
        date, number = parse_version(input)

        self.assertFalse(number)
        self.assertFalse(date)
    
    def test_parse_version_string1(self):
        input = '2005/05/09 v0.3 1, 2, many: numbersets  (ums)'
        date, number = parse_version(input)

        self.assertEqual(date, parse("2005/05/09"))
        self.assertEqual(number, "0.3")
            
    def test_parse_version_string2(self):
        input = '2020/10/05 v2.5k e-TeX tools for LaTeX (JAW)'
        date, number = parse_version(input)

        self.assertEqual(date, parse('2020/10/05'))
        self.assertEqual(number, '2.5k')
    
    # TODO: Add more tests for exctracting Version from str

    # TODO: Add tests for __eq__ 
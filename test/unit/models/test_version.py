import unittest
from src.models.Version import parse_version, Version
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
        self.assertEqual(date, parse(i_date).date())
          
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

        self.assertEqual(date, parse("2005/05/09").date())
        self.assertEqual(number, "0.3")
            
    def test_parse_version_string2(self):
        input = '2020/10/05 v2.5k e-TeX tools for LaTeX (JAW)'
        date, number = parse_version(input)

        self.assertEqual(date, parse('2020/10/05').date())
        self.assertEqual(number, '2.5k')
                
    def test_parse_version_string_number_only(self):
        input = 'v1.2a '
        date, number = parse_version(input)

        self.assertEqual(date, None)
        self.assertEqual(number, '1.2a')

    def test_parse_version_string_single_number(self):
        input = 'sometext pkgA v2 other text'
        date, number = parse_version(input)

        self.assertEqual(date, None)
        self.assertEqual(number, '2')


    # TODO: Add more tests for exctracting Version from str

    # FIXME: How do i test this better?
    def test_Version_equality(self):
        num_11 = num_12 = "2.32a"
        num_2 = "2.3"
        num_n = None
        num_n2 = ""

        date_11 = date_12 = "2012-09-30"
        date_2 = "2013-09-30"
        date_n = None
        date_n2 = ""

        v1_1 = Version(build_dict(date_11, num_11))
        v1_2 = Version(build_dict(date_12, num_12))

        v2 = Version(build_dict(date_2, num_2))
        v2_n = Version(build_dict(date_2, num_n))
        vn_2 = Version(build_dict(date_n, num_2))
        
        vn = Version(build_dict(date_n, num_n))
        vn2 = Version(build_dict(date_n2, num_n2))

        self.assertEqual(v1_1, v1_2)
        self.assertEqual(v1_2, v1_1)
        self.assertEqual(v1_1, v1_1)
        self.assertEqual(v1_2, v1_2)


        # TODO: What about this case: (some_date, None) == (None, some_number)?
        # self.assertEqual(v2_n, vn_2)
        # self.assertEqual(vn_2 ,v2_n)

        # FIXME: What about (somedate, some_number) == (None, None) or (somedate, None) == (None, None)
        # self.assertEqual(v2, v2_n)
        # self.assertEqual(v2_n, v2)
        # self.assertEqual(v2, vn_2)
        # self.assertEqual(vn_2, v2)
        # self.assertNotEqual(v1_1, vn)
        # self.assertNotEqual(v2_n, vn)
        # self.assertNotEqual(vn_2, vn)

        # self.assertEqual(vn, vn2)
        # self.assertEqual(vn2, vn)


def build_dict(date: str, number: str):
    return {'date': date, 'number': number}
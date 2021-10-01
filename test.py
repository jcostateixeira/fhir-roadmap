import unittest
from extract_metadata2 import main
from data_parser import get_data_and_create_node

class TestFunctions(unittest.TestCase):
    ##overal function test, need to check path 
    def test_func_overal(self):
        self.assertEqual(main("test/test1"), "ok", "Function runs ok")

    #def test_sum_tuple(self):
   #     self.assertEqual(sum((1, 2, 2)), 6, "Should be 6")

if __name__ == '__main__':
    unittest.main()
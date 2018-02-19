import unittest
import os
import filecmp


class TestParser(unittest.TestCase):
    def test_demo(self):
        os.system("connectors.py in C:\\test\Abu\input out C:\\test\Abu\output")
        self.assertTrue(filecmp.cmp('C:\\test\Abu\output\Connectors.arxml', 'C:\\test\Abu\Connectors.arxml', shallow=False))


suite = unittest.TestLoader().loadTestsFromTestCase(TestParser)
unittest.TextTestRunner(verbosity=1).run(suite)
import unittest
import os
import filecmp


class TestParser(unittest.TestCase):
    def test_demo(self):
        os.system("connectors.py -in D:\\test\connectors\input -out D:\\test\connectors\output")
        self.assertTrue(filecmp.cmp('D:\\test\connectors\output\Connectors.arxml', 'D:\\test\connectors\Connectors.arxml', shallow=False))


suite = unittest.TestLoader().loadTestsFromTestCase(TestParser)
unittest.TextTestRunner(verbosity=1).run(suite)
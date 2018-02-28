import unittest
import os
import os.path
import filecmp
import re
from xml.dom import minidom
from lxml import etree
from xml.etree import ElementTree as ET

class FileCompare():
    def areSame(first_location, second_location):
        file1 = open(first_location)
        file2 = open(second_location)

        line_file1 = file1.readline()
        line_file2 = file2.readline()

        while line_file1 != "" or line_file2 != "":
            line_file1 = line_file1.rstrip()
            line_file1 = line_file1.lstrip()
            line_file2 = line_file2.rstrip()
            line_file2 = line_file2.lstrip()
            if line_file1 != line_file2:
                return False
            line_file1 = file1.readline()
            line_file2 = file2.readline()

        file1.close()
        file2.close()
        return True


    def matchLine(path, line_number, text):
        """
        path = used for defining the file to be checked
        line_number = used to identify the line that will be checked
        text = string containing the text to match
        """
        datafile = open(path)
        line_file = datafile.readline()
        line_file = line_file.rstrip()
        line_no = 1
        while line_file != "":
            if line_no == line_number:
                if line_file == text:
                    return True
                else:
                    return False
            line_no = line_no+1
            line_file = datafile.readline()
            line_file = line_file.rstrip()







################################################################# TESTE ################################################

    # xmlRegex = '(<?xml version="1.0" encoding="UTF-8"?>)'
    # rg = re.compile(xmlRegex, re.IGNORECASE | re.DOTALL)
    # lineCount = 0
    #     with open("C:\\test\Abu\TRS.ABU.FUNC.001\Connectors.arxml"):
    #         for line in f:
    #             lineCount += 1
    #             match = rg.search(line)
    #
    #             if match:
    #                 self.assertTrue(False, logger.failed("An XML Declaration was detected on line: " + str(lineCount) + ".")
    #                 else:
    #                     pass

# datafile = open("C:\\test\Abu\TRS.ABU.GEN.001\output\Connectors.arxml")
# string = "<?xml version='1.0' encoding='UTF-8'?>"
# string2 = '<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2_STRICT_COMPACT.xsd">'
# for line in datafile:
#     if string in line:
#         print('True')
#     else:
#         print('False')

# tree = ET.parse("C:\\test\Abu\TRS.ABU.GEN.001\Connectors.arxml")
# root = tree.getroot()
# print(root.tag)
# print(root.attrib)


################################################################# TESTE ################################################


class TestParser(unittest.TestCase):
    # def test_TRS_ABU_GEN_0002_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0002_1\input -out C:\\test\Abu\TRS.ABU.FUNC.0002_1\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0002_1\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0002_1\Connectors.arxml'))
    #
    # def test_TRS_ABU_GEN_0002_2(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0002_2\input -out C:\\test\Abu\TRS.ABU.FUNC.0002_2\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0002_2\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0002_2\Connectors.arxml'))
    #
    # def test_TRS_ABU_GEN_0003_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0003_1\input -out C:\\test\Abu\TRS.ABU.FUNC.0003_1\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0003_1\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0003_1\Connectors.arxml'))
    #
    # def test_TRS_ABU_GEN_0003_2(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0003_2\input -out C:\\test\Abu\TRS.ABU.FUNC.0003_2\output")
    #     self.assertFalse(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0003_2\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0003_2\Connectors.arxml'))
    #
    # def test_TRS_ABU_GEN_0004(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0004\input -out C:\\test\Abu\TRS.ABU.FUNC.0004\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0004\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0004\Connectors.arxml'))
    #
    # def test_TRS_ABU_GEN_0005(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0005\input -out C:\\test\Abu\TRS.ABU.FUNC.0005\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0005\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0005\Connectors.arxml'))
    #
    # def test_TRS_ABU_GEN_0006(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0006\input -out C:\\test\Abu\TRS.ABU.FUNC.0006\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0006\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0006\Connectors.arxml'))

    # def test_TRS_ABU_GEN_0007(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0007\input -out C:\\test\Abu\TRS.ABU.FUNC.0007\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0007\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0007\Connectors.arxml'))

    # def test_TRS_ABU_GEN_0008(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0008\input -out C:\\test\Abu\TRS.ABU.FUNC.0008\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0008\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0008\Connectors.arxml'))

    # def test_TRS_ABU_GEN_0009_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0009_1\input -out C:\\test\Abu\TRS.ABU.FUNC.0009_1\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0009_1\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0009_1\Connectors.arxml'))

    # def test_TRS_ABU_GEN_0009_2(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.FUNC.0009_2\input -out C:\\test\Abu\TRS.ABU.FUNC.0009_2\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.FUNC.0009_2\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.FUNC.0009_2\Connectors.arxml'))

    # def test_TRS_ABU_GEN_001(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.001\input -out C:\\test\Abu\TRS.ABU.GEN.001\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.001\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.001\Connectors.arxml'))

    def test_TRS_ABU_GEN_001_1(self):
        os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.001\input -out C:\\test\Abu\TRS.ABU.GEN.001\output")
        self.assertTrue(FileCompare.matchLine('C:\\test\Abu\TRS.ABU.GEN.001\output\Connectors.arxml', 1, "<?xml version='1.0' encoding='UTF-8'?>"))
        self.assertTrue(FileCompare.matchLine('C:\\test\Abu\TRS.ABU.GEN.001\output\Connectors.arxml', 2,
                                              '<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2_STRICT_COMPACT.xsd">'))

    # def test_TRS_ABU_GEN_002(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.002\input -out C:\\test\Abu\TRS.ABU.GEN.002\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.002\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.002\Connectors.arxml'))

    # def test_TRS_ABU_GEN_003_1(self):       #Check that a warning is present - De intrebat Cristi!!!!
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.003_1\input -out C:\\test\Abu\TRS.ABU.GEN.003_1\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.003_1\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.003_1\Connectors.arxml'))

    # def test_TRS_ABU_GEN_003_2(self):       #Check that a warning is present - De intrebat Cristi!!!!
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.003_2\input -out C:\\test\Abu\TRS.ABU.GEN.003_2\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.003_2\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.003_2\Connectors.arxml'))

    # def test_TRS_ABU_GEN_004_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_1\input -out C:\\test\Abu\TRS.ABU.GEN.004_1\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.004_1\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.004_1\Connectors.arxml'))

    # def test_TRS_ABU_GEN_004_2(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_2\input -out C:\\test\Abu\TRS.ABU.GEN.004_2\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.004_2\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.004_2\Connectors.arxml'))

    # def test_TRS_ABU_GEN_004_3(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_3\input -out C:\\test\Abu\TRS.ABU.GEN.004_3\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.004_3\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.004_3\Connectors.arxml'))
    #


suite = unittest.TestLoader().loadTestsFromTestCase(TestParser)
unittest.TextTestRunner(verbosity=2).run(suite)

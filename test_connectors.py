import unittest
import os
import os.path
import filecmp
import re
from xml.dom import minidom
from lxml import etree
import xml.etree.ElementTree as ET

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

    def checkLog(path, level, message):
        """
        path = used for defining the file to be checked
        level = criticity level :INFO, WARNING, ERROR
        message = string to be matched
        help: preia un fisier si verifica daca contine nivelul de criticitate selectat; daca acesta exista, ccmpara
        daca este prezent si restul mesajului pe aceeasi linie si returneaza TRUE; daca parcurge toate liniile si nu
        gaseste mesajul cercetat alaturi de nivelul de criticitate, atunci returneaza FALSE
        exemplu apel: FileCompare.checkLog(<cale_fisier>, "WARNING", "<numele_portului>")
        """
        # datafile = open(path)
        # line_file = datafile.readline()
        # while line_file != "":
        #     if level + " " + message in line_file:
        #         # if message in line_file:
        #         return True
        #     line_file = datafile.readline()
        # return False

        datafile = open(path)
        line_file = datafile.readline()
        while line_file != "":
            for text in message:
                if level + " " + text in line_file:
                    # print(line_file)
                    return True
            line_file = datafile.readline()
        return False


        # with open(path) as datafile:
        #     for line in datafile:
        #         for text in message:
        #             if (level + " " + text) in line:
        #                 return True
        #     return False


    def checkParsing(path1, path2, message):
        """
        path1 = used for taking the .arxml files name
        path2 = used for defining the file to be checked
        message = string to be matched
        """
        list_arxml_file = [f for f in os.listdir(path1) if f.endswith('.arxml')]
        datafile = open(path2)
        line_file = datafile.readline()
        while line_file != "":
            for files in list_arxml_file:
                if files + " " + message in line_file:
                    return True
            line_file = datafile.readline()
        return False

    def checkStructure(path, child, grandchild, connector):
        """
        path = used for defining the file to be checked
        child = Connector child list
        grandchild = Connector grandchild list
        connector = connector tag name
        """
        tree = ET.parse(path)
        root = tree.getroot()
        for element in root.iter(tag = connector):
            for child in element:
                for grandchild in child:
                    if child.tag.split('}', 1)[1] in child:
                        if grandchild.tag.split('}', 1)[1] in grandchild:
                            return True
                        else:
                            return False



################################################################# TESTE ################################################

tree = ET.parse('C:\\test\Abu\TRS.ABU.GEN.002\output\Connectors.arxml')
root = tree.getroot()
ns = '{http://autosar.org/schema/r4.0}'
childList = ["SHORT-NAME", "PROVIDER-IREF", "REQUESTER-IREF"]
grandchildList = []
connectorTag = '{http://autosar.org/schema/r4.0}ASSEMBLY-SW-CONNECTOR'
for element in root.iter(tag = connectorTag):
    for child in element:
        # if child.tag.split('}', 1)[1] == "SHORT-NAAME" or "PROVIDER-IREF" or "REQUESTER-IREF":
        if child.tag.split('}', 1)[1] in childList:
            print("Yes")
        else:
            print('No')
        # print(child.tag.split('}', 1)[1]) #return SHORT-NAME, PROVIDER-IREF, REQUESTER-IREF
        for grandchild in child:
            print(grandchild.tag.split('}', 1)[1])

tree = ET.parse('C:\\test\Abu\TRS.ABU.GEN.002\output\Connectors.arxml')
root = tree.getroot()
child = ["SHORT-NAME", "PROVIDER-IREF", "REQUESTER-IREF"]
grandchild = ["CONTEXT-COMPONENT-REF", "TARGET-P-PORT-REF", "CONTEXT-COMPONENT-REF", "TARGET-R-PORT-REF"]
connector = '{http://autosar.org/schema/r4.0}ASSEMBLY-SW-CONNECTOR'
for element in root.iter(tag = connector):
    for child in element:
        for grandchild in child:
            if child.tag.split('}', 1)[1] in child:
                if grandchild.tag.split('}', 1)[1] in grandchild:
                    print("yes")
                else:
                    print("No")


# ################################################################# TESTE ################################################
tree = ET.parse('C:\\test\Abu\TRS.ABU.GEN.002\output\Connectors.arxml')
root = tree.getroot()
ns = '{http://autosar.org/schema/r4.0}'
for element in root.iter(tag = '{http://autosar.org/schema/r4.0}ASSEMBLY-SW-CONNECTOR'):
    for child in element:
        print(child.tag.split('}', 1)[1]) #return SHORT-NAME, PROVIDER-IREF, REQUESTER-IREF
        for grandchild in child:
            # print(grandchild.tag.split('}', 1)[1])

################################################################# TESTE ################################################



class TestParser(unittest.TestCase):

    # def test_TRS_ABU_INOUT_001(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.INOUT.001\input -out C:\\test\Abu\TRS.ABU.INOUT.001\output")
    #     self.assertTrue(FileCompare.checkParsing('C:\\test\Abu\TRS.ABU.INOUT.001\input', 'C:\\test\Abu\TRS.ABU.INOUT.001\output\\result.log', 'is'))



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

    # def test_TRS_ABU_GEN_001_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.001\input -out C:\\test\Abu\TRS.ABU.GEN.001\output")
    #     self.assertTrue(FileCompare.matchLine('C:\\test\Abu\TRS.ABU.GEN.001\output\Connectors.arxml', 1, "<?xml version='1.0' encoding='UTF-8'?>"))
    #     self.assertTrue(FileCompare.matchLine('C:\\test\Abu\TRS.ABU.GEN.001\output\Connectors.arxml', 2,
    #                                           '<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2_STRICT_COMPACT.xsd">'))





    # def test_TRS_ABU_GEN_002(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.002\input -out C:\\test\Abu\TRS.ABU.GEN.002\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.002\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.002\Connectors.arxml'))

    # def test_TRS_ABU_GEN_002_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.002\input -out C:\\test\Abu\TRS.ABU.GEN.002\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.002\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.002\Connectors.arxml'))
    #




    # def test_TRS_ABU_GEN_003_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.003_1\input -out C:\\test\Abu\TRS.ABU.GEN.003_1\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.003_1\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.003_1\Connectors.arxml'))

    # def test_TRS_ABU_GEN_003_1_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.003_1\input -out C:\\test\Abu\TRS.ABU.GEN.003_1\output")
    #     self.assertTrue(FileCompare.checkLog("C:\\test\Abu\TRS.ABU.GEN.003_1\output\\result.log", "WARNING", ["PRP_CS_VehicleSPeed", "ASWC_M740_MSI"]))


    # def test_TRS_ABU_GEN_003_2(self):       #Check that a warning is present - De intrebat Cristi!!!!
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.003_2\input -out C:\\test\Abu\TRS.ABU.GEN.003_2\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.003_2\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.003_2\Connectors.arxml'))

    # def test_TRS_ABU_GEN_003_2_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.003_2\input -out C:\\test\Abu\TRS.ABU.GEN.003_2\output")
    #     self.assertTrue(FileCompare.checkLog("C:\\test\Abu\TRS.ABU.GEN.003_2\output\\result.log", "WARNING", ["PRP_CS_VehicleSPeed"]))




    # def test_TRS_ABU_GEN_004_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_1\input -out C:\\test\Abu\TRS.ABU.GEN.004_1\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.004_1\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.004_1\Connectors.arxml'))

    # def test_TRS_ABU_GEN_004_1_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_1\input -out C:\\test\Abu\TRS.ABU.GEN.004_1\output")
    #     self.assertTrue(FileCompare.checkLog("C:\\test\Abu\TRS.ABU.GEN.004_1\output\\result.log", "ERROR", [""]))


    # def test_TRS_ABU_GEN_004_2(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_2\input -out C:\\test\Abu\TRS.ABU.GEN.004_2\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.004_2\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.004_2\Connectors.arxml'))

    # def test_TRS_ABU_GEN_004_2_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_2\input -out C:\\test\Abu\TRS.ABU.GEN.004_2\output")
    #     self.assertTrue(FileCompare.checkLog("C:\\test\Abu\TRS.ABU.GEN.004_2\output\\result.log", "ERROR", [""]))

    # def test_TRS_ABU_GEN_004_3(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_3\input -out C:\\test\Abu\TRS.ABU.GEN.004_3\output")
    #     self.assertTrue(FileCompare.areSame('C:\\test\Abu\TRS.ABU.GEN.004_3\output\Connectors.arxml', 'C:\\test\Abu\TRS.ABU.GEN.004_3\Connectors.arxml'))

    # def test_TRS_ABU_GEN_004_3_1(self):
    #     os.system("connectors.py -in C:\\test\Abu\TRS.ABU.GEN.004_3\input -out C:\\test\Abu\TRS.ABU.GEN.004_3\output")
    #     self.assertTrue(FileCompare.checkLog("C:\\test\Abu\TRS.ABU.GEN.004_3\output\\result.log", "ERROR", [""]))



suite = unittest.TestLoader().loadTestsFromTestCase(TestParser)
unittest.TextTestRunner(verbosity=2).run(suite)

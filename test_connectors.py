import unittest
import os
import os.path
import ntpath
import coverage
import HtmlTestRunner
from lxml import etree


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
            if line_file1.startswith("<SHORT-NAME>ASSEMBLY_CONNECTOR"):
                line_file1 = file1.readline()
                line_file2 = file2.readline()
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
        """
        datafile = open(path)
        line_file = datafile.readline()
        bool_message = []
        for elem in message:
            bool_message.append(False)
        i = 0
        while line_file != "":
            for text in message:
                if level in line_file:
                    if text in line_file:
                        # print(line_file)
                        bool_message[i] = True
                        i = i + 1
            line_file = datafile.readline()
        for elem in bool_message:
            if elem == False:
                return False
        return True

    def checkError(path, level, message):
        """
        path = used for defining the file to be checked
        level = criticity level :INFO, WARNING, ERROR
        message = string to be matched
        """
        datafile = open(path)
        line_file = datafile.readline()
        while line_file != "":
            for text in message:
                if level in line_file:
                    if text in line_file:
                        # print(line_file)
                        return True
            line_file = datafile.readline()
        return False

    def checkParsing(path1, path2, message):
        """
        path1 = used for taking the .arxml files name
        path2 = used for defining the file to be checked
        message = string to be matched
        """
        all_files = []
        found_files = []
        for file in os.listdir(path1):
            if file.endswith('.arxml'):
                all_files.append(file)
        for file in all_files:
            found_files.append(False)
        datafile = open(path2)
        line_file = datafile.readline()
        i = 0
        while line_file != "":
            for files in all_files:
                if files + " " + message in line_file:
                    found_files[i] = True
                    i =i + 1
            line_file = datafile.readline()
        for item in found_files:
            if item == False:
                return False
        return True

    def isConnector(path):
        """
        path = used for defining the file to be checked
        """
        tree = etree.parse(path)
        root = tree.getroot()
        found_name = found_provider = found_requester = found_contextP = found_targetP = found_contextR =found_targetR = False
        connectors = root.findall(".//{http://autosar.org/schema/r4.0}ASSEMBLY-SW-CONNECTOR")
        for elem in connectors:
            for c in elem:
                if c.tag == "{http://autosar.org/schema/r4.0}SHORT-NAME":
                    found_name = True
                if c.tag == "{http://autosar.org/schema/r4.0}PROVIDER-IREF":
                    found_provider = True
                    provider = elem.find(".//{http://autosar.org/schema/r4.0}PROVIDER-IREF")
                    for child in provider:
                        if child.tag == "{http://autosar.org/schema/r4.0}CONTEXT-COMPONENT-REF":
                            found_contextP = True
                        if child.tag == "{http://autosar.org/schema/r4.0}TARGET-P-PORT-REF":
                            found_targetP = True
                if c.tag == "{http://autosar.org/schema/r4.0}REQUESTER-IREF":
                    found_requester = True
                    requester = elem.find(".//{http://autosar.org/schema/r4.0}REQUESTER-IREF")
                    for child in requester:
                        if child.tag == "{http://autosar.org/schema/r4.0}CONTEXT-COMPONENT-REF":
                            found_contextR = True
                        if child.tag == "{http://autosar.org/schema/r4.0}TARGET-R-PORT-REF":
                            found_targetR = True

        if found_name and found_provider and found_requester and found_contextP and found_targetP and found_contextR and found_targetR:
            return True
        else:
            return False

    def isOutput(path):
        """
        path = used for defining the folder to be checked
        """
        if os.path.isfile(path):
            return True
        else:
            return False


class ConnectorDescriptor(unittest.TestCase):

    def test_TRS_CONNECTOR_INOUT_001(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\\TRS.CONNECTOR.INOUT.001\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.checkParsing(head + '\\tests\\TRS.CONNECTOR.INOUT.001\\input', head + '\\tests\\TRS.CONNECTOR.INOUT.001\\output\\result.log', 'is well-formed'))

    def test_TRS_CONNECTOR_FUNC_0002_1(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0002_1\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0002_1\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0002_1\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_0002_2(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0002_2\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0002_2\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0002_2\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_0003_1(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0003_1\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0003_1\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0003_1\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_0003_2(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0003_2\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0003_2\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0003_2\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_0004(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0004\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0004\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0004\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_0005(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0005\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0005\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0005\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_0006(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0006\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0006\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0006\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_0009_1(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0009_1\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0009_1\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0009_1\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_0009_2(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.0009_2\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.0009_2\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.0009_2\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_010_1(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.010_1\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.010_1\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.010_1\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_010_2(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.010_2\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.010_2\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.010_2\Connectors.arxml'))

    def test_TRS_CONNECTOR_FUNC_011(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.FUNC.011\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.FUNC.011\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.FUNC.011\Connectors.arxml'))

    def test_TRS_CONNECTOR_GEN_001(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.GEN.001\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.matchLine(head + '\\tests\TRS.CONNECTOR.GEN.001\output\Connectors.arxml', 1, "<?xml version='1.0' encoding='UTF-8'?>"))
        self.assertTrue(FileCompare.matchLine(head + '\\tests\TRS.CONNECTOR.GEN.001\output\Connectors.arxml', 2, '<AUTOSAR xmlns="http://autosar.org/schema/r4.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://autosar.org/schema/r4.0 AUTOSAR_4-2-2_STRICT_COMPACT.xsd">'))

    def test_TRS_CONNECTOR_GEN_002(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.GEN.002\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.isConnector(head + '\\tests\TRS.CONNECTOR.GEN.002\output\Connectors.arxml'))

    def test_TRS_CONNECTOR_CHECK_003_1(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.CHECK.003_1\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.CHECK.003_1\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.CHECK.003_1\Connectors.arxml'))
        self.assertTrue(FileCompare.checkLog(head + '\\tests\TRS.CONNECTOR.CHECK.003_1\output\\result.log', "WARNING", ["PRP_NV_VehicleData", "PP_SR_VehicleSPeed", "RP_CS_VehicleMovement"]))

    def test_TRS_CONNECTOR_CHECK_003_2(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.CHECK.003_2\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.CHECK.003_2\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.CHECK.003_2\Connectors.arxml'))
        self.assertTrue(FileCompare.checkLog(head + '\\tests\TRS.CONNECTOR.CHECK.003_2\output\\result.log', "WARNING", ["PRP_CS_VehicleSPeed"]))

    def test_TRS_CONNECTOR_CHECK_004_1(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.CHECK.004_1\ConfigConnectorDescriptor.xml')
        self.assertFalse(FileCompare.isOutput(head + '\\tests\TRS.CONNECTOR.CHECK.004_1\output\Connectors.arxml'))
        self.assertTrue(FileCompare.checkError(head + '\\tests\TRS.CONNECTOR.CHECK.004_1\output\\result.log', "ERROR", ["multiple PPorts"]))

    def test_TRS_CONNECTOR_CHECK_004_2(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.CHECK.004_2\ConfigConnectorDescriptor.xml')
        self.assertFalse(FileCompare.isOutput('' + head + '\\tests\TRS.CONNECTOR.CHECK.004_2\output\Connectors.arxml'))
        self.assertTrue(FileCompare.checkError(head + '\\tests\TRS.CONNECTOR.CHECK.004_2\output\\result.log', "ERROR", ["multiple PPorts"]))

    def test_TRS_CONNECTOR_CHECK_004_3(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.CHECK.004_3\ConfigConnectorDescriptor.xml')
        self.assertFalse(FileCompare.isOutput(head + '\\tests\TRS.CONNECTOR.CHECK.004_3\output\Connectors.arxml'))
        self.assertTrue(FileCompare.checkError(head + '\\tests\TRS.CONNECTOR.CHECK.004_3\output\\result.log', "ERROR", ["multiple PPorts"]))

    def test_CHECK_ARXML(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\CHECK.ARXML\ConfigConnectorDescriptor.xml')
        self.assertFalse(FileCompare.isOutput(head + '\\tests\CHECK.ARXML\output\Connectors.arxml'))
        self.assertTrue(FileCompare.checkError(head + '\\tests\CHECK.ARXML\output\\result.log', "ERROR", ["mismatched tag"]))

    def test_TRS_CONNECTOR_CHECK_003_3(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.CHECK.003_3\\ConfigConnectorDescriptor.xml')
        self.assertTrue(FileCompare.areSame(head + '\\tests\TRS.CONNECTOR.CHECK.003_3\output\Connectors.arxml', head + '\\tests\TRS.CONNECTOR.CHECK.003_3\Connectors.arxml'))

    def test_TRS_CONNECTOR_CHECK_004_4(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.CHECK.004_4\ConfigConnectorDescriptor.xml')
        self.assertFalse(FileCompare.isOutput(head + '\\tests\TRS.CONNECTOR.CHECK.004_4\output\Connectors.arxml'))
        self.assertTrue(FileCompare.checkError(head + '\\tests\TRS.CONNECTOR.CHECK.004_4\output\\result.log', "ERROR", [" "]))

    def test_TRS_CONNECTOR_CHECK_004_5(self):
        current_path = os.path.realpath(__file__)
        head, tail = ntpath.split(current_path)
        os.system('coverage run ConnectorDescriptor.py -config ' + head + '\\tests\TRS.CONNECTOR.CHECK.004_5\ConfigConnectorDescriptor.xml')
        self.assertFalse(FileCompare.checkError(head + '\\tests\TRS.CONNECTOR.CHECK.004_5\output\\result.log', "ERROR", [" "]))



suite = unittest.TestLoader().loadTestsFromTestCase(ConnectorDescriptor)
unittest.TextTestRunner(verbosity=2).run(suite)
#
# current_path = os.path.realpath(__file__)
# head, tail = ntpath.split(current_path)
# if __name__ == "__main__":
#     unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output=head + "\\tests"))

import argparse, os, logging, ntpath
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from xml.dom import minidom
from lxml import etree
import xml.etree.ElementTree as ET


def main():
    # parsing the command line arguments
    parser = argparse.ArgumentParser()
    arg_parse(parser)
    args = parser.parse_args()
    input_directory = args.input_directory
    output_directory = args.output_path
    # setting input and output paths
    input_path = input_directory.replace("\\", "/")
    output_path = output_directory.replace("\\", "/")
    # logger creation and setting
    logger = logging.getLogger('result')
    hdlr = logging.FileHandler(output_path + '/result.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    open(output_path + '/result.log', 'w').close()

    create_connectors(input_path, output_path, logger)


def create_connectors(input_path, output_path, logger):
    current_path = os.path.realpath(__file__)
    head, tail = ntpath.split(current_path)
    xsd_path = head + '/AUTOSAR_4-2-2_STRICT.xsd'
    path = xsd_path.replace("\\", "/")
    connectors = []
    PPorts = []
    RPorts = []
    for directory, directories, files in os.walk(input_path):
        for file in files:
            if file.endswith('.arxml'):
                fullname = os.path.join(directory, file)
                try:
                    check_if_xml_is_wellformed(fullname)
                    logger.info('The file: ' + fullname + ' is well-formed')
                except Exception as e:
                    logger.error('The file: ' + fullname + ' is not well-formed: ' + str(e))
                    return
                validate_xml_with_xsd(path, fullname, logger)
                tree = etree.parse(fullname)
                root = tree.getroot()
                PPort = root.findall(".//{http://autosar.org/schema/r4.0}P-PORT-PROTOTYPE")
                RPort = root.findall(".//{http://autosar.org/schema/r4.0}R-PORT-PROTOTYPE")
                # build list of PPorts
                for elemPP in PPort:
                    aswc = elemPP.getparent().getprevious().text
                    if aswc != "AswcDiagForDcm":
                        objPPort = {}
                        objPPort['SHORT-NAME'] = elemPP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        objPPort['PROVIDED-INTERFACE-TREF'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").text
                        objPPort['ASWC'] = aswc
                        PPorts.append(objPPort)
                # build list of RPorts
                for elemRP in RPort:
                    aswc = elemRP.getparent().getprevious().text
                    objRPort = {}
                    objRPort['SHORT-NAME'] = elemRP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                    objRPort['REQUIRED-INTERFACE-TREF'] = elemRP.find("{http://autosar.org/schema/r4.0}REQUIRED-INTERFACE-TREF").text
                    objRPort['ASWC'] = aswc
                    RPorts.append(objRPort)
    # build list of connectors
    lengthR = len(RPorts)
    lengthP = len(PPorts)
    for indexR in range(lengthR):
        for indexP in range(lengthP):
            if RPorts[indexR]['REQUIRED-INTERFACE-TREF'] == PPorts[indexP]['PROVIDED-INTERFACE-TREF']:
                if (RPorts[indexR]['SHORT-NAME'][:2] == 'RP') and (PPorts[indexP]['SHORT-NAME'][:2] == 'PP'):
                    if RPorts[indexR]['SHORT-NAME'][3:] == PPorts[indexP]['SHORT-NAME'][3:]:
                        objConnector = {}
                        objConnector['NAME'] = RPorts[indexR]['SHORT-NAME'][3:]
                        objConnector['INTERFACE'] = RPorts[indexR]['REQUIRED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-PP'] = PPorts[indexP]['SHORT-NAME']
                        objConnector['PROVIDED-INTERFACE-TREF'] = PPorts[indexP]['PROVIDED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-RP'] = RPorts[indexR]['SHORT-NAME']
                        objConnector['REQUIRED-INTERFACE-TREF'] = RPorts[indexR]['REQUIRED-INTERFACE-TREF']
                        objConnector['ASWC-PPORT'] = PPorts[indexP]['ASWC']
                        objConnector['ASWC-RPORT'] = RPorts[indexR]['ASWC']
                        connectors.append(objConnector)

    # check if there are multiple RP and PP for the same interface
    lengthC = len(connectors)
    for indexC1 in range(lengthC):
        for indexC2 in range(lengthC):
            if indexC1 != indexC2:
                if (connectors[indexC1]['NAME'] == connectors[indexC2]['NAME']) and (
                        connectors[indexC1]['INTERFACE'] == connectors[indexC2]['INTERFACE']):
                    logger.error('multiple RP and PP for ' + connectors[indexC1]['NAME'] + ' for interface ' +
                                 connectors[indexC1]['INTERFACE'])
                    logger.error('Connectors file not generated!')
                    try:
                        os.remove(output_path + '/Connectors.arxml')
                    except OSError:
                        pass
                    return

    # create Connectors.arxml
    rootConnectors = ET.Element('AUTOSAR')
    rootConnectors.set('xmlns', "http://autosar.org/schema/r4.0")
    rootConnectors.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    rootConnectors.set('xsi:schemaLocation', "http://autosar.org/schema/r4.0 AUTOSAR_4-2-2_STRICT_COMPACT.xsd")
    packages = ET.SubElement(rootConnectors, 'AR-PACKAGES', xmlns="")
    package = ET.SubElement(packages, 'AR-PACKAGE')
    short_name = ET.SubElement(package, 'SHORT-NAME').text = 'RootCompo'
    compo = ET.SubElement(package, 'COMPOSITION-SW-COMPONENT-TYPE')
    short_name = ET.SubElement(compo, 'SHORT-NAME').text = 'CompoVSM'
    connector = ET.SubElement(compo, 'CONNECTORS')
    for indexC1 in range(lengthC):
        assembly = ET.SubElement(connector, 'ASSEMBLY-SW-CONNECTOR')
        ET.SubElement(assembly, 'SHORT-NAME').text = connectors[indexC1]['SHORT-NAME-PP'][3:] + "_" + connectors[indexC1]['ASWC-PPORT'] + "_to_" + connectors[indexC1]['ASWC-RPORT']
        ET.SubElement(assembly, 'PROVIDER-IREF').text = connectors[indexC1]['SHORT-NAME-PP']
        ET.SubElement(assembly, 'REQUESTER-IREF').text = connectors[indexC1]['SHORT-NAME-RP']
    pretty_xml = prettify_xml(rootConnectors)
    tree = ET.ElementTree(ET.fromstring(pretty_xml))
    tree.write(output_path + '/Connectors.arxml', encoding="UTF-8", xml_declaration=True, method="xml")
    validate_xml_with_xsd(path, output_path + '/Connectors.arxml', logger)
    #remove ns0 namespace from all file
    ET.register_namespace("", "http://autosar.org/schema/r4.0")
    tree = ET.parse(output_path + '/Connectors.arxml')
    root = tree.getroot()
    output = ET.ElementTree(root)
    output.write(output_path + '/Connectors.arxml', encoding="UTF-8", xml_declaration=True, method="xml")


def arg_parse(parser):
    # adding command line options
    parser.add_argument("input", help="specify the input parameters")
    parser.add_argument("input_directory", help="location of input files")
    parser.add_argument("output", help="specify the output parameters")
    parser.add_argument("output_path", help="folder which will contain the output files")


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


def validate_xml_with_xsd(path_xsd, path_xml, logger):
    # load xsd file
    xmlschema_xsd = etree.parse(path_xsd)
    xmlschema = etree.XMLSchema(xmlschema_xsd)
    # validate xml file
    xmldoc = etree.parse(path_xml)
    if xmlschema.validate(xmldoc) is not True:
        logger.warning('The file: ' + path_xml + ' is not valid with the AUTOSAR4.2.2-STRICT  schema')
    else:
        logger.info('The file: ' + path_xml + ' is valid with the AUTOSAR4.2.2-STRICT schema')


def check_if_xml_is_wellformed(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)


if __name__ == "__main__":
        main()
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
    input_path = input_path.split(';')
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
    for each_path in input_path:
        for directory, directories, files in os.walk(each_path):
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
                    PRPort = root.findall(".//{http://autosar.org/schema/r4.0}PR-PORT-PROTOTYPE")
                    RPort = root.findall(".//{http://autosar.org/schema/r4.0}R-PORT-PROTOTYPE")
                    # build list of PPorts
                    for elemPP in PPort:
                        swc = root.find(".//{http://autosar.org/schema/r4.0}SW-COMPONENT-PROTOTYPE").getchildren()[0].text
                        aswc = elemPP.getparent().getprevious().text
                        root_p = elemPP.getparent().getparent().getparent().getprevious().text
                        objPPort = {}
                        objPPort['SHORT-NAME'] = elemPP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        objPPort['PROVIDED-INTERFACE-TREF'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").text
                        objPPort['ASWC'] = aswc
                        objPPort['ROOT'] = root_p
                        objPPort['SWC'] = swc
                        objPPort['SINGLE'] = True
                        PPorts.append(objPPort)
                    for elemPRP in PRPort:
                        swc = root.find(".//{http://autosar.org/schema/r4.0}SW-COMPONENT-PROTOTYPE").getchildren()[0].text
                        aswc = elemPRP.getparent().getprevious().text
                        root_p = elemPRP.getparent().getparent().getparent().getprevious().text
                        objPRPort = {}
                        objPRPort['SHORT-NAME'] = elemPRP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        objPRPort['PROVIDED-INTERFACE-TREF'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").text
                        objPRPort['ASWC'] = aswc
                        objPRPort['ROOT'] = root_p
                        objPRPort['SWC'] = swc
                        objPRPort['SINGLE'] = True
                        PPorts.append(objPRPort)
                    # build list of RPorts
                    for elemRP in RPort:
                        swc = root.find(".//{http://autosar.org/schema/r4.0}SW-COMPONENT-PROTOTYPE").getchildren()[0].text
                        aswc = elemRP.getparent().getprevious().text
                        root_p = elemRP.getparent().getparent().getparent().getprevious().text
                        objRPort = {}
                        objRPort['SHORT-NAME'] = elemRP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        objRPort['REQUIRED-INTERFACE-TREF'] = elemRP.find("{http://autosar.org/schema/r4.0}REQUIRED-INTERFACE-TREF").text
                        objRPort['ASWC'] = aswc
                        objRPort['ROOT'] = root_p
                        objRPort['SWC'] = swc
                        objRPort['SINGLE'] = True
                        RPorts.append(objRPort)
    # build list of connectors
    for indexR in range(len(RPorts)):
        for indexP in range(len(PPorts)):
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
                        objConnector['ROOT-PPORT'] = PPorts[indexP]['ROOT']
                        objConnector['ROOT-RPORT'] = RPorts[indexR]['ROOT']
                        objConnector['SWC-PPORT'] = PPorts[indexP]['SWC']
                        objConnector['SWC-RPORT'] = RPorts[indexR]['SWC']
                        connectors.append(objConnector)
                        RPorts[indexR]['SINGLE'] = False
                        PPorts[indexP]['SINGLE'] = False
                else:
                    if RPorts[indexR]['SHORT-NAME'][3:] == PPorts[indexP]['SHORT-NAME'][4:]:
                        objConnector = {}
                        objConnector['NAME'] = RPorts[indexR]['SHORT-NAME'][3:]
                        objConnector['INTERFACE'] = RPorts[indexR]['REQUIRED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-PP'] = PPorts[indexP]['SHORT-NAME']
                        objConnector['PROVIDED-INTERFACE-TREF'] = PPorts[indexP]['PROVIDED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-RP'] = RPorts[indexR]['SHORT-NAME']
                        objConnector['REQUIRED-INTERFACE-TREF'] = RPorts[indexR]['REQUIRED-INTERFACE-TREF']
                        objConnector['ASWC-PPORT'] = PPorts[indexP]['ASWC']
                        objConnector['ASWC-RPORT'] = RPorts[indexR]['ASWC']
                        objConnector['ROOT-PPORT'] = PPorts[indexP]['ROOT']
                        objConnector['ROOT-RPORT'] = RPorts[indexR]['ROOT']
                        connectors.append(objConnector)
                        RPorts[indexR]['SINGLE'] = False
                        PPorts[indexP]['SINGLE'] = False
    for indexR in range(len(RPorts)):
        if RPorts[indexR]['SINGLE']:
            logger.warning(RPorts[indexR]['SHORT-NAME'] + ' is without connector')
    for indexP in range(len(PPorts)):
        if PPorts[indexP]['SINGLE']:
            logger.warning(PPorts[indexP]['SHORT-NAME'] + ' is without connector')

    # check if there are multiple RP and PP for the same interface
    # also, if there are several PPorts or PRPorts, and one of them is from <DiagForDcm>, ignore it
    for indexC1 in range(len(connectors)):
        for indexC2 in range(len(connectors)):
            if indexC1 != indexC2:
                if connectors[indexC1]['NAME'] == connectors[indexC2]['NAME']:
                    if connectors[indexC2]['ASWC-PPORT'] == "AswcDiagForDcm":
                        connectors.remove(connectors[indexC2])
                    elif connectors[indexC1]['INTERFACE'] == connectors[indexC2]['INTERFACE']:
                        logger.error('multiple RP and PP for ' + connectors[indexC1]['NAME'] + ' for interface ' + connectors[indexC1]['INTERFACE'])
                        # logger.error('Connectors file not generated!')
                        # try:
                        #     os.remove(output_path + '/Connectors.arxml')
                        # except OSError:
                        #     pass
                        # return

    # create Connectors.arxml
    rootConnectors = ET.Element('AUTOSAR')
    rootConnectors.set('xmlns', "http://autosar.org/schema/r4.0")
    rootConnectors.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    rootConnectors.set('xsi:schemaLocation', "http://autosar.org/schema/r4.0 AUTOSAR_4-2-2_STRICT_COMPACT.xsd")
    packages = ET.SubElement(rootConnectors, 'AR-PACKAGES', xmlns="")
    package = ET.SubElement(packages, 'AR-PACKAGE')
    short_name = ET.SubElement(package, 'SHORT-NAME').text = 'RootP_Composition'
    compo = ET.SubElement(package, 'COMPOSITION-SW-COMPONENT-TYPE')
    short_name = ET.SubElement(compo, 'SHORT-NAME').text = 'Compo_VSM'
    connector = ET.SubElement(compo, 'CONNECTORS')
    for indexC1 in range(len(connectors)):
        assembly = ET.SubElement(connector, 'ASSEMBLY-SW-CONNECTOR')
        ET.SubElement(assembly, 'SHORT-NAME').text = connectors[indexC1]['SHORT-NAME-PP'] + "_" + connectors[indexC1]['ASWC-PPORT'] + "_to_" + connectors[indexC1]['ASWC-RPORT']
        provider = ET.SubElement(assembly, 'PROVIDER-IREF')
        context_provider = ET.SubElement(provider, 'CONTEXT-COMPONENT-REF')
        context_provider.set('DEST', "SW-COMPONENT-PROTOTYPE")
        context_provider.text = '/RootP_Composition/Compo_VSM/' + connectors[indexC1]['SWC-PPORT']
        if connectors[indexC1]['SHORT-NAME-PP'][:3] == "PP_":
            target_provided = ET.SubElement(provider, 'TARGET-P-PORT-REF')
            target_provided.set('DEST', "P-PORT-PROTOTYOPE")
            target_provided.text = '/' + connectors[indexC1]['ROOT-PPORT'] + '/' + connectors[indexC1]['ASWC-PPORT'] + '/' + connectors[indexC1]['SHORT-NAME-PP']
        else:
            target_provided = ET.SubElement(provider, 'TARGET-PR-PORT-REF')
            target_provided.set('DEST', "PR-PORT-PROTOTYOPE")
            target_provided.text = '/'+connectors[indexC1]['ROOT-PPORT']+'/'+connectors[indexC1]['ASWC-PPORT']+'/'+connectors[indexC1]['SHORT-NAME-PP']
        requester = ET.SubElement(assembly, 'REQUESTER-IREF')
        context_requester = ET.SubElement(requester, 'CONTEXT-COMPONENT-REF')
        context_requester.set('DEST', "SW-COMPONENT-PROTOTYPE")
        context_requester.text = '/RootP_Composition/Compo_VSM/'+connectors[indexC1]['SWC-RPORT']
        target_requested = ET.SubElement(requester, 'TARGET-R-PORT-REF')
        target_requested.set('DEST', "R-PORT-PROTOTYOPE")
        target_requested.text = '/'+connectors[indexC1]['ROOT-RPORT']+'/'+connectors[indexC1]['ASWC-RPORT']+'/'+connectors[indexC1]['SHORT-NAME-RP']
    pretty_xml = prettify_xml(rootConnectors)
    tree = ET.ElementTree(ET.fromstring(pretty_xml))
    tree.write(output_path + '/Connectors.arxml', encoding="UTF-8", xml_declaration=True, method="xml")
    validate_xml_with_xsd(path, output_path + '/Connectors.arxml', logger)
    # remove ns0 namespace from all file
    ET.register_namespace("", "http://autosar.org/schema/r4.0")
    tree = ET.parse(output_path + '/Connectors.arxml')
    root = tree.getroot()
    output = ET.ElementTree(root)
    output.write(output_path + '/Connectors.arxml', encoding="UTF-8", xml_declaration=True, method="xml")


def arg_parse(parser):
    # adding command line options
    parser.add_argument("-in", action="store_const", const='-in')
    parser.add_argument("input_directory", help="location(s) of input files")
    parser.add_argument("-out", action="store_const", const='-out')
    parser.add_argument("output_path", help="folder which will contain the produced files")


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

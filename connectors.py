import argparse, os, logging                # pragma: no cover
from xml.sax.handler import ContentHandler  # pragma: no cover
from xml.sax import make_parser             # pragma: no cover
from xml.dom import minidom                 # pragma: no cover
from lxml import etree                      # pragma: no cover
from coverage import Coverage               # pragma: no cover
import xml.etree.ElementTree as ET          # pragma: no cover


def main():
    # parsing the command line arguments
    parser = argparse.ArgumentParser()
    arg_parse(parser)
    args = parser.parse_args()
    config_file = args.input_configuration_file
    config_file = config_file.replace("\\", "/")
    # get all configuration parameters
    recursive_path_arxml = []
    simple_path_arxml = []
    recursive_path_swc = []
    simple_path_swc = []
    tree = etree.parse(config_file)
    root = tree.getroot()
    directories = root.findall(".//DIR")
    output_path = ""
    report_path = ""
    for element in directories:
        if element.getparent().tag == "ARXML":
            if element.getparent().getparent().tag == "INPUTS":
                if element.attrib['RECURSIVE'] == "true":
                    recursive_path_arxml.append(element.text)
                else:
                    simple_path_arxml.append(element.text)
            else:
                output_path = element.text
        elif element.getparent().tag == "REPORT":
            report_path = element.text
        elif element.getparent().tag == "SWC_ALLOCATION":
            if element.attrib['RECURSIVE'] == "true":
                recursive_path_swc.append(element.text)
            else:
                simple_path_swc.append(element.text)
    xsd_path = root.find(".//FILE_PATH").text
    # logger creation and setting
    logger = logging.getLogger('result')
    hdlr = logging.FileHandler(report_path + '/result.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    open(report_path + '/result.log', 'w').close()
    create_connectors(recursive_path_arxml, simple_path_arxml, recursive_path_swc, simple_path_swc, xsd_path, output_path, logger)


def create_connectors(recursive_arxml, simple_arxml, recursive_swc, simple_swc, xsd_path, output_path, logger):
    connectors = []
    PPorts = []
    RPorts = []
    input_connectors = []
    software_allocs = []
    compos = []
    for each_path in recursive_arxml:
        for directory, directories, files in os.walk(each_path):
            for file in files:
                if file.endswith('.arxml'):
                    fullname = os.path.join(directory, file)
                    try:
                        check_if_xml_is_wellformed(fullname)
                        logger.info('The file: ' + fullname + ' is well-formed')
                    except Exception as e:
                        logger.error('The file: ' + fullname + ' is not well-formed: ' + str(e))
                        try:
                            os.remove(output_path + '/Connectors.arxml')
                        except OSError:
                            pass
                        return
                    validate_xml_with_xsd(xsd_path, fullname, logger)
                    tree = etree.parse(fullname)
                    root = tree.getroot()
                    PPort = root.findall(".//{http://autosar.org/schema/r4.0}P-PORT-PROTOTYPE")
                    PRPort = root.findall(".//{http://autosar.org/schema/r4.0}PR-PORT-PROTOTYPE")
                    RPort = root.findall(".//{http://autosar.org/schema/r4.0}R-PORT-PROTOTYPE")
                    input_connector = root.findall(".//{http://autosar.org/schema/r4.0}ASSEMBLY-SW-CONNECTOR")
                    sw_compos = root.findall(".//{http://autosar.org/schema/r4.0}SW-COMPONENT-PROTOTYPE")
                    # build list of PPorts
                    for elemPP in PPort:
                        objPPort = {}
                        root_p = elemPP.getparent().getparent().getparent().getparent().getchildren()[0].text
                        aswc = elemPP.getparent().getparent().getchildren()[0].text
                        objPPort['TYPE'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").attrib['DEST']
                        objPPort['FULL-NAME'] = elemPP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        objPPort['SHORT-NAME'] = objPPort['FULL-NAME'][3:]
                        objPPort['INTERFACE-TYPE'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").attrib['DEST']
                        objPPort['PROVIDED-INTERFACE-TREF'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").text
                        objPPort['ASWC'] = aswc
                        objPPort['ROOT'] = root_p
                        objPPort['CORE'] = ""
                        objPPort['PARTITION'] = ""
                        objPPort['SWC'] = ""
                        objPPort['SINGLE'] = True
                        objPPort['CROSSED'] = False
                        if elemPP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].tag == '{http://autosar.org/schema/r4.0}SHORT-NAME':
                            root_s = elemPP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].text
                            objPPort['ROOT'] = root_s + '/' + root_p
                        PPorts.append(objPPort)
                    for elemPRP in PRPort:
                        aswc = elemPRP.getparent().getparent().getchildren()[0].text
                        root_p = elemPRP.getparent().getparent().getparent().getparent().getchildren()[0].text
                        objPRPort = {}
                        objPRPort['FULL-NAME'] = elemPRP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        objPRPort['SHORT-NAME'] = objPRPort['FULL-NAME'][4:]
                        objPRPort['INTERFACE-TYPE'] = \
                        elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").attrib['DEST']
                        objPRPort['PROVIDED-INTERFACE-TREF'] = elemPRP.find(
                            "{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").text
                        objPRPort['TYPE'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").attrib['DEST']
                        objPRPort['ASWC'] = aswc
                        objPRPort['ROOT'] = root_p
                        objPRPort['CORE'] = ""
                        objPRPort['PARTITION'] = ""
                        objPRPort['SWC'] = ""
                        objPRPort['SINGLE'] = True
                        objPRPort['CROSSED'] = False
                        if elemPRP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].tag == '{http://autosar.org/schema/r4.0}SHORT-NAME':
                            root_s = elemPRP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].text
                            objPRPort['ROOT'] = root_s + '/' + root_p
                        PPorts.append(objPRPort)
                    # build list of RPorts
                    for elemRP in RPort:
                        aswc = elemRP.getparent().getparent().getchildren()[0].text
                        root_p = elemRP.getparent().getparent().getparent().getparent().getchildren()[0].text
                        objRPort = {}
                        objRPort['FULL-NAME'] = elemRP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        objRPort['SHORT-NAME'] = objRPort['FULL-NAME'][3:]
                        objRPort['INTERFACE-TYPE'] = elemRP.find("{http://autosar.org/schema/r4.0}REQUIRED-INTERFACE-TREF").attrib['DEST']
                        objRPort['REQUIRED-INTERFACE-TREF'] = elemRP.find("{http://autosar.org/schema/r4.0}REQUIRED-INTERFACE-TREF").text
                        objRPort['TYPE'] = elemRP.find("{http://autosar.org/schema/r4.0}REQUIRED-INTERFACE-TREF").attrib['DEST']
                        objRPort['ASWC'] = aswc
                        objRPort['ROOT'] = root_p
                        objRPort['CORE'] = ""
                        objRPort['PARTITION'] = ""
                        objRPort['SWC'] = ""
                        objRPort['SINGLE'] = True
                        objRPort['UNIQUE'] = True
                        objRPort['CROSSED'] = False
                        if elemRP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].tag == '{http://autosar.org/schema/r4.0}SHORT-NAME':
                            root_s = elemRP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].text
                            objRPort['ROOT'] = root_s + '/' + root_p
                        RPorts.append(objRPort)
                    # build list of existing connectors
                    for elemC in input_connector:
                        objConn = {}
                        objConn['NAME'] = elemC.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        if elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-P-PORT-REF") is not None:
                            objConn['PROVIDER'] = elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-P-PORT-REF").text
                        if elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-PR-PORT-REF") is not None:
                            objConn['PROVIDER'] = elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-PR-PORT-REF").text
                        objConn['REQUESTER'] = elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-R-PORT-REF").text
                        input_connectors.append(objConn)
                    for elemSW in sw_compos:
                        objSw = {}
                        objSw['NAME'] = elemSW.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                        objSw['TYPE'] = elemSW.find("{http://autosar.org/schema/r4.0}TYPE-TREF").text
                        temp = objSw['TYPE'].split('/')
                        objSw['SWC'] = temp[-1]
                        compos.append(objSw)
    for each_path in simple_arxml:
        for file in os.listdir(each_path):
            if file.endswith('.arxml'):
                fullname = os.path.join(each_path, file)
                try:
                    check_if_xml_is_wellformed(fullname)
                    logger.info('The file: ' + fullname + ' is well-formed')
                except Exception as e:
                    logger.error('The file: ' + fullname + ' is not well-formed: ' + str(e))
                    try:
                        os.remove(output_path + '/Connectors.arxml')
                    except OSError:
                        pass
                    return
                validate_xml_with_xsd(xsd_path, fullname, logger)
                tree = etree.parse(fullname)
                root = tree.getroot()
                PPort = root.findall(".//{http://autosar.org/schema/r4.0}P-PORT-PROTOTYPE")
                PRPort = root.findall(".//{http://autosar.org/schema/r4.0}PR-PORT-PROTOTYPE")
                RPort = root.findall(".//{http://autosar.org/schema/r4.0}R-PORT-PROTOTYPE")
                input_connector = root.findall(".//{http://autosar.org/schema/r4.0}ASSEMBLY-SW-CONNECTOR")
                sw_compos = root.findall(".//{http://autosar.org/schema/r4.0}SW-COMPONENT-PROTOTYPE")
                # build list of PPorts
                for elemPP in PPort:
                    objPPort = {}
                    aswc = elemPP.getparent().getparent().getchildren()[0].text
                    root_p = elemPP.getparent().getparent().getparent().getparent().getchildren()[0].text
                    objPPort['TYPE'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").attrib['DEST']
                    objPPort['FULL-NAME'] = elemPP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                    objPPort['SHORT-NAME'] = objPPort['FULL-NAME'][3:]
                    objPPort['INTERFACE-TYPE'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").attrib['DEST']
                    objPPort['PROVIDED-INTERFACE-TREF'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").text
                    objPPort['ASWC'] = aswc
                    objPPort['ROOT'] = root_p
                    objPPort['CORE'] = ""
                    objPPort['PARTITION'] = ""
                    objPPort['SWC'] = ""
                    objPPort['SINGLE'] = True
                    objPPort['CROSSED'] = False
                    if elemPP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].tag == '{http://autosar.org/schema/r4.0}SHORT-NAME':
                        root_s = elemPP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].text
                        objPPort['ROOT'] = root_s + '/' + root_p
                    PPorts.append(objPPort)
                for elemPRP in PRPort:
                    aswc = elemPRP.getparent().getparent().getchildren()[0].text
                    root_p = elemPRP.getparent().getparent().getparent().getparent().getchildren()[0].text
                    objPRPort = {}
                    objPRPort['FULL-NAME'] = elemPRP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                    objPRPort['SHORT-NAME'] = objPRPort['FULL-NAME'][4:]
                    objPRPort['INTERFACE-TYPE'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").attrib['DEST']
                    objPRPort['PROVIDED-INTERFACE-TREF'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").text
                    objPRPort['TYPE'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").attrib['DEST']
                    objPRPort['ASWC'] = aswc
                    objPRPort['ROOT'] = root_p
                    objPRPort['CORE'] = ""
                    objPRPort['PARTITION'] = ""
                    objPRPort['SWC'] = ""
                    objPRPort['SINGLE'] = True
                    objPRPort['CROSSED'] = False
                    if elemPRP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].tag == '{http://autosar.org/schema/r4.0}SHORT-NAME':
                        root_s = elemPRP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].text
                        objPRPort['ROOT'] = root_s + '/' + root_p
                    PPorts.append(objPRPort)
                # build list of RPorts
                for elemRP in RPort:
                    aswc = elemRP.getparent().getparent().getchildren()[0].text
                    root_p = elemRP.getparent().getparent().getparent().getparent().getchildren()[0].text
                    objRPort = {}
                    objRPort['FULL-NAME'] = elemRP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                    objRPort['SHORT-NAME'] = objRPort['FULL-NAME'][3:]
                    objRPort['INTERFACE-TYPE'] = elemRP.find("{http://autosar.org/schema/r4.0}REQUIRED-INTERFACE-TREF").attrib['DEST']
                    objRPort['REQUIRED-INTERFACE-TREF'] = elemRP.find("{http://autosar.org/schema/r4.0}REQUIRED-INTERFACE-TREF").text
                    objRPort['TYPE'] = elemRP.find("{http://autosar.org/schema/r4.0}REQUIRED-INTERFACE-TREF").attrib['DEST']
                    objRPort['ASWC'] = aswc
                    objRPort['ROOT'] = root_p
                    objRPort['CORE'] = ""
                    objRPort['PARTITION'] = ""
                    objRPort['SWC'] = ""
                    objRPort['SINGLE'] = True
                    objRPort['UNIQUE'] = True
                    objRPort['CROSSED'] = False
                    if elemRP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].tag == '{http://autosar.org/schema/r4.0}SHORT-NAME':
                        root_s = elemRP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].text
                        objRPort['ROOT'] = root_s + '/' + root_p
                    RPorts.append(objRPort)
                # build list of existing connectors
                for elemC in input_connector:
                    objConn = {}
                    objConn['NAME'] = elemC.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                    if elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-P-PORT-REF") is not None:
                        objConn['PROVIDER'] = elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-P-PORT-REF").text
                    if elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-PR-PORT-REF") is not None:
                        objConn['PROVIDER'] = elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-PR-PORT-REF").text
                    objConn['REQUESTER'] = elemC.find(".//{http://autosar.org/schema/r4.0}TARGET-R-PORT-REF").text
                    input_connectors.append(objConn)
                for elemSW in sw_compos:
                    objSw = {}
                    objSw['NAME'] = str(elemSW.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text)
                    objSw['TYPE'] = elemSW.find("{http://autosar.org/schema/r4.0}TYPE-TREF").text
                    temp = objSw['TYPE'].split('/')
                    objSw['SWC'] = temp[-1]
                    compos.append(objSw)
    for each_path in recursive_swc:
        for directory, directories, files in os.walk(each_path):
            for file in files:
                if file.endswith('.xml'):
                    fullname = os.path.join(directory, file)
                    try:
                        check_if_xml_is_wellformed(fullname)
                        logger.info('The file: ' + fullname + ' is well-formed')
                    except Exception as e:
                        logger.error('The file: ' + fullname + ' is not well-formed: ' + str(e))
                        try:
                            os.remove(output_path + '/Connectors.arxml')
                        except OSError:
                            pass
                        return
                    validate_xml_with_xsd(xsd_path, fullname, logger)
                    tree = etree.parse(fullname)
                    root = tree.getroot()
                    swc_allocations = root.findall(".//SWC-ALLOCATION")
                    for elem in swc_allocations:
                        objElem = {}
                        objElem['SWC'] = elem.find("SWC-REF").text
                        objElem['CORE'] = elem.find("CORE").text
                        objElem['PARTITION'] = elem.find("PARTITION").text
                        software_allocs.append(objElem)
    for each_path in simple_swc:
        for file in os.listdir(each_path):
            if file.endswith('.xml'):
                fullname = os.path.join(each_path, file)
                try:
                    check_if_xml_is_wellformed(fullname)
                    logger.info('The file: ' + fullname + ' is well-formed')
                except Exception as e:
                    logger.error('The file: ' + fullname + ' is not well-formed: ' + str(e))
                    try:
                        os.remove(output_path + '/Connectors.arxml')
                    except OSError:
                        pass
                    return
                validate_xml_with_xsd(xsd_path, fullname, logger)
                tree = etree.parse(fullname)
                root = tree.getroot()
                swc_allocations = root.findall(".//SWC-ALLOCATION")
                for elem in swc_allocations:
                    objElem = {}
                    objElem['SWC'] = elem.find("SWC-REF").text
                    objElem['CORE'] = elem.find("CORE").text
                    objElem['PARTITION'] = elem.find("PARTITION").text
                    software_allocs.append(objElem)

    # delete NV-DATA-INTERFACE related ports
    for elemPort in PPorts[:]:
        if elemPort['INTERFACE-TYPE'] == "NV-DATA-INTERFACE":
            PPorts.remove(elemPort)
    for elemPort in RPorts[:]:
        if elemPort['INTERFACE-TYPE'] == "NV-DATA-INTERFACE":
            RPorts.remove(elemPort)

    for index1 in range(len(RPorts)):
        for index2 in range(len(RPorts)):
            if index1 != index2:
                if RPorts[index1]['REQUIRED-INTERFACE-TREF'] == RPorts[index2]['REQUIRED-INTERFACE-TREF']:
                    RPorts[index1]['CROSSED'] = True
                    RPorts[index2]['CROSSED'] = True
    for index1 in range(len(PPorts)):
        for index2 in range(len(PPorts)):
            if index1 != index2:
                if PPorts[index1]['PROVIDED-INTERFACE-TREF'] == PPorts[index2]['PROVIDED-INTERFACE-TREF']:
                    PPorts[index1]['CROSSED'] = True
                    PPorts[index2]['CROSSED'] = True

    for elemPort in PPorts:
        for elemSw in compos:
            if elemPort['ASWC'] == elemSw['SWC']:
                elemPort['SWC'] = elemSw['NAME']
    for elemPort in RPorts:
        for elemSw in compos:
            if elemPort['ASWC'] == elemSw['SWC']:
                elemPort['SWC'] = elemSw['NAME']
    # remove the ports where their ASWC is not referenced into a compo
    for elemPort in PPorts[:]:
        if elemPort['SWC'] == '':
            if elemPort['TYPE'] != "MODE-SWITCH-INTERFACE":
                PPorts.remove(elemPort)
    for elemPort in RPorts[:]:
        if elemPort['SWC'] == '':
            RPorts.remove(elemPort)

    for elemPort in PPorts:
        for elemC in software_allocs:
            if elemPort['ROOT'] in elemC['SWC'] and elemPort['ASWC'] in elemC['SWC']:
                elemPort['CORE'] = elemC['CORE']
                elemPort['PARTITION'] = elemC['PARTITION']
    for elemPort in RPorts:
        for elemC in software_allocs:
            if elemPort['ROOT'] in elemC['SWC'] and elemPort['ASWC'] in elemC['SWC']:
                elemPort['CORE'] = elemC['CORE']
                elemPort['PARTITION'] = elemC['PARTITION']

    # implement TRS.CONNECTOR.FUNC.0003(0) & TRS.CONNECTOR.FUNC.0009(0)
    # filter for multiple PPorts or PRPorts
    # also, if there are several PPorts or PRPorts, and one of them is from <DiagForDcm>, ignore it
    # this creates a new list with valid PPorts to be further used in creating the connectors
    # TODO: define with Julien the name for <AswcDiagForDcm>
    final_pports = []
    for indexPort1 in range(len(PPorts)):
        add = True
        for indexPort2 in range(len(PPorts)):
            if indexPort1 != indexPort2:
                if PPorts[indexPort1]['SHORT-NAME'] == PPorts[indexPort2]['SHORT-NAME'] and PPorts[indexPort1]['PROVIDED-INTERFACE-TREF'] == PPorts[indexPort2]['PROVIDED-INTERFACE-TREF']:
                    if PPorts[indexPort1]['ASWC'] != "AswcDiagForDcm":
                        if PPorts[indexPort2]['ASWC'] == "AswcDiagForDcm":
                            pass
                        else:
                            logger.error('multiple PPorts for interface ' + PPorts[indexPort1]['PROVIDED-INTERFACE-TREF'])
                            add = False
                            logger.error('Connectors file not generated!')
                            try:
                                os.remove(output_path + '/Connectors.arxml')
                            except OSError:
                                pass
                            return
                    else:
                        add = False
        if add:
            final_pports.append(PPorts[indexPort1])
    # create list with MSI PPorts
    msi_pports = []
    for elem in final_pports[:]:
        if elem['INTERFACE-TYPE'] == "MODE-SWITCH-INTERFACE":
            msi_pports.append(elem)
            final_pports.remove(elem)

    # check if there are multiple RPorts with the same SHORT-NAME
    # this creates a new list to be further used in the connectors creation
    final_rports = []
    for indexPort1 in range(len(RPorts)):
        for indexPort2 in range(len(RPorts)):
            if indexPort1 != indexPort2:
                if RPorts[indexPort1]['FULL-NAME'] == RPorts[indexPort2]['FULL-NAME']:
                    RPorts[indexPort1]['UNIQUE'] = False
        final_rports.append(RPorts[indexPort1])
    # create list with MSI RPorts
    msi_rports = []
    for elem in final_rports[:]:
        if elem['INTERFACE-TYPE'] == "MODE-SWITCH-INTERFACE":
            msi_rports.append(elem)
            final_rports.remove(elem)

    # implement TRS.CONNECTOR.FUNC.011
    for elemPP in msi_pports:
        for elemRP in msi_rports:
            if elemPP['PROVIDED-INTERFACE-TREF'] == elemRP['REQUIRED-INTERFACE-TREF']:
                # infos = []
                # if find_between(elemPP['FULL-NAME'], "OsApp_", "_AppSwitchLocalPort") == '':
                #     infos = find_between(elemPP['FULL-NAME'], "OsApp_", "_BswMSwitchLocalPort").split('_', 1)
                # else:
                #     infos = find_between(elemPP['FULL-NAME'], "OsApp_", "_AppSwitchLocalPort").split('_', 1)
                if elemRP['CORE'] in elemPP['FULL-NAME'] and elemRP['PARTITION'] in elemPP['FULL-NAME']:
                    if 'AppSwitchLocalPort' in elemPP['FULL-NAME'] or 'BswMSwitchLocalPort' in elemPP['FULL-NAME']:
                        objConnector = {}
                        objConnector['NAME'] = elemRP['SHORT-NAME']
                        objConnector['INTERFACE'] = elemRP['REQUIRED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-PP'] = elemPP['FULL-NAME']
                        objConnector['PROVIDED-INTERFACE-TREF'] = elemPP['PROVIDED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-RP'] = elemRP['FULL-NAME']
                        objConnector['REQUIRED-INTERFACE-TREF'] = elemRP['REQUIRED-INTERFACE-TREF']
                        objConnector['ASWC-PPORT'] = elemPP['ASWC']
                        objConnector['ASWC-RPORT'] = elemRP['ASWC']
                        objConnector['ROOT-PPORT'] = elemPP['ROOT']
                        objConnector['ROOT-RPORT'] = elemRP['ROOT']
                        objConnector['SWC-PPORT'] = elemPP['SWC']
                        objConnector['SWC-RPORT'] = elemRP['SWC']
                        connectors.append(objConnector)
                        elemRP['SINGLE'] = False
                        elemPP['SINGLE'] = False
                    else:
                        objConnector = {}
                        objConnector['NAME'] = elemRP['SHORT-NAME']
                        objConnector['INTERFACE'] = elemRP['REQUIRED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-PP'] = elemPP['FULL-NAME']
                        objConnector['PROVIDED-INTERFACE-TREF'] = elemPP['PROVIDED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-RP'] = elemRP['FULL-NAME']
                        objConnector['REQUIRED-INTERFACE-TREF'] = elemRP['REQUIRED-INTERFACE-TREF']
                        objConnector['ASWC-PPORT'] = elemPP['ASWC']
                        objConnector['ASWC-RPORT'] = elemRP['ASWC']
                        objConnector['ROOT-PPORT'] = elemPP['ROOT']
                        objConnector['ROOT-RPORT'] = elemRP['ROOT']
                        objConnector['SWC-PPORT'] = elemPP['SWC']
                        objConnector['SWC-RPORT'] = elemRP['SWC']
                        connectors.append(objConnector)
                        elemRP['SINGLE'] = False
                        elemPP['SINGLE'] = False
                else:
                    logger.warning("Not the same CORE or PARTITION for "+elemPP['FULL-NAME']+" and "+elemRP['FULL-NAME']+" referencing the interface"+elemRP['REQUIRED-INTERFACE-TREF'])

    # build list of remainig types of interface connectors
    for indexR in range(len(final_rports)):
        if final_rports[indexR]['CROSSED'] is not True:
            if final_rports[indexR]['UNIQUE']:
                # implement TRS.CONNECTOR.FUNC.0005(0)
                # check only interface
                for indexP in range(len(final_pports)):
                    if final_rports[indexR]['REQUIRED-INTERFACE-TREF'] == final_pports[indexP]['PROVIDED-INTERFACE-TREF']:
                        objConnector = {}
                        objConnector['NAME'] = final_rports[indexR]['SHORT-NAME'][3:]
                        objConnector['INTERFACE'] = final_rports[indexR]['REQUIRED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-PP'] = final_pports[indexP]['FULL-NAME']
                        objConnector['PROVIDED-INTERFACE-TREF'] = final_pports[indexP]['PROVIDED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-RP'] = final_rports[indexR]['FULL-NAME']
                        objConnector['REQUIRED-INTERFACE-TREF'] = final_rports[indexR]['REQUIRED-INTERFACE-TREF']
                        objConnector['ASWC-PPORT'] = final_pports[indexP]['ASWC']
                        objConnector['ASWC-RPORT'] = final_rports[indexR]['ASWC']
                        objConnector['ROOT-PPORT'] = final_pports[indexP]['ROOT']
                        objConnector['ROOT-RPORT'] = final_rports[indexR]['ROOT']
                        objConnector['SWC-PPORT'] = final_pports[indexP]['SWC']
                        objConnector['SWC-RPORT'] = final_rports[indexR]['SWC']
                        connectors.append(objConnector)
                        final_rports[indexR]['SINGLE'] = False
                        final_pports[indexP]['SINGLE'] = False
            else:
                # implement TRS.CONNECTOR.FUNC.0006(0)
                # check short name and interface
                for indexP in range(len(final_pports)):
                    if final_rports[indexR]['REQUIRED-INTERFACE-TREF'] == final_pports[indexP]['PROVIDED-INTERFACE-TREF']:
                        if final_rports[indexR]['FULL-NAME'] == final_pports[indexP]['FULL-NAME']:
                            objConnector = {}
                            objConnector['NAME'] = final_rports[indexR]['FULL-NAME'][3:]
                            objConnector['INTERFACE'] = final_rports[indexR]['REQUIRED-INTERFACE-TREF']
                            objConnector['SHORT-NAME-PP'] = final_pports[indexP]['FULL-NAME']
                            objConnector['PROVIDED-INTERFACE-TREF'] = final_pports[indexP]['PROVIDED-INTERFACE-TREF']
                            objConnector['SHORT-NAME-RP'] = final_rports[indexR]['FULL-NAME']
                            objConnector['REQUIRED-INTERFACE-TREF'] = final_rports[indexR]['REQUIRED-INTERFACE-TREF']
                            objConnector['ASWC-PPORT'] = final_pports[indexP]['ASWC']
                            objConnector['ASWC-RPORT'] = final_rports[indexR]['ASWC']
                            objConnector['ROOT-PPORT'] = final_pports[indexP]['ROOT']
                            objConnector['ROOT-RPORT'] = final_rports[indexR]['ROOT']
                            objConnector['SWC-PPORT'] = final_pports[indexP]['SWC']
                            objConnector['SWC-RPORT'] = final_rports[indexR]['SWC']
                            connectors.append(objConnector)
                            final_rports[indexR]['SINGLE'] = False
                            final_pports[indexP]['SINGLE'] = False
        else:
            for indexP in range(len(final_pports)):
                if final_rports[indexR]['REQUIRED-INTERFACE-TREF'] == final_pports[indexP]['PROVIDED-INTERFACE-TREF']:
                    if final_rports[indexR]['SHORT-NAME'] == final_pports[indexP]['SHORT-NAME']:
                        objConnector = {}
                        objConnector['NAME'] = final_rports[indexR]['FULL-NAME'][3:]
                        objConnector['INTERFACE'] = final_rports[indexR]['REQUIRED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-PP'] = final_pports[indexP]['FULL-NAME']
                        objConnector['PROVIDED-INTERFACE-TREF'] = final_pports[indexP]['PROVIDED-INTERFACE-TREF']
                        objConnector['SHORT-NAME-RP'] = final_rports[indexR]['FULL-NAME']
                        objConnector['REQUIRED-INTERFACE-TREF'] = final_rports[indexR]['REQUIRED-INTERFACE-TREF']
                        objConnector['ASWC-PPORT'] = final_pports[indexP]['ASWC']
                        objConnector['ASWC-RPORT'] = final_rports[indexR]['ASWC']
                        objConnector['ROOT-PPORT'] = final_pports[indexP]['ROOT']
                        objConnector['ROOT-RPORT'] = final_rports[indexR]['ROOT']
                        objConnector['SWC-PPORT'] = final_pports[indexP]['SWC']
                        objConnector['SWC-RPORT'] = final_rports[indexR]['SWC']
                        connectors.append(objConnector)
                        final_rports[indexR]['SINGLE'] = False
                        final_pports[indexP]['SINGLE'] = False
    # throw warning for any unconnected ports
    for indexR in range(len(final_rports)):
        if final_rports[indexR]['SINGLE']:
            logger.warning(final_rports[indexR]['FULL-NAME'] + ' is without connector')
    for indexP in range(len(final_pports)):
        if final_pports[indexP]['SINGLE']:
            logger.warning(final_pports[indexP]['FULL-NAME'] + ' is without connector')
    for indexR in range(len(msi_rports)):
        if msi_rports[indexR]['SINGLE']:
            logger.warning(msi_rports[indexR]['FULL-NAME'] + ' is without connector')
    for indexP in range(len(msi_pports)):
        if msi_pports[indexP]['SINGLE']:
            logger.warning(msi_pports[indexP]['FULL-NAME'] + ' is without connector')

    # implement TRS.CONNECTOR.FUNC.0004(0)
    # delete connector from list of dict if the same connector from input_connectors already exists
    for elem in connectors[:]:
        for elemC in input_connectors:
            if str("/" + elem['ROOT-PPORT'] + "/" + elem['ASWC-PPORT'] + "/" + elem['SHORT-NAME-PP']) == elemC['PROVIDER']:
                if str("/" + elem['ROOT-RPORT'] + "/" + elem['ASWC-RPORT'] + "/" + elem['SHORT-NAME-RP']) == elemC['REQUESTER']:
                    connectors.remove(elem)

    # build Connectors.arxml
    rootConnectors = ET.Element('AUTOSAR')
    rootConnectors.set('xmlns', "http://autosar.org/schema/r4.0")
    rootConnectors.set('xmlns:xsi', "http://www.w3.org/2001/XMLSchema-instance")
    rootConnectors.set('xsi:schemaLocation', "http://autosar.org/schema/r4.0 AUTOSAR_4-2-2_STRICT_COMPACT.xsd")
    packages = ET.SubElement(rootConnectors, 'AR-PACKAGES', xmlns="")
    package = ET.SubElement(packages, 'AR-PACKAGE')
    short_name = ET.SubElement(package, 'SHORT-NAME').text = 'RootP_Composition'
    elements = ET.SubElement(package, 'ELEMENTS')
    compo = ET.SubElement(elements, 'COMPOSITION-SW-COMPONENT-TYPE')
    short_name = ET.SubElement(compo, 'SHORT-NAME').text = 'Compo_VSM'
    connector = ET.SubElement(compo, 'CONNECTORS')
    for con in connectors:
        assembly = ET.SubElement(connector, 'ASSEMBLY-SW-CONNECTOR')
        short_name = ET.SubElement(assembly, 'SHORT-NAME')
        short_name.text = con['SHORT-NAME-PP'] + "_" + con['ASWC-PPORT'] + "_to_" + con['ASWC-RPORT']
        provider = ET.SubElement(assembly, 'PROVIDER-IREF')
        context_provider = ET.SubElement(provider, 'CONTEXT-COMPONENT-REF')
        context_provider.set('DEST', "SW-COMPONENT-PROTOTYPE")
        context_provider.text = '/RootP_Composition/Compo_VSM/' + con['SWC-PPORT']
        if con['SHORT-NAME-PP'][:3] != "PRP":
            target_provided = ET.SubElement(provider, 'TARGET-P-PORT-REF')
            target_provided.set('DEST', "P-PORT-PROTOTYPE")
            target_provided.text = '/' + con['ROOT-PPORT'] + '/' + con['ASWC-PPORT'] + '/' + con['SHORT-NAME-PP']
        else:
            target_provided = ET.SubElement(provider, 'TARGET-PR-PORT-REF')
            target_provided.set('DEST', "PR-PORT-PROTOTYPE")
            target_provided.text = '/' + con['ROOT-PPORT'] + '/' + con['ASWC-PPORT'] + '/' + con['SHORT-NAME-PP']
        requester = ET.SubElement(assembly, 'REQUESTER-IREF')
        context_requester = ET.SubElement(requester, 'CONTEXT-COMPONENT-REF')
        context_requester.set('DEST', "SW-COMPONENT-PROTOTYPE")
        context_requester.text = '/RootP_Composition/Compo_VSM/' + con['SWC-RPORT']
        target_requested = ET.SubElement(requester, 'TARGET-R-PORT-REF')
        target_requested.set('DEST', "R-PORT-PROTOTYPE")
        target_requested.text = '/' + con['ROOT-RPORT'] + '/' + con['ASWC-RPORT'] + '/' + con['SHORT-NAME-RP']
    pretty_xml = prettify_xml(rootConnectors)
    tree = ET.ElementTree(ET.fromstring(pretty_xml))
    tree.write(output_path + '/Connectors.arxml', encoding="UTF-8", xml_declaration=True, method="xml")
    validate_xml_with_xsd(xsd_path, output_path + '/Connectors.arxml', logger)
    # remove ns0 namespace from all file
    ET.register_namespace("", "http://autosar.org/schema/r4.0")
    tree = ET.parse(output_path + '/Connectors.arxml')
    root = tree.getroot()
    output = ET.ElementTree(root)
    output.write(output_path + '/Connectors.arxml', encoding="UTF-8", xml_declaration=True, method="xml")


def arg_parse(parser):
    parser.add_argument("-config", action="store_const", const="-config")
    parser.add_argument("input_configuration_file", help="configuration file location")


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
        logger.warning('The file: ' + path_xml + ' is not valid with the AUTOSAR4.2.2-STRICT schema')
    else:
        logger.info('The file: ' + path_xml + ' is valid with the AUTOSAR4.2.2-STRICT schema')


def check_if_xml_is_wellformed(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)


def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

if __name__ == "__main__":                          # pragma: no cover
    cov = Coverage()                                # pragma: no cover
    cov.start()                                     # pragma: no cover
    main()                                          # pragma: no cover
    cov.stop()                                      # pragma: no cover
    cov.html_report(directory='coverage-html')      # pragma: no cover

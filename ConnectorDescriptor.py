import argparse                             # pragma: no cover
import os                                   # pragma: no cover
import sys                                  # pragma: no cover
import logging                              # pragma: no cover
from xml.sax.handler import ContentHandler  # pragma: no cover
from xml.sax import make_parser             # pragma: no cover
from xml.dom.minidom import parseString     # pragma: no cover
from lxml import etree                      # pragma: no cover
import uuid                                 # pragma: no cover
import datetime


def main():
    # parsing the command line arguments
    parser = argparse.ArgumentParser()
    arg_parse(parser)
    args = parser.parse_args()
    input_path = args.inp
    error = False
    path_list = []
    file_list = []
    entry_list = []
    for path in input_path:
        if path.startswith('@'):
            file = open(path[1:])
            line_file = file.readline()
            while line_file != "":
                line_file = line_file.rstrip()
                line_file = line_file.lstrip()
                if "#" not in line_file:
                    if os.path.isdir(line_file):
                        path_list.append(line_file)
                    elif os.path.isfile(line_file):
                        file_list.append(line_file)
                    else:
                        print("\nError defining the input path: " + line_file + "\n")
                        error = True
                    line_file = file.readline()
                else:
                    line_file = file.readline()
            file.close()
        else:
            if os.path.isdir(path):
                path_list.append(path)
            elif os.path.isfile(path):
                file_list.append(path)
            else:
                print("\nError defining the input path: " + path + "\n")
                error = True
    for path in path_list:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for file in filenames:
                fullname = dirpath + '\\' + file
                file_list.append(fullname)
    [entry_list.append(elem) for elem in file_list if elem not in entry_list]
    if error:
        sys.exit(1)
    output_path = args.out
    output_arxml = args.out_arxml
    output_log = args.out_log
    if output_path:
        if not os.path.isdir(output_path):
            print("\nError defining the output path!\n")
            sys.exit(1)
        if output_log:
            if not os.path.isdir(output_log):
                print("\nError defining the output log path!\n")
                sys.exit(1)
            logger = set_logger(output_log)
            create_connectors(entry_list, output_path, logger)
        else:
            logger = set_logger(output_path)
            create_connectors(entry_list, output_path, logger)
    elif not output_path:
        if output_arxml:
            if not os.path.isdir(output_arxml):
                print("\nError defining the output configuration path!\n")
                sys.exit(1)
            if output_log:
                if not os.path.isdir(output_log):
                    print("\nError defining the output log path!\n")
                    sys.exit(1)
                logger = set_logger(output_log)
                create_connectors(entry_list, output_arxml, logger)
            else:
                logger = set_logger(output_arxml)
                create_connectors(entry_list, output_arxml, logger)
    else:
        print("\nNo output path defined!\n")
        sys.exit(1)


def create_connectors(files_list, output_path, logger):
    NSMAP = {None: 'http://autosar.org/schema/r4.0',
             "xsi": 'http://www.w3.org/2001/XMLSchema-instance'}
    attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
    connectors = []
    PPorts = []
    RPorts = []
    error_no = 0
    warning_no = 0
    info_no = 0
    input_connectors = []
    software_allocs = []
    compos = []
    try:
        for file in files_list:
            if file.endswith('.arxml'):
                try:
                    check_if_xml_is_wellformed(file)
                    logger.info('The file: ' + file + ' is well-formed')
                    info_no = info_no + 1
                except Exception as e:
                    logger.error('The file: ' + file + ' is not well-formed: ' + str(e))
                    print('Error: The file: ' + file + ' is not well-formed: ' + str(e))
                    error_no = error_no + 1
                tree = etree.parse(file)
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
                    if objPPort['FULL-NAME'][:3] == "PP_":
                        objPPort['SHORT-NAME'] = objPPort['FULL-NAME'][3:]
                    elif objPPort['FULL-NAME'][:4] == "MPP_":
                        objPPort['SHORT-NAME'] = objPPort['FULL-NAME'][4:]
                    else:
                        objPPort['SHORT-NAME'] = objPPort['FULL-NAME']
                    objPPort['INTERFACE-TYPE'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").attrib['DEST']
                    objPPort['PROVIDED-INTERFACE-TREF'] = elemPP.find("{http://autosar.org/schema/r4.0}PROVIDED-INTERFACE-TREF").text
                    objPPort['ASWC'] = aswc
                    objPPort['ROOT'] = root_p
                    objPPort['CORE'] = ""
                    objPPort['PARTITION'] = ""
                    objPPort['SWC'] = ""
                    objPPort['SINGLE'] = True
                    objPPort['UNIQUE'] = True
                    objPPort['CROSSED'] = False
                    objPPort['PTYPE'] = "PP"
                    if elemPP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].tag == '{http://autosar.org/schema/r4.0}SHORT-NAME':
                        root_s = elemPP.getparent().getparent().getparent().getparent().getparent().getparent().getchildren()[0].text
                        objPPort['ROOT'] = root_s + '/' + root_p
                    PPorts.append(objPPort)
                for elemPRP in PRPort:
                    aswc = elemPRP.getparent().getparent().getchildren()[0].text
                    root_p = elemPRP.getparent().getparent().getparent().getparent().getchildren()[0].text
                    objPRPort = {}
                    objPRPort['TYPE'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").attrib['DEST']
                    objPRPort['FULL-NAME'] = elemPRP.find("{http://autosar.org/schema/r4.0}SHORT-NAME").text
                    if objPRPort['FULL-NAME'][:3] == "PP_":
                        objPRPort['SHORT-NAME'] = objPRPort['FULL-NAME'][3:]
                    if objPRPort['FULL-NAME'][:4] == "PRP_":
                        objPRPort['SHORT-NAME'] = objPRPort['FULL-NAME'][4:]
                    elif objPRPort['FULL-NAME'][:5] == "MPRP_":
                        objPRPort['SHORT-NAME'] = objPRPort['FULL-NAME'][5:]
                    else:
                        objPRPort['SHORT-NAME'] = objPRPort['FULL-NAME']
                    objPRPort['INTERFACE-TYPE'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").attrib['DEST']
                    objPRPort['PROVIDED-INTERFACE-TREF'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").text
                    objPRPort['TYPE'] = elemPRP.find("{http://autosar.org/schema/r4.0}PROVIDED-REQUIRED-INTERFACE-TREF").attrib['DEST']
                    objPRPort['ASWC'] = aswc
                    objPRPort['ROOT'] = root_p
                    objPRPort['CORE'] = ""
                    objPRPort['PARTITION'] = ""
                    objPRPort['SWC'] = ""
                    objPRPort['SINGLE'] = True
                    objPRPort['UNIQUE'] = True
                    objPRPort['CROSSED'] = False
                    objPRPort['PTYPE'] = "PRP"
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
                    if objRPort['FULL-NAME'][:3] == "RP_":
                        objRPort['SHORT-NAME'] = objRPort['FULL-NAME'][3:]
                    elif objRPort['FULL-NAME'][:4] == "MRP_":
                        objRPort['SHORT-NAME'] = objRPort['FULL-NAME'][4:]
                    else:
                        objRPort['SHORT-NAME'] = objRPort['FULL-NAME']
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
            if file.endswith('.xml'):
                try:
                    check_if_xml_is_wellformed(file)
                    logger.info('The file: ' + file + ' is well-formed')
                    info_no = info_no + 1
                except Exception as e:
                    logger.error('The file: ' + file + ' is not well-formed: ' + str(e))
                    print('Error: The file: ' + file + ' is not well-formed: ' + str(e))
                    error_no = error_no + 1
                tree = etree.parse(file)
                root = tree.getroot()
                swc_allocations = root.findall(".//SWC-ALLOCATION")
                for elem in swc_allocations:
                    objElem = {}
                    objElem['SWC'] = elem.find("SWC-REF").text
                    objElem['CORE'] = elem.find("CORE").text
                    objElem['PARTITION'] = elem.find("PARTITION").text
                    software_allocs.append(objElem)
        if error_no != 0:
            print("There is at least one blocking error! Check the generated log.")
            print("\nExecution stopped with: " + str(info_no) + " infos, " + str(warning_no) + " warnings, " + str(error_no) + " errors\n")
            try:
                os.remove(output_path + '/Connectors.arxml')
            except OSError:
                pass
            sys.exit(1)

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

        # check that the PPort is the only provided port of the interface
        for indexPort1 in range(len(PPorts)):
            for indexPort2 in range(len(PPorts)):
                if indexPort1 != indexPort2:
                    if PPorts[indexPort1]["PROVIDED-INTERFACE-TREF"] == PPorts[indexPort2]["PROVIDED-INTERFACE-TREF"]:
                        PPorts[indexPort1]['UNIQUE'] = False

        # implement TRS.CONNECTOR.FUNC.0003(0) & TRS.CONNECTOR.FUNC.0009(0)
        # filter for multiple PPorts or PRPorts
        # also, if there are several PPorts or PRPorts, and one of them is from <Aswc_IntDcm>, ignore it
        # this creates a new list with valid PPorts to be further used in creating the connectors
        final_pports = []
        for indexPort1 in range(len(PPorts)):
            add = True
            if PPorts[indexPort1]["TYPE"] == "CLIENT-SERVER-INTERFACE" or PPorts[indexPort1]["TYPE"] == "MODE-SWITCH-INTERFACE":
                for indexPort2 in range(len(PPorts)):
                    if indexPort1 != indexPort2:
                        if PPorts[indexPort1]['SHORT-NAME'] == PPorts[indexPort2]['SHORT-NAME'] and PPorts[indexPort1]['PROVIDED-INTERFACE-TREF'] == PPorts[indexPort2]['PROVIDED-INTERFACE-TREF'] and PPorts[indexPort1]['CORE'] == PPorts[indexPort2]['CORE'] and PPorts[indexPort1]['PARTITION'] == PPorts[indexPort2]['PARTITION']:
                            if PPorts[indexPort1]['ASWC'] != "Aswc_IntDcm":
                                if PPorts[indexPort2]['ASWC'] == "Aswc_IntDcm":
                                    pass
                                else:
                                    logger.error('Multiple PPorts for interface ' + PPorts[indexPort1]['PROVIDED-INTERFACE-TREF'] + ": " + PPorts[indexPort1]['FULL-NAME'] + "(ASWC " +PPorts[indexPort1]['ASWC'] + ", CORE " + PPorts[indexPort1]['CORE'] +  ", PARTITION " + PPorts[indexPort1]['PARTITION'] + ")")
                                    print('Error: Multiple PPorts for interface ' + PPorts[indexPort1]['PROVIDED-INTERFACE-TREF'] + ": " + PPorts[indexPort1]['FULL-NAME'] + "(ASWC " +PPorts[indexPort1]['ASWC'] + ", CORE " + PPorts[indexPort1]['CORE'] +  ", PARTITION " + PPorts[indexPort1]['PARTITION'] + ")")
                                    error_no = error_no + 1
                                    add = False
                            else:
                                add = False
            else:
                for indexPort2 in range(len(PPorts)):
                    if indexPort1 != indexPort2:
                        if PPorts[indexPort1]['SHORT-NAME'] == PPorts[indexPort2]['SHORT-NAME'] and PPorts[indexPort1]['PROVIDED-INTERFACE-TREF'] == PPorts[indexPort2]['PROVIDED-INTERFACE-TREF']:
                            if PPorts[indexPort1]['ASWC'] != "Aswc_IntDcm":
                                if PPorts[indexPort2]['ASWC'] == "Aswc_IntDcm":
                                    pass
                                else:
                                    logger.error('Multiple PPorts for interface ' + PPorts[indexPort1]['PROVIDED-INTERFACE-TREF'] + ": " + PPorts[indexPort1]['FULL-NAME'] + "(ASWC " +PPorts[indexPort1]['ASWC'] + ")")
                                    print('Error: Multiple PPorts for interface ' + PPorts[indexPort1]['PROVIDED-INTERFACE-TREF'] + ": " + PPorts[indexPort1]['FULL-NAME'] + "(ASWC " +PPorts[indexPort1]['ASWC'] + ")")
                                    error_no = error_no + 1
                                    add = False
                            else:
                                add = False
            if add:
                final_pports.append(PPorts[indexPort1])
        if error_no != 0:
            print("There is at least one blocking error! Check the generated log.")
            print("\nExecution stopped with: " + str(info_no) + " infos, " + str(warning_no) + " warnings, " + str(error_no) + " errors\n")
            try:
                os.remove(output_path + '/Connectors.arxml')
            except OSError:
                pass
            sys.exit(1)

        # delete PPorts without instance -> them are not to be used
        for elem in final_pports[:]:
            if elem['SWC'] == "":
                final_pports.remove(elem)

        # create list with CSI PPorts
        csi_pports = []
        for elem in final_pports[:]:
            if elem['INTERFACE-TYPE'] == "CLIENT-SERVER-INTERFACE":
                csi_pports.append(elem)
                final_pports.remove(elem)

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

        # delete RPorts without instance -> them are not to be used
        for elem in final_rports[:]:
            if elem['SWC'] == "":
                final_rports.remove(elem)

        # create list with CSI RPorts
        csi_rports = []
        for elem in final_rports[:]:
            if elem['INTERFACE-TYPE'] == "CLIENT-SERVER-INTERFACE":
                csi_rports.append(elem)
                final_rports.remove(elem)

        # create list with MSI RPorts
        msi_rports = []
        for elem in final_rports[:]:
            if elem['INTERFACE-TYPE'] == "MODE-SWITCH-INTERFACE":
                msi_rports.append(elem)
                final_rports.remove(elem)

        # create connector between Pport and Rport referencing a CLIENT-SERVER-INTERFACE
        for elemPP in csi_pports:
            for elemRP in csi_rports:
                if elemPP['UNIQUE']:
                    if elemPP['PROVIDED-INTERFACE-TREF'] == elemRP['REQUIRED-INTERFACE-TREF']:
                        if elemRP['CORE'] == elemPP['CORE'] and elemRP['PARTITION'] == elemPP['PARTITION']:
                            objConnector = {}
                            objConnector['CONNECTOR'] = elemPP['ASWC'] + "_" + elemPP['FULL-NAME'] + "_to_" + elemRP['ASWC'] + "_" + elemRP['FULL-NAME']
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
                            objConnector['PTYPE'] = elemPP['PTYPE']
                            connectors.append(objConnector)
                            elemRP['SINGLE'] = False
                            elemPP['SINGLE'] = False
                        else:
                            logger.warning("Not the same CORE or PARTITION for "+elemPP['FULL-NAME']+" and "+elemRP['FULL-NAME']+" referencing the interface "+elemRP['REQUIRED-INTERFACE-TREF'])
                            warning_no = warning_no + 1
                else:
                    if elemPP['PROVIDED-INTERFACE-TREF'] == elemRP['REQUIRED-INTERFACE-TREF']:
                        if elemRP['CORE'] == elemPP['CORE'] and elemRP['PARTITION'] == elemPP['PARTITION']:
                            if elemPP['SHORT-NAME'] == elemRP['SHORT-NAME']:
                                objConnector = {}
                                objConnector['CONNECTOR'] = elemPP['ASWC'] + "_" + elemPP['FULL-NAME'] + "_to_" + elemRP['ASWC'] + "_" + elemRP['FULL-NAME']
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
                                objConnector['PTYPE'] = elemPP['PTYPE']
                                connectors.append(objConnector)
                                elemRP['SINGLE'] = False
                                elemPP['SINGLE'] = False
                        else:
                            logger.warning("Not the same CORE or PARTITION for "+elemPP['FULL-NAME']+" and "+elemRP['FULL-NAME']+" referencing the interface "+elemRP['REQUIRED-INTERFACE-TREF'])
                            warning_no = warning_no + 1


        # implement TRS.CONNECTOR.FUNC.011
        for elemPP in msi_pports:
            portCore = elemPP['FULL-NAME'].split('_')[-2]
            portPartition = elemPP['FULL-NAME'].split('_')[-1]
            for elemRP in msi_rports:
                if elemPP['PROVIDED-INTERFACE-TREF'] == elemRP['REQUIRED-INTERFACE-TREF']:
                    if elemRP['CORE'] == portCore and elemRP['PARTITION'] == portPartition:
                        objConnector = {}
                        objConnector['CONNECTOR'] = elemPP['ASWC'] + "_" + elemPP['FULL-NAME'] + "_to_" + elemRP['ASWC'] + "_" + elemRP['FULL-NAME']
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
                        objConnector['PTYPE'] = elemPP['PTYPE']
                        connectors.append(objConnector)
                        elemRP['SINGLE'] = False
                        elemPP['SINGLE'] = False
                    else:
                        logger.warning("Not the same CORE or PARTITION for "+elemPP['FULL-NAME']+" and "+elemRP['FULL-NAME']+" referencing the interface "+elemRP['REQUIRED-INTERFACE-TREF'])
                        warning_no = warning_no + 1

        # build list of remainig types of interface connectors
        for indexP in range(len(final_pports)):
            for indexR in range(len(final_rports)):
                # implement TRS.CONNECTOR.FUNC.0005(0)
                # check only interface because the PPort and the RPort are the only ports of their interface
                if final_pports[indexP]['UNIQUE']:
                    if final_rports[indexR]['REQUIRED-INTERFACE-TREF'] == final_pports[indexP]['PROVIDED-INTERFACE-TREF']:
                        objConnector = {}
                        objConnector['CONNECTOR'] = final_pports[indexP]['ASWC'] + "_" + final_pports[indexP]['FULL-NAME'] + "_to_" + final_rports[indexR]['ASWC'] + "_" + final_rports[indexR]['FULL-NAME']
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
                        objConnector['PTYPE'] = final_pports[indexP]['PTYPE']
                        connectors.append(objConnector)
                        final_rports[indexR]['SINGLE'] = False
                        final_pports[indexP]['SINGLE'] = False
                else:
                    # implement TRS.CONNECTOR.FUNC.0006(0)
                    # check short name and interface
                    if final_rports[indexR]['REQUIRED-INTERFACE-TREF'] == final_pports[indexP]['PROVIDED-INTERFACE-TREF']:
                        if final_rports[indexR]['SHORT-NAME'] == final_pports[indexP]['SHORT-NAME']:
                            objConnector = {}
                            objConnector['CONNECTOR'] = final_pports[indexP]['ASWC'] + "_" + final_pports[indexP]['FULL-NAME'] + "_to_" + final_rports[indexR]['ASWC'] + "_" + final_rports[indexR]['FULL-NAME']
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
                            objConnector['PTYPE'] = final_pports[indexP]['PTYPE']
                            connectors.append(objConnector)
                            final_rports[indexR]['SINGLE'] = False
                            final_pports[indexP]['SINGLE'] = False
        # throw warning for any unconnected ports
        for indexR in range(len(final_rports)):
            if final_rports[indexR]['SINGLE']:
                logger.warning(final_rports[indexR]['FULL-NAME'] + ' is without connector')
                warning_no = warning_no + 1
        for indexP in range(len(final_pports)):
            if final_pports[indexP]['SINGLE']:
                logger.warning(final_pports[indexP]['FULL-NAME'] + ' is without connector')
                warning_no = warning_no + 1
        for indexR in range(len(csi_rports)):
            if csi_rports[indexR]['SINGLE']:
                logger.warning(csi_rports[indexR]['FULL-NAME'] + ' is without connector')
                warning_no = warning_no + 1
        for indexP in range(len(csi_pports)):
            if csi_pports[indexP]['SINGLE']:
                logger.warning(csi_pports[indexP]['FULL-NAME'] + ' is without connector')
                warning_no = warning_no + 1
        for indexR in range(len(msi_rports)):
            if msi_rports[indexR]['SINGLE']:
                logger.warning(msi_rports[indexR]['FULL-NAME'] + ' is without connector')
                warning_no = warning_no + 1
        for indexP in range(len(msi_pports)):
            if msi_pports[indexP]['SINGLE']:
                logger.warning(msi_pports[indexP]['FULL-NAME'] + ' is without connector')
                warning_no = warning_no + 1

        # implement TRS.CONNECTOR.FUNC.0004(0)
        # delete connector from list of dict if the same connector from input_connectors already exists
        for elemC in input_connectors:
            for elem in connectors[:]:
                if str("/" + elem['ROOT-PPORT'] + "/" + elem['ASWC-PPORT'] + "/" + elem['SHORT-NAME-PP']) == elemC['PROVIDER']:
                    if str("/" + elem['ROOT-RPORT'] + "/" + elem['ASWC-RPORT'] + "/" + elem['SHORT-NAME-RP']) == elemC['REQUESTER']:
                        connectors.remove(elem)

        # remove duplicates
        connectors = list(unique_items(connectors))
        # build Connectors.arxml
        rootConnectors = etree.Element('AUTOSAR', {attr_qname: 'http://autosar.org/schema/r4.0 AUTOSAR_4-2-2_STRICT_COMPACT.xsd'}, nsmap=NSMAP)
        packages = etree.SubElement(rootConnectors, 'AR-PACKAGES')
        package = etree.SubElement(packages, 'AR-PACKAGE')
        short_name = etree.SubElement(package, 'SHORT-NAME').text = 'RootP_Composition'
        elements = etree.SubElement(package, 'ELEMENTS')
        compo = etree.SubElement(elements, 'COMPOSITION-SW-COMPONENT-TYPE')
        short_name = etree.SubElement(compo, 'SHORT-NAME').text = 'Compo_VSM'
        connector = etree.SubElement(compo, 'CONNECTORS')
        for con in connectors:
            assembly = etree.SubElement(connector, 'ASSEMBLY-SW-CONNECTOR')
            short_name = etree.SubElement(assembly, 'SHORT-NAME')
            # short_name.text = con['ASWC-PPORT'] + "_" + con['SHORT-NAME-PP'] + "_to_" + con['ASWC-RPORT'] + "_" + con['SHORT-NAME-RP']
            short_name.text = "ASSEMBLY_CONNECTOR_" + uuid.uuid4().hex[:6].upper() + "_" + uuid.uuid4().hex[:6].upper() + "_" + uuid.uuid4().hex[:6].upper() + "_" + str(datetime.datetime.now()).split(".")[-1]
            provider = etree.SubElement(assembly, 'PROVIDER-IREF')
            context_provider = etree.SubElement(provider, 'CONTEXT-COMPONENT-REF')
            context_provider.set('DEST', "SW-COMPONENT-PROTOTYPE")
            context_provider.text = '/RootP_Composition/Compo_VSM/' + con['SWC-PPORT']
            if con['PTYPE'] != "PRP":
                target_provided = etree.SubElement(provider, 'TARGET-P-PORT-REF')
                target_provided.set('DEST', "P-PORT-PROTOTYPE")
                target_provided.text = '/' + con['ROOT-PPORT'] + '/' + con['ASWC-PPORT'] + '/' + con['SHORT-NAME-PP']
            else:
                target_provided = etree.SubElement(provider, 'TARGET-P-PORT-REF')
                target_provided.set('DEST', "PR-PORT-PROTOTYPE")
                target_provided.text = '/' + con['ROOT-PPORT'] + '/' + con['ASWC-PPORT'] + '/' + con['SHORT-NAME-PP']
            requester = etree.SubElement(assembly, 'REQUESTER-IREF')
            context_requester = etree.SubElement(requester, 'CONTEXT-COMPONENT-REF')
            context_requester.set('DEST', "SW-COMPONENT-PROTOTYPE")
            context_requester.text = '/RootP_Composition/Compo_VSM/' + con['SWC-RPORT']
            target_requested = etree.SubElement(requester, 'TARGET-R-PORT-REF')
            target_requested.set('DEST', "R-PORT-PROTOTYPE")
            target_requested.text = '/' + con['ROOT-RPORT'] + '/' + con['ASWC-RPORT'] + '/' + con['SHORT-NAME-RP']
        pretty_xml = prettify_xml(rootConnectors)
        tree = etree.ElementTree(etree.fromstring(pretty_xml))
        tree.write(output_path + '/Connectors.arxml', encoding="UTF-8", xml_declaration=True, method="xml")
        #################################
        if error_no != 0:
            print("There is at least one blocking error! Check the generated log.")
            print("\nExecution stopped with: " + str(info_no) + " infos, " + str(warning_no) + " warnings, " + str(error_no) + " errors\n")
            try:
                os.remove(output_path + '/Connectors.arxml')
            except OSError:
                pass
            sys.exit(1)
        else:
            print("\nExecution finished with: " + str(info_no) + " infos, " + str(warning_no) + " warnings, " + str(error_no) + " errors\n")
    except Exception as e:
        print("Unexpected error: " + str(e))
        print("\nExecution stopped with: " + str(info_no) + " infos, " + str(warning_no) + " warnings, " + str(error_no) + " errors\n")
        try:
            os.remove(output_path + '/Connectors.arxml')
        except OSError:
            pass
        sys.exit(1)


def arg_parse(parser):
    parser.add_argument('-in', '--inp', nargs='*', help="input path or file", required=True, default="")
    parser.add_argument('-out', '--out', help="output path", required=False, default="")
    parser.add_argument('-out_arxml', '--out_arxml', help="output path for configuration file(s)", required=False, default="")
    parser.add_argument('-out_log', '--out_log', help="output path for log file", required=False, default="")


def set_logger(path):
    # logger creation and setting
    logger = logging.getLogger('result')
    hdlr = logging.FileHandler(path + '/result_ConDesc.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)
    open(path + '/result_ConDesc.log', 'w').close()
    return logger


def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = etree.tostring(elem, pretty_print=True)
    reparsed = parseString(rough_string)
    return '\n'.join([line for line in reparsed.toprettyxml(indent=' ' * 4).split('\n') if line.strip()])


def check_if_xml_is_wellformed(file):
    parser = make_parser()
    parser.setContentHandler(ContentHandler())
    parser.parse(file)


def unique_items(list_to_check):
    found = set()
    for item in list_to_check:
        if item['CONNECTOR'] not in found:
            yield item
            found.add(item['CONNECTOR'])


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


if __name__ == "__main__":                          # pragma: no cover
    # process = psutil.Process(os.getpid())
    # start_time = time.clock()
    # cov = Coverage()                                # pragma: no cover
    # cov.start()                                     # pragma: no cover
    main()                                          # pragma: no cover
    # cov.stop()                                      # pragma: no cover
    # cov.html_report(directory='coverage-html')      # pragma: no cover
    # print(str(time.clock() - start_time) + " seconds ")
    # print(str(process.memory_info()[0]/float(2**20)) + " MB ")

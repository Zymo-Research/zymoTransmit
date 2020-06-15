import os
import typing
import argparse

try: # Stuff will seriously break if there is no config file, so if it is missing, this will create the template
    from zymoTransmitSupport import config
except ImportError:
    import shutil
    cleanConfig = os.path.join("zymoTransmitSupport", "configClean.py")
    newConfig = os.path.join("zymoTransmitSupport", "config.py")
    shutil.copy(cleanConfig, newConfig)
    print("No config file was found at the expected location. Please input your lab information into the config file at:\n%s" %(os.path.abspath(newConfig)))
    import zymoTransmitSupport
    if zymoTransmitSupport.gui.active:
        print("Opening config file for editing. Please save and exit when done.")
        zymoTransmitSupport.gui.textEditFile(newConfig)
    else:
        print("GUI appears inactive, unable to open configuration file")
    quit()

import zymoTransmitSupport


class CheckArgs(object):

    __slots__ = ["input"]

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--testConnection", help = "Test connection to upload site only", action = 'store_true')
        parser.add_argument("-l", "--loinc", help = "Display potentially relevant LOINC codes",  action = 'store_true')
        parser.add_argument("-s", "--snomed", help = "Display potentially relevant SNOMED codes",  action = 'store_true')
        parser.add_argument("-c", "--convertCertificate", help = "Convert certificate file [certificate path]", action = 'store_true')
        parser.add_argument("-e", "--editConfig", help = "Edit configuration file", action = 'store_true')
        parser.add_argument("input", help = "Input file/folder", type = str, nargs='?')
        rawArgs = parser.parse_args()
        testConnection = rawArgs.testConnection
        convertCertificate = rawArgs.convertCertificate
        editConfig = rawArgs.editConfig
        loinc = rawArgs.loinc
        snomed = rawArgs.snomed
        input = rawArgs.input
        if testConnection or loinc or snomed:
            if loinc:
                print("LOINC codes of potential interest:")
                zymoTransmitSupport.hl7Encoder.loinc.printLoincTable()
                print()
            if snomed:
                print("SNOMED codes of potential interest:")
                zymoTransmitSupport.hl7Encoder.snomed.printSnomedTable()
            if testConnection:
                certificatePath = os.path.join(config.Connection.certificateFolder, config.Connection.certificateFileName)
                zymoTransmitSupport.inputOutput.connection.getSOAPClient(
                    config.Connection.wsdlURL,
                    certificatePath,
                    testOnly=True)
            quit()
        if editConfig:
            if zymoTransmitSupport.gui.active:
                print("Opening config file for editing. Please save and exit when done.")
                zymoTransmitSupport.gui.textEditFile(newConfig)
            else:
                print("GUI appears inactive, unable to open configuration file")
            quit()
        if not input:
            if zymoTransmitSupport.gui.active:
                if convertCertificate:
                    openPrompt = "Select certificate for opening."
                    fileTypes = (("PFX Certificate", "*.pfx"), ("All Files", "*.*"))
                else:
                    openPrompt = "Select result table for opening."
                    fileTypes = (("Text", "*.txt"), ("All Files", "*.*"))
                input = zymoTransmitSupport.gui.selectFileForOpening(openPrompt, fileTypes=fileTypes)
                if not input:
                    quit("No file was selected.")
            else:
                raise ValueError("No input file path supplied and GUI is not active to prompt.")
        if not os.path.isfile(input):
            raise FileNotFoundError("No such file %s" %input)
        self.input = input
        if convertCertificate:
            convertPFX(self.input)
            print("Converted certificate %s" %self.input)
            quit()


def convertPFX(pfxPath:str, pfxPassword:str=None):
    pemPath = zymoTransmitSupport.authentication.certHandler.convertPFX(pfxPath, config.Connection.certificateFolder, pfxPassword)
    return pemPath


def getTestResults(testResultPath:str="results.txt"):
    resultList = zymoTransmitSupport.inputOutput.resultReader.loadRawDataTable(testResultPath)
    return resultList


def makeHL7Codes(resultList:typing.List[zymoTransmitSupport.inputOutput.resultReader.TestResult]):
    hl7Sets = {}
    for result in resultList:
        patientID = result.patientID
        specimenID = result.specimenID
        hl7Sets[(patientID, specimenID)] = []
        currentSet = hl7Sets[(patientID, specimenID)]
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeMSHLine())
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeSFTLine())
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makePIDLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeORCLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeOBRLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeOBXLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeSPMLine(result))
        if result.note:
            currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeNTELine(result))
    return hl7Sets


def makeHL7Blocks(hl7Sets:typing.Dict[typing.Tuple[str, str], typing.List[zymoTransmitSupport.hl7Encoder.generics.Hl7Line]]):
    hl7Blocks = {}
    for resultID, hl7Set in hl7Sets.items():
        textBlock = "\n".join(str(line) for line in hl7Set)
        hl7Blocks[resultID] = textBlock
    return hl7Blocks


def main(args:CheckArgs):
    certificateFilePath = os.path.join(config.Connection.certificateFolder, config.Connection.certificateFileName)
    client, session = zymoTransmitSupport.inputOutput.connection.getSOAPClient(
        config.Connection.wsdlURL, certificateFilePath, dumpClientInfo=False)
    resultList = getTestResults(args.input)
    hl7Sets = makeHL7Codes(resultList)
    hl7TextBlocks = makeHL7Blocks(hl7Sets)
    transmissionResults = zymoTransmitSupport.inputOutput.soapAPI.transmitBlocks(client, hl7TextBlocks)
    resultText = zymoTransmitSupport.inputOutput.logger.writeLogFile(config.Configuration.logFolder, transmissionResults)
    print(resultText)


def makeDirectoriesIfNeeded():
    if not os.path.isdir(config.Connection.certificateFolder):
        os.mkdir(config.Connection.certificateFolder)
    if not os.path.isdir(config.Configuration.logFolder):
        os.mkdir(config.Configuration.logFolder)


if __name__  == "__main__":
    makeDirectoriesIfNeeded()
    args = CheckArgs()
    main(args)

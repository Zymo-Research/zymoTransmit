import os

contentRoot = os.path.split(os.path.abspath(__file__))[0]

import typing
import argparse

try: # Stuff will seriously break if there is no config file, so if it is missing, this will create the template
    from zymoTransmitSupport import config
except FileNotFoundError:
    import shutil
    cleanConfig = os.path.join(contentRoot, "zymoTransmitSupport", "configClean.txt")
    newConfig = os.path.join(contentRoot, "config.txt")
    shutil.copy(cleanConfig, newConfig)
    print("No config file was found at the expected location. Please input your lab information into the config file at:\n%s" %(os.path.abspath(newConfig)))
    import zymoTransmitSupport
    if zymoTransmitSupport.gui.active:
        print("Opening config file for editing. Please save and exit when done.")
        zymoTransmitSupport.gui.textEditFile(newConfig)
    else:
        print("GUI appears inactive, unable to open configuration file")
    input("Press enter to quit.")
    quit()

import zymoTransmitSupport


class CheckArgs(object):

    __slots__ = ["input", "noTransmit"]

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--testConnection", help = "Test connection to upload site only", action = 'store_true')
        parser.add_argument("-l", "--loinc", help = "Display potentially relevant LOINC codes",  action = 'store_true')
        parser.add_argument("-s", "--snomed", help = "Display potentially relevant SNOMED codes",  action = 'store_true')
        parser.add_argument("-c", "--convertCertificate", help = "Convert certificate file [certificate path]", action = 'store_true')
        parser.add_argument("-e", "--editConfig", help = "Edit configuration file", action = 'store_true')
        parser.add_argument("-n", "--noTransmit", help = "Do not attempt to transmit datat", action = 'store_true')
        parser.add_argument("input", help = "Input file", type = str, nargs='?')
        rawArgs = parser.parse_args()
        testConnection = rawArgs.testConnection
        convertCertificate = rawArgs.convertCertificate
        editConfig = rawArgs.editConfig
        loinc = rawArgs.loinc
        snomed = rawArgs.snomed
        inputValue = rawArgs.input
        self.noTransmit = rawArgs.noTransmit
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
            input("Press enter to quit.")
            quit()
        if editConfig:
            if zymoTransmitSupport.gui.active:
                print("Opening config file for editing. Please save and exit when done.")
                zymoTransmitSupport.gui.textEditFile(os.path.join(contentRoot, "config.txt"))
            else:
                print("GUI appears inactive, unable to open configuration file")
            input("Press enter to quit.")
            quit()
        if not inputValue:
            if zymoTransmitSupport.gui.active:
                if convertCertificate:
                    openPrompt = "Select certificate for opening."
                    fileTypes = (("PFX Certificate", "*.pfx"), ("All Files", "*.*"))
                else:
                    openPrompt = "Select result table for opening."
                    fileTypes = (("Text/HL7/Cert", "*.txt *.csv *.tdf *.hl7 *.pfx"), ("All Files", "*.*"))
                inputValue = zymoTransmitSupport.gui.selectFileForOpening(openPrompt, fileTypes=fileTypes)
                if not inputValue:
                    input("No file selected. Press enter to quit.")
                    quit("No file was selected.")
            else:
                raise ValueError("No input file path supplied and GUI is not active to prompt.")
        if not os.path.isfile(inputValue):
            raise FileNotFoundError("No such file %s" %inputValue)
        self.input = inputValue
        if convertCertificate:
            convertPFX(self.input)
            input("Press enter to quit.")
            quit()


def convertPFX(pfxPath:str, pfxPassword:str=None):
    pemPath = zymoTransmitSupport.authentication.certHandler.convertPFX(pfxPath, os.path.join(contentRoot, config.Connection.certificateFolder), pfxPassword)
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
        textBlock += "\n"
        hl7Blocks[resultID] = textBlock
    return hl7Blocks


def makeHL7TextRecord(hl7Blocks:typing.Dict[typing.Tuple[str, str], str]):
    textRecord = ""
    for identifier, text in hl7Blocks.items():
        textRecord += text
    return textRecord


def main(args:CheckArgs):
    if os.path.abspath(args.input) == os.path.join(contentRoot, "config.txt"):
        if zymoTransmitSupport.gui.active:
            print("Opening config file for editing. Please save and exit when done.")
            zymoTransmitSupport.gui.textEditFile(os.path.join(args.input))
        else:
            print("GUI appears inactive, unable to open configuration file")
        input("Press enter to quit.")
        quit()
    if args.input.endswith(".pfx"):
        if zymoTransmitSupport.gui.active:
            password = zymoTransmitSupport.gui.promptForCertPassword()
            convertPFX(args.input, pfxPassword=password)
        input("Press enter to quit.")
        quit()
    certificateFilePath = os.path.join(contentRoot, config.Connection.certificateFolder, config.Connection.certificateFileName)
    client, session = zymoTransmitSupport.inputOutput.connection.getSOAPClient(
        config.Connection.wsdlURL, certificateFilePath, dumpClientInfo=False)
    if args.input.lower().endswith(".hl7"):
        print("Using raw HL7 from file %s" %args.input)
        hl7TextBlocks = zymoTransmitSupport.inputOutput.rawHL7.textBlocksFromRawHL7(args.input)
    else:
        resultList = getTestResults(args.input)
        hl7Sets = makeHL7Codes(resultList)
        hl7TextBlocks = makeHL7Blocks(hl7Sets)
    hl7TextRecord = makeHL7TextRecord(hl7TextBlocks)
    if not args.noTransmit:
        transmissionResults = zymoTransmitSupport.inputOutput.soapAPI.transmitBlocks(client, hl7TextBlocks)
        resultText = zymoTransmitSupport.inputOutput.logger.writeLogFile(config.Configuration.logFolder, transmissionResults, hl7TextRecord)
        print(resultText)
    else:
        print("Results not transmitted due to argument noTransmit being set to true.")


def makeDirectoriesIfNeeded():
    if not os.path.isdir(os.path.join(contentRoot, config.Connection.certificateFolder)):
        os.mkdir(os.path.join(contentRoot, config.Connection.certificateFolder))
    if not os.path.isdir(os.path.join(contentRoot, config.Configuration.logFolder)):
        os.mkdir(os.path.join(contentRoot, config.Configuration.logFolder))


if __name__ == "__main__":
    makeDirectoriesIfNeeded()
    args = CheckArgs()
    main(args)
    input("Press enter to quit.")
    quit()

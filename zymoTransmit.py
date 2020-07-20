try:
    import os
    import sys
    import traceback
    import csv

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

except Exception as err:
    print("Encountered an unhandled error as follows:")
    traceback.print_exc()
    input("Run crashed before beginning. A common cause for this can be a corrupt config.txt file. Press enter to quit.")
    sys.exit(1)


class CheckArgs(object):

    __slots__ = ["input", "noTransmit", "hl7Directory", "cdph", "debug"]

    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-t", "--testConnection", help = "Test connection to upload site only", action = 'store_true')
        parser.add_argument("-l", "--loinc", help = "Display potentially relevant LOINC codes",  action = 'store_true')
        parser.add_argument("-s", "--snomed", help = "Display potentially relevant SNOMED codes",  action = 'store_true')
        parser.add_argument("-c", "--convertCertificate", help = "Convert certificate file [certificate path]", action = 'store_true')
        parser.add_argument("-e", "--editConfig", help = "Edit configuration file", action = 'store_true')
        parser.add_argument("-n", "--noTransmit", help = "Do not attempt to transmit data", action = 'store_true')
        parser.add_argument("-d", "--hl7Directory", help = "Upload a directory of HL7 files", action = 'store_true')
        parser.add_argument("--cdph", help = "Read CDPH format with header line", action = 'store_true')
        parser.add_argument("--debug", help="Running in debugging mode", action='store_true')
        parser.add_argument("input", help = "Input file", type = str, nargs='?')
        rawArgs = parser.parse_args()
        testConnection = rawArgs.testConnection
        convertCertificate = rawArgs.convertCertificate
        editConfig = rawArgs.editConfig
        loinc = rawArgs.loinc
        snomed = rawArgs.snomed
        inputValue = rawArgs.input
        self.noTransmit = rawArgs.noTransmit
        self.hl7Directory = rawArgs.hl7Directory
        self.cdph = rawArgs.cdph
        self.debug = rawArgs.debug
        if self.hl7Directory and convertCertificate:
            raise RuntimeError("Error: Program cannot be set to both process a certificate AND take in a directory for upload")
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
                if self.hl7Directory:
                    openPrompt = "Select directory for batch HL7 upload"
                    inputValue = zymoTransmitSupport.gui.selectDirectoryForOpening(openPrompt)
                else:
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
        if not self.hl7Directory and not os.path.isfile(inputValue):
            raise FileNotFoundError("No such file %s" %inputValue)
        self.input = inputValue
        if os.path.abspath(self.input) == os.path.abspath(os.path.join(contentRoot, "rejects.csv")):
            raise RuntimeError("Please avoid running this program directly on the rejects.csv file it creates.  Resubmitting this file after correcting any issues IS recommended, but only after renaming that file to something else.")
        if convertCertificate:
            convertPFX(self.input)
            input("Press enter to quit.")
            quit()


def convertPFX(pfxPath:str, pfxPassword:str=None):
    pemPath = zymoTransmitSupport.authentication.certHandler.convertPFX(pfxPath, os.path.join(contentRoot, config.Connection.certificateFolder), pfxPassword)
    return pemPath


def getTestResults(testResultPath:str="results.txt", cdphCSV:bool=False):
    resultList = zymoTransmitSupport.inputOutput.resultReader.loadRawDataTable(testResultPath, cdphCSV)
    return resultList


def makeHL7Codes(resultList:typing.List[zymoTransmitSupport.inputOutput.resultReader.TestResult]):
    hl7Sets = {}
    for result in resultList:
        patientID = result.patientID
        specimenID = result.specimenID
        hl7Sets[(patientID, specimenID)] = []
        currentSet = hl7Sets[(patientID, specimenID)]
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeMSHLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeSFTLine())
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makePIDLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeORCLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeOBRLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeOBXLine(result))
        currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeSPMLine(result))
        if result.note:
            currentSet.append(zymoTransmitSupport.hl7Encoder.encoders.makeNTELine(result))
        if not result.okToTransmit:
            print("Skipping preparation of %s:%s for the following reasons:" %(result.patientID, result.specimenID))
            for reason in result.reasonForFailedTransmission:
                print("\t%s" %reason)
            del hl7Sets[(patientID, specimenID)]
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


def processRejects(resultList:typing.List[zymoTransmitSupport.inputOutput.resultReader.TestResult], delimiter:str="\t"):
    file = open(os.path.join(contentRoot, "rejects.csv"), 'a', newline="")
    for result in resultList:
        csvHandle = csv.writer(file)
        if result.okToTransmit and result.transmittedSuccessfully:
            continue
        if type(result.rawLine) == str:
            csvHandle.writerow(result.rawLine.split(delimiter))
        else:
            csvHandle.writerow(result.rawLine)
    file.close()


def prepareAndSendResults(args:CheckArgs):
    if not args.hl7Directory:
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
    skippedData = []
    resultList = []
    certificateFilePath = os.path.join(contentRoot, config.Connection.certificateFolder, config.Connection.certificateFileName)
    client, session = zymoTransmitSupport.inputOutput.connection.getSOAPClient(
        config.Connection.wsdlURL, certificateFilePath, dumpClientInfo=False)
    if args.hl7Directory:
        if not os.path.isdir(args.input):
            raise NotADirectoryError("%s was given as a directory for raw HL7 block files, but it is not a directory.")
        hl7TextBlocks = zymoTransmitSupport.inputOutput.hl7DirectoryReader.makeHL7BlocksFromDirectory(args.input)
    else:
        if args.input.lower().endswith(".hl7"):
            print("Using raw HL7 from file %s" %args.input)
            hl7TextBlocks = zymoTransmitSupport.inputOutput.rawHL7.textBlocksFromRawHL7(args.input)
        else:
            resultList = getTestResults(args.input, args.cdph)
            hl7Sets = makeHL7Codes(resultList)
            hl7TextBlocks = makeHL7Blocks(hl7Sets)
    hl7TextRecord = makeHL7TextRecord(hl7TextBlocks)
    if not args.noTransmit:
        transmissionResults = zymoTransmitSupport.inputOutput.soapAPI.transmitBlocks(client, hl7TextBlocks, resultList)
        resultText = zymoTransmitSupport.inputOutput.logger.writeLogFile(config.Configuration.logFolder, transmissionResults, hl7TextRecord)
        print(resultText)
        for result in resultList:
            if not (result.okToTransmit and result.transmittedSuccessfully):
                skippedData.append((result.patientID, result.specimenID, result.reasonForFailedTransmission))
        if skippedData:
            print("\n\nWARNING: SOME RESULTS WERE SKIPPED, FAILED TO TRANSMIT, OR WERE REJECTED BY THE GATEWAY FOR REASONS BELOW:\n")
            for patientID, specimenID, reasons in skippedData:
                print("%s:%s was not successfully transmitted because:" %(patientID, specimenID))
                for reason in reasons:
                    print("\t%s" %reason)
    else:
        print("Results not transmitted due to argument noTransmit being set to true.")
    if skippedData:
        processRejects(resultList)


def makeDirectoriesIfNeeded():
    if not os.path.isdir(os.path.join(contentRoot, config.Connection.certificateFolder)):
        os.mkdir(os.path.join(contentRoot, config.Connection.certificateFolder))
    if not os.path.isdir(os.path.join(contentRoot, config.Configuration.logFolder)):
        os.mkdir(os.path.join(contentRoot, config.Configuration.logFolder))
    if not os.path.isfile(os.path.join(contentRoot, "rejects.csv")):
        file = open(os.path.join(contentRoot, "rejects.csv"), 'w')
        file.write("#Header for lines that were not transmitted due to issue with interpretation\n")
        file.close()


class PlaceHolderException(Exception):
    pass


def main():
    if "--debug" in sys.argv:
        allOrNothingException = PlaceHolderException
    else:
        allOrNothingException = Exception
    try:
        makeDirectoriesIfNeeded()
        args = CheckArgs()
        prepareAndSendResults(args)
    except allOrNothingException as err:
        print("Encountered an unhandled error as follows:")
        traceback.print_exc()
        input("Run was not successful. Press enter to quit")
        sys.exit(1)


if __name__ == "__main__":
    main()
    input("Completed successfully. Press enter to quit.")
    quit()

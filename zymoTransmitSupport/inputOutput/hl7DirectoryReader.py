import os
import re
from .. import hl7Encoder

hl7LineStartRegex = re.compile(r"\w\w\w\|", re.IGNORECASE)
softwareLineRegex = re.compile(r"^SFT\|", re.IGNORECASE | re.MULTILINE)


def getFileList(targetDirectory:str):
    filteredFiles = []
    rawFiles = os.listdir(targetDirectory)
    for file in rawFiles:
        fullPath = os.path.join(targetDirectory, file)
        if not os.path.isfile(fullPath):
            continue
        try:
            probeFile = open(fullPath)
            first4 = probeFile.read(4)
            line = probeFile.readline()
            while line: # This loop will throw some error if there are non-text characters in the file
                line = probeFile.readline()
        except: # Using a catch all here because if a file can't be opened this way, it will break everything later and I'm probably not interested in it anyway
            continue
        if not hl7LineStartRegex.match(first4):
            continue
        baseName = ".".join(file.split(".")[:-1])
        fileInfoTuple = (baseName, fullPath)
        filteredFiles.append(fileInfoTuple)
    return filteredFiles


def processRawHL7Block(rawBlock:str):
    rawBlock = rawBlock.strip()
    if not softwareLineRegex.search(rawBlock):
        softwareLine = hl7Encoder.encoders.makeSFTLine(passThruMode=True)
        rawBlock = "%s\n%s" %(softwareLine, rawBlock)
    if not rawBlock.startswith("MSH|"):
        messageHeader = hl7Encoder.encoders.makeMSHLine()
        rawBlock = "%s\n%s" %(messageHeader, rawBlock)
    rawBlock += "\n"
    return rawBlock


def makeHL7BlocksFromDirectory(targetDirectory:str):
    hl7Blocks = {}
    filteredFiles = getFileList(targetDirectory)
    for baseName, fullPath in filteredFiles:
        rawBlock = open(fullPath).read()
        hl7Blocks[("Batch HL7: %s" %baseName)] = processRawHL7Block(rawBlock)
    return hl7Blocks


import os

def readRawHL7(filePath: str):
    if not os.path.isfile(filePath):
        raise FileNotFoundError("Unable to find raw HL7 file at %s" % filePath)
    file = open(filePath)
    text = file.read()
    file.close()
    text = text.strip()
    text = text + "\n"
    return text


def textBlocksFromRawHL7(filePath: str):
    if not os.path.isfile(filePath):
        raise FileNotFoundError("Unable to find raw HL7 file at %s" % filePath)
    text = readRawHL7(filePath)
    fileName = os.path.split(filePath)[1]
    fileBase = ".".join(fileName.split(".")[:-1])
    textBlock = {
        ("Raw HL7", fileBase): text
    }
    return textBlock
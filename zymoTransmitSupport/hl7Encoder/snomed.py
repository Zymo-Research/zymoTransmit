import os
import typing


class SNOMED(object):

    def __init__(self, code:str, fullName:str, preferredName:str):
        self.code = code
        self.fullName = fullName
        self.preferredName = preferredName

    def __str__(self):
        outputLines = []
        outputLines.append("\t".join([self.code, self.preferredName]))
        outputLines.append("\t" + self.fullName)
        return "\n".join(outputLines)


class EmptySNOMED(object):

    def __init__(self):
        self.code = ""
        self.fullName = ""
        self.preferredName = ""

    def __str__(self):
        return "#Empty SNOMED code"


def loadRawDataTable():
    inputFileDirectory = os.path.split(os.path.abspath(__file__))[0]
    inputFileDirectory = os.path.split(inputFileDirectory)[0]
    inputFileDirectory = os.path.split(inputFileDirectory)[0]
    inputFile = "snomedSpecimens.txt"
    inputPath = os.path.join(inputFileDirectory, inputFile)
    data = open(inputPath, 'r').readlines()
    data = [line.strip() for line in data if line and not line.startswith("#")]
    data = [line.split("\t") for line in data if line]
    dataTable = []
    for line in data:
        line = [element.strip() for element in line]
        if len(line) == 7:
            line.append("")
        dataTable.append(line)
    return dataTable


def makeSnomedTable(data:list):
    loincTable = {}
    for line in data:
        code, fullName, preferredName = line
        loincTable[code] = SNOMED(code, fullName, preferredName)
    return loincTable


def makeLookupTables(loincTable:typing.Dict[str, SNOMED]):
    fullName = {}
    preferredName = {}
    for code, snomed in loincTable.items():
        if snomed.fullName in fullName:
            raise RuntimeError("SNOMED full name %s appears to be listed twice." %snomed.fullName)
        fullName[snomed.fullName] = code
        if snomed.preferredName in preferredName:
            raise RuntimeError("SNOMED preferred name %s appears to be listed twice." %snomed.preferredName)
        preferredName[snomed.preferredName] = code
    return fullName, preferredName


def main():
    data = loadRawDataTable()
    snomedTable = makeSnomedTable(data)
    fullName, preferredName = makeLookupTables(snomedTable)
    lookupTable = {
        "full name": fullName,
        "preferred name": preferredName
    }
    return snomedTable, lookupTable


snomedTable, lookupTable = main()
snomedTable[""] = EmptySNOMED()


def printSnomedTable():
    for code, snomed in snomedTable.items():
        if code == "":
            continue
        print(snomed)

if __name__ == "__main__":
    printSnomedTable()


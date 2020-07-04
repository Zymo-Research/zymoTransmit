import os
import typing


class LOINC(object):

    def __init__(self, code:str, commonName:str, component:str, property:str, time:str, system:str, scale:str, method:str):
        self.code = code
        self.commonName = commonName
        self.component = component
        self.property = property
        self.time = time
        self.system = system
        self.scale = scale
        self.method = method

    def __str__(self):
        outputLines = []
        outputLines.append(self.code)
        outputLines.append("\t" + self.commonName)
        outputLines.append("\t" + "\t".join([self.component, self.property, self.method]))
        outputLines.append("\t" + "\t".join([self.time, self.system, self.scale]))
        return "\n".join(outputLines)


class EmptyLOINC(object):

    def __init__(self):
        self.code = ""
        self.commonName = ""
        self.component = ""
        self.property = ""
        self.time = ""
        self.system = ""
        self.scale = ""
        self.method = ""

    def __str__(self):
        return "Empty LOINC code"


def loadRawDataTable():
    inputFileDirectory = os.path.split(__file__)[0]
    inputFileDirectory = os.path.split(inputFileDirectory)[0]
    inputFileDirectory = os.path.split(inputFileDirectory)[0]
    inputFile = "loincCodes.txt"
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


def makeLoincTable(data:list):
    loincTable = {}
    for line in data:
        code, commonName, component, property, time, system, scale, method = line
        loincTable[code] = LOINC(code, commonName, component, property, time, system, scale, method)
    return loincTable


def makeLookupTables(loincTable:typing.Dict[str, LOINC]):
    commonName = {}
    component = {}
    property = {}
    method = {}
    for code, loinc in loincTable.items():
        if loinc.commonName in commonName:
            raise RuntimeError("LOINC common name %s appears to be listed twice." %loinc.commonName)
        commonName[loinc.commonName] = code
        if not loinc.component in component:
            component[loinc.component] = []
        component[loinc.component].append(code)
        if not loinc.property in property:
            property[loinc.property] = []
        property[loinc.property].append(code)
        if not loinc.method in method:
            method[loinc.method] = []
        method[loinc.method].append(code)
    return commonName, component, property, method


def main():
    data = loadRawDataTable()
    loincTable = makeLoincTable(data)
    commonName, component, property, method = makeLookupTables(loincTable)
    lookupTable = {
        "common name": commonName,
        "component": component,
        "property": property,
        "method": method
    }
    return loincTable, lookupTable


loincTable, lookupTable = main()
loincTable[""] = EmptyLOINC()

def printLoincTable():
    for code, loinc in loincTable.items():
        if code == "":
            continue
        print(loinc)

if __name__ == "__main__":
    printLoincTable()
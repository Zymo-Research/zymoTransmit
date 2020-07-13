import os
import typing


class RaceEthnicity(object):

    def __init__(self, code:str, preferredName:str, aliases:typing.List[str]):
        self.code = code
        self.preferredName = preferredName
        self.aliases = aliases

    def __str__(self):
        outputLines = []
        aliasLine = " | ".join(self.aliases)
        outputLines.append(self.code)
        outputLines.append("\t" + aliasLine)
        return "\n".join(outputLines)


def loadRawDataTable():
    inputFileDirectory = os.path.split(os.path.abspath(__file__))[0]
    inputFileDirectory = os.path.split(inputFileDirectory)[0]
    inputFileDirectory = os.path.split(inputFileDirectory)[0]
    inputFile = "raceEthnicityCodes.txt"
    inputPath = os.path.join(inputFileDirectory, inputFile)
    data = open(inputPath, 'r').readlines()
    data = [line.strip() for line in data if line and not line.startswith("#")]
    data = [line.split("\t") for line in data if line]
    dataTable = []
    for line in data:
        line = [element.strip() for element in line]
        dataTable.append(line)
    return dataTable


def makeRaceEthnicityTable(data:list):
    raceEthnicityTable = {}
    for line in data:
        code = line[0]
        aliasList = line[1:]
        aliasList = [alias.upper() for alias in aliasList]
        preferredName = aliasList[0]
        raceEthnicityTable[code] = RaceEthnicity(code, preferredName, aliasList)
    return raceEthnicityTable


def makeAliasTable(raceEthnicityTable:typing.Dict[str, RaceEthnicity]):
    aliasTable = {}
    for code, raceEthnicity in raceEthnicityTable.items():
        aliasTable[code] = code
        for alias in raceEthnicity.aliases:
            aliasTable[alias] = code
    aliasTable[""] = aliasTable["UNKNOWN"]
    return aliasTable


def main():
    data = loadRawDataTable()
    raceEthnicityTable = makeRaceEthnicityTable(data)
    aliasTable = makeAliasTable(raceEthnicityTable)
    return raceEthnicityTable, aliasTable


raceEthnicityTable, aliasTable = main()


def printRaceEthnicityTable():
    for code, raceEthnicity in raceEthnicityTable.items():
        print(raceEthnicity)


if __name__ == "__main__":
    printRaceEthnicityTable()
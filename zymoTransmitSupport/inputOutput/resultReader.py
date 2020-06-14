import os
import datetime


class TestResult(object):
    expectedElements = 24

    def __init__(self, rawLine:str, delimiter:str = "\t"):
        self.rawLine = rawLine
        self.elementArray = self.processRawLine(delimiter)
        (self.patientID,
         self.patientLastName,
         self.patientFirstName,
         self.patientMiddleName,
         patientDateOfBirth,
         self.patientSex,
         self.patientStreetAddress,
         self.patientCity,
         self.patientState,
         self.patientZip,
         self.patientPhone,
         self.providerLastName,
         self.providerFirstName,
         self.providerMiddleName,
         self.providerPhone,
         self.specimenID,
         collectionDate,
         receivedDate,
         self.specimenSNOMED,
         self.testLOINC,
         analysisDate,
         self.resultString,
         reportedDate,
         self.note
         ) = self.elementArray
        self.patientDateOfBirth = self.processDate(patientDateOfBirth)
        self.collectionDate = self.processDate(collectionDate)
        self.receivedDate = self.processDate(receivedDate)
        self.analysisDate = self.processDate(analysisDate)
        self.reportedDate = self.processDate(reportedDate)

    def processRawLine(self, delimiter):
        rawLine = self.rawLine.strip()
        rawLine = rawLine.split(delimiter)
        rawLine = [element.strip() for element in rawLine]
        rawLine = [element.strip('"') for element in rawLine]
        if len(rawLine) < self.expectedElements:
            for i in range(self.expectedElements - len(rawLine)):
                rawLine.append("")
        if not len(rawLine) == self.expectedElements:
            errorMessageLines = []
            errorMessageLines.append("Got a line with an unexpected number of elements")
            errorMessageLines.append("Expecting %s elements, but only got %s." %(self.expectedElements, len(rawLine)))
            errorMessageLines.append("Elements: %s" %rawLine)
            raise ValueError("\n".join(errorMessageLines))
        return rawLine

    def processDate(self, dateString:str, possibleDelimiters = "/-. "):
        if not dateString.strip():
            return datetime.date(1, 1, 1)
        delimiter = None
        for possibleDelimiter in possibleDelimiters:
            if possibleDelimiter in dateString:
                delimiter = possibleDelimiter
                break
        if not delimiter:
            if len(dateString) == 8:
                month = dateString[:2]
                day = dateString[2:4]
                year = dateString[4:]
            else:
                errorMessageLines = []
                errorMessageLines.append("Unable to process date value")
                errorMessageLines.append("Attempting to process '%s' as a date failed." %dateString)
                errorMessageLines.append("Elements: %s" % self.elementArray)
                raise ValueError("\n".join(errorMessageLines))
        else:
            dateSplit = dateString.split(delimiter)
            if not len(dateSplit) == 3:
                errorMessageLines = []
                errorMessageLines.append("Unable to process date value")
                errorMessageLines.append("Attempting to process '%s' as a date with delimiter '%s' failed." %(dateString, delimiter))
                errorMessageLines.append("Elements: %s" % self.elementArray)
                raise ValueError("\n".join(errorMessageLines))
            month, day, year = dateSplit
        return datetime.date(int(year), int(month), int(day))

    def __str__(self):
        return ", ".join([str(item) for item in self.elementArray])


def loadRawDataTable(filePath:str):
    testResults = []
    if not os.path.isfile(filePath):
        raise FileNotFoundError("Unable to find input file at %s" %filePath)
    resultsFile = open(filePath, 'r')
    line = resultsFile.readline()
    while line:
        line = line.strip()
        if not line or line.startswith("#"):
            line = resultsFile.readline()
            continue
        testResults.append(TestResult(line))
        line = resultsFile.readline()
    resultsFile.close()
    return testResults

import collections
from . import resultReader

class CALabTestResult(object):
    expectedElements = 43

    def __init__(self, rawLine: [str, collections.Iterable], delimiter: str = "\t"):
        self.rawLine = rawLine
        if type(self.rawLine) == str:
            self.elementArray = self.processRawLine(delimiter)
        elif isinstance(rawLine, collections.Iterable):
            self.elementArray = self.processList(self.rawLine)
        (
             self.facilityName,
             self.facilityCLIA,
             self.facilityStreet,
             self.facilityCity,
             self.facilityState,
             self.facilityZip,
             self.facilityPhone,
             self.patientID,
             self.patientFirstName,
             self.patientMiddleName,
             self.patientLastName,
             self.patientDateOfBirth,
             self.patientSex,
             self.race,
             self.ethnicity,
             self.language,
             self.patientStreetAddress,
             self.patientCity,
             self.patientState,
             self.patientZip,
             self.patientCounty,
             self.patientPhone,
             self.okToContact,
             self.providerFirstName,
             self.providerLastName,
             self.providerNPI,
             self.providerStreet,
             self.providerZip,
             self.providerPhone,
             self.specimenID,
             self.collectionDate,
             self.testOrderedDate,
             self.analysisDate,
             self.reportedDate,
             self.specimenSNOMED,
             self.specimenSite,
             self.testName,
             self.resultString,
             self.accession,
             self.testLOINC,
             self.resultCode,
             self.deviceIdentifier,
             self.note
         ) = self.elementArray


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
            errorMessageLines.append("Expecting %s elements, but got %s." % (self.expectedElements, len(rawLine)))
            errorMessageLines.append("Elements: %s" % rawLine)
            raise ValueError("\n".join(errorMessageLines))
        return rawLine

    def processList(self, rawLine):
        processedList = []
        for element in rawLine:
            processedList.append(element.strip().strip('"'))
        if len(processedList) < self.expectedElements:
            for i in range(self.expectedElements - len(processedList)):
                processedList.append("")
        if not len(processedList) == self.expectedElements:
            errorMessageLines = []
            errorMessageLines.append("Got a line with an unexpected number of elements")
            errorMessageLines.append("Expecting %s elements, but only got %s." % (self.expectedElements, len(processedList)))
            errorMessageLines.append("Elements: %s" % processedList)
            raise ValueError("\n".join(errorMessageLines))
        return processedList

    def convertToStandardResultObject(self):
        resultArray = [
             self.patientID,
             self.patientLastName,
             self.patientFirstName,
             self.patientMiddleName,
             self.patientDateOfBirth,
             self.patientSex,
             self.patientStreetAddress,
             self.patientCity,
             self.patientState,
             self.patientZip,
             self.patientPhone,
             self.providerLastName,
             self.providerFirstName,
             "",
             self.providerStreet,
             "",
             "",
             self.providerZip,
             self.providerPhone,
             self.specimenID,
             self.collectionDate,
             "",
             "",
             "",
             self.specimenSNOMED,
             self.testLOINC,
             self.analysisDate,
             "",
             self.resultString,
             self.reportedDate,
             "",
             self.note,
             self.race,
             self.ethnicity,
             self.accession,
             self.testOrderedDate,
             "",
             "",
             self.deviceIdentifier,
             "",
            self.providerNPI
        ]
        resultObject = resultReader.TestResult(resultArray)
        auxiliaryData = {
            "labName": self.facilityName,
            "labCLIA": self.facilityCLIA,
            "labStreet": self.facilityStreet,
            "labCity": self.facilityCity,
            "labState": self.facilityState,
            "labZip": self.facilityZip,
            "labPhone": self.facilityPhone,
            "okToContact": self.okToContact
        }
        resultObject.auxiliaryData = auxiliaryData.copy()
        resultObject.rawLine = self.rawLine
        return resultObject

    def __str__(self):
        return ", ".join([str(item) for item in self.elementArray])
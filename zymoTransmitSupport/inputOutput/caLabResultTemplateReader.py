import os
import datetime
import re
import collections
from . import resultReader

class CATestResult(object):
    expectedElements = 40

    def __init__(self, rawLine: [str, collections.Iterable], delimiter: str = "\t"):
        self.rawLine = rawLine
        if type(self.rawLine) == str:
            self.elementArray = self.processRawLine(delimiter)
        elif isinstance(rawLine, collections.Iterable):
            self.elementArray = self.processList(self.rawLine)
        (self.sendingApplication,
         self.facilityName,
         self.facilityCLIA,
         self.facilityStreet,
         self.facilityCity,
         self.facilityState,
         self.facilityZip,
         self.facilityPhone,
         self.patientID,
         self.patientFirstName,
         self.patientLastName,
         patientDateOfBirth,
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
         collectionDate,
         testOrderDate,
         analyzedDate,
         reportedDate,
         self.specimenType,
         self.specimenSite,
         self.testName,
         self.resultString,
         self.accession,
         self.testCode,
         self.resultCode,
         self.deviceIdentifier
         ) = self.elementArray
        self.patientDateOfBirth = self.processDateAndTime(patientDateOfBirth, "")
        self.collectionDateTime = self.processDateAndTime(collectionDate, "")
        self.reportedDateTime = self.processDateAndTime(reportedDateAndTime, "")
        self.patientDateOfBirth, patientTimeOfBirth = self.revertDateTimeObject(self.patientDateOfBirth)
        self.collectionDate, self.collectionTime = self.revertDateTimeObject(self.collectionDateTime)
        self.reportedDate, self.reportedTime = self.revertDateTimeObject(self.reportedDateTime)
        self.testLOINC = self.findTestLoinc()
        self.specimenSNOMED = self.determineSampleType()


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
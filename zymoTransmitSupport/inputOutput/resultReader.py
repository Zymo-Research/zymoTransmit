import os
import datetime
import re
import zipcodes
import collections
import csv
import typing
from . import caResultReader


class TestResult(object):
    expectedElements = 40

    def __init__(self, rawLine: [str, collections.Iterable], delimiter: str = "\t"):
        self.okToTransmit = True
        self.reasonForFailedTransmission = []
        self.transmittedSuccessfully = None
        self.rawLine = rawLine
        if type(self.rawLine) == str:
            self.rawLine = self.rawLine.strip()
            self.elementArray = self.processRawLine(delimiter)
        elif isinstance(rawLine, collections.Iterable):
            self.elementArray = self.processList(self.rawLine)
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
         self.providerStreet,
         self.providerCity,
         self.providerState,
         self.providerZip,
         self.providerPhone,
         self.specimenID,
         collectionDate,
         collectionTime,
         receivedDate,
         receivedTime,
         self.specimenSNOMED,
         self.testLOINC,
         analysisDate,
         analysisTime,
         self.resultString,
         reportedDate,
         reportedTime,
         self.note,
         self.race,
         self.ethnicity,
         self.accession,
         testOrderedDate,
         testOrderedTime,
         self.equipmentCode,
         self.equipmentDescription,
         self.equipmentID
         ) = self.elementArray
        if not (self.specimenID or self.accession):
            raise ValueError("All samples must have either specimen ID or accession number")
        if not self.accession:
            self.accession = self.specimenID
        if not self.specimenID:
            self.specimenID = self.accession
        if not self.patientID:
            self.patientID = self.accession
        if self.equipmentDescription and not self.equipmentID:
            raise ValueError("If test equipment description is present, test equipment code must also be present.")
        self.patientDateOfBirth = self.processDateAndTime(patientDateOfBirth, "")
        self.collectionDateTime = self.processDateAndTime(collectionDate, collectionTime)
        self.receivedDateTime = self.processDateAndTime(receivedDate, receivedTime)
        self.analysisDateTime = self.processDateAndTime(analysisDate, analysisTime)
        self.reportedDateTime = self.processDateAndTime(reportedDate, reportedTime)
        self.testOrderedDateTime = self.processDateAndTime(testOrderedDate, testOrderedTime)
        self.auxiliaryData = {}

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
            # raise ValueError("\n".join(errorMessageLines))
            print("\n".join(errorMessageLines))
            self.okToTransmit = False
            self.reasonForFailedTransmission.append("Line has too many elements")
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
            # raise ValueError("\n".join(errorMessageLines))
            print("\n".join(errorMessageLines))
            self.okToTransmit = False
            self.reasonForFailedTransmission.append("Line has too many elements")
        return processedList

    def processDateAndTime(self, dateString: str, timeString: str, possibleDateDelimiters="/-. ",
                           possibleTimeDelimiters=":"):
        if not dateString.strip():
            return datetime.datetime(1, 1, 1, 0, 0, 0)
        if not timeString:
            timeString = "00:00"
        dateDelimiter = None
        for possibleDelimiter in possibleDateDelimiters:
            if possibleDelimiter in dateString:
                dateDelimiter = possibleDelimiter
                break
        if not dateDelimiter:
            if len(dateString) == 8:
                year = dateString[:4]
                month = dateString[4:6]
                day = dateString[6:]
            else:
                errorMessageLines = []
                errorMessageLines.append("Unable to process date value")
                errorMessageLines.append("Attempting to process '%s' as a date failed." % dateString)
                errorMessageLines.append("Elements: %s" % self.elementArray)
                # raise ValueError("\n".join(errorMessageLines))
                print("\n".join(errorMessageLines))
                self.okToTransmit = False
                self.reasonForFailedTransmission.append("Unable to process %s as date" %dateString)
                return datetime.datetime(1, 1, 1, 0, 0, 0)
        else:
            dateSplit = dateString.split(dateDelimiter)
            if not len(dateSplit) == 3:
                errorMessageLines = []
                errorMessageLines.append("Unable to process date value")
                errorMessageLines.append(
                    "Attempting to process '%s' as a date with delimiter '%s' failed." % (dateString, dateDelimiter))
                errorMessageLines.append("Elements: %s" % self.elementArray)
                # raise ValueError("\n".join(errorMessageLines))
                print("\n".join(errorMessageLines))
                self.okToTransmit = False
                self.reasonForFailedTransmission.append("Attempting to process '%s' as a date with delimiter '%s' failed." % (dateString, dateDelimiter))
                return datetime.datetime(1, 1, 1, 0, 0, 0)
            month, day, year = dateSplit
        timeDelimiter = None
        for possibleDelimiter in possibleTimeDelimiters:
            if possibleDelimiter in timeString:
                timeDelimiter = possibleDelimiter
                break
        if not timeDelimiter:
            if len(timeString) <= 4:
                timeString = timeString.zfill(4)
                timeString = timeString + "00"
            elif len(timeString) in [5, 6]:
                timeString = timeString.zfill(6)
            else:
                errorMessageLines = []
                errorMessageLines.append("Unable to process time value")
                errorMessageLines.append(
                    "Attempting to process '%s' as a time with no delimiter failed." % timeString)
                # raise ValueError("\n".join(errorMessageLines))
                print("\n".join(errorMessageLines))
                self.okToTransmit = False
                self.reasonForFailedTransmission.append("Attempting to process '%s' as a time with no delimiter failed." % timeString)
                return datetime.datetime(1, 1, 1, 0, 0, 0)
            hour = int(timeString[:2])
            minute = int(timeString[2:4])
            second = int(timeString[4:])
        else:
            timeSplit = timeString.split(timeDelimiter)
            if len(timeSplit) in [2, 3]:
                hour = int(timeSplit[0])
                minute = int(timeSplit[1])
                if len(timeSplit) == 3:
                    second = int(timeSplit[2])
                else:
                    second = 0
            else:
                errorMessageLines = []
                errorMessageLines.append("Unable to process time value")
                errorMessageLines.append(
                    "Attempting to process '%s' as a time with delimiter '%s' failed." % (timeString, timeDelimiter))
                errorMessageLines.append("Elements: %s" % self.elementArray)
                # raise ValueError("\n".join(errorMessageLines))
                print("\n".join(errorMessageLines))
                self.okToTransmit = False
                self.reasonForFailedTransmission.append("Attempting to process '%s' as a time with delimiter '%s' failed." % (timeString, timeDelimiter))
                return datetime.datetime(1, 1, 1, 0, 0, 0)
            hourCheck = hour in range(24)
            minuteCheck = minute in range(60)
            secondCheck = second in range(60)
            if not hourCheck and minuteCheck and secondCheck:
                errorMessageLines = []
                errorMessageLines.append("Unable to process time value")
                errorMessageLines.append(
                    "Attempting to process '%s' as a time with delimiter '%s' returned a value out of range (hour not between 0 and 23 or second not between 0 and 59)." % (
                    timeString, timeDelimiter))
                errorMessageLines.append("Elements: %s" % self.elementArray)
                # raise ValueError("\n".join(errorMessageLines))
                print("\n".join(errorMessageLines))
                self.okToTransmit = False
                self.reasonForFailedTransmission.append("Attempting to process '%s' as a time with delimiter '%s' returned a value out of range (hour not between 0 and 23 or second not between 0 and 59)." % (
                    timeString, timeDelimiter))
                return datetime.datetime(1, 1, 1, 0, 0, 0)
        try:
            dateTimeObject = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
        except ValueError as err:
            dateTimeObject = (dateString, timeString, str(err))
        return dateTimeObject

    def getInvalidZips(self):
        zipCodeFields = [self.patientZip, self.providerZip]
        invalidZips = []
        for zip in zipCodeFields:
            if not zip:
                continue
            if not (re.match("^\d{5}$", zip) or re.match("^\d{5}-\d{4}$", zip)):
                issue = (zip, "Invalid zip format")
                invalidZips.append(issue)
            elif not zipcodes.matching(zip):
                issue = (zip, "Zip appears not to exist")
                invalidZips.append(issue)
        return invalidZips

    def getInvalidDateTimes(self):
        invalidMessages = []
        dateTimeAttributes = [
            "patientDateOfBirth",
            "collectionDateTime",
            "receivedDateTime",
            "analysisDateTime",
            "reportedDateTime"
        ]
        for field in dateTimeAttributes:
            value = getattr(self, field)
            if not value:
                continue
            if type(value) == datetime.datetime:
                continue
            errorMessage = "Date and time %s %s generated an error: %s" % (value[0], value[1], value[2])
            invalidMessages.append(errorMessage)
            setattr(self, field, datetime.datetime(1, 1, 1, 0, 0, 0))
        return invalidMessages

    def __str__(self):
        return ", ".join([str(item) for item in self.elementArray])


def yesAnswer(question: str):
    answerTable = {
        "YES": True,
        "Y": True,
        "NO": False,
        "N": False
                   }
    validAnswer = False
    answer = ""
    while not validAnswer:
        answer = input(question)
        answer = answer.upper()
        if answer not in answerTable:
            print("Invalid answer. Please answer yes or no.")
            validAnswer = False
            continue
        return answerTable[answer]


def confirmProceedWithInvalidZipsOrDateTimes(invalidZipWarnings:list, invalidDateTimeWarnings:list):
    if invalidZipWarnings:
        print("Invalid zipcodes were found. Please fix if possible. Invalid zip(s):")
        for invalidZipWarning in invalidZipWarnings:
            print(invalidZipWarning)
    if invalidDateTimeWarnings:
        print("Invalid dates and/or times were found. Please fix if possible. Invalid dates/times:")
        for invalidDateTimeWarning in invalidDateTimeWarnings:
            print(invalidDateTimeWarning)
    proceedAnyway = yesAnswer("Do you wish to proceed anyway?")
    print()
    if not proceedAnyway:
        quit("Please correct issues and resume")
    else:
        return True


def loadTextDataTable(filePath: str):
    testResults = []
    if not os.path.isfile(filePath):
        raise FileNotFoundError("Unable to find input file at %s" % filePath)
    resultsFile = open(filePath, 'r')
    currentLine = 0
    line = resultsFile.readline()
    currentLine += 1
    while line:
        line = line.strip()
        if not line or line.startswith("#"):
            line = resultsFile.readline()
            currentLine += 1
            continue
        testResults.append((currentLine, TestResult(line)))
        line = resultsFile.readline()
        currentLine += 1
    resultsFile.close()
    cleanedResults = validateResultTable(testResults)
    return cleanedResults


def loadCSVDataTable(filePath: str, cdphCSV:bool=False):
    testResults = []
    if not os.path.isfile(filePath):
        raise FileNotFoundError("Unable to find input file at %s" % filePath)
    probeFile = open(filePath, 'rb')
    probeBytes = probeFile.read(3)
    probeFile.close()
    if probeBytes == b'\xef\xbb\xbf':
        resultsFile = open(filePath, 'r', encoding='utf-8-sig')
        utf8 = True
        print("WARNING: This CSV appears to use UTF-8 encoding. This may cause errors. Please use plain ASCII (standard) CSV format in the future.")
    else:
        resultsFile = open(filePath, 'r')
        utf8 = False
    csvHandle = csv.reader(resultsFile)
    currentLine = 0
    if cdphCSV:
        header = next(csvHandle)
        currentLine += 1
    line = next(csvHandle)
    currentLine += 1
    while line:
        if not line or line[0].startswith("#"):
            try:
                line = next(csvHandle)
            except StopIteration:
                line = []
            currentLine += 1
            continue
        if cdphCSV:
            caTestResult = caResultReader.CATestResult(line)
            testResultObject = caTestResult.convertToStandardResultObject()
        else:
            testResultObject = TestResult(line)
        testResults.append((currentLine, testResultObject))
        try:
            line = next(csvHandle)
        except StopIteration:
            line = []
        currentLine += 1
    resultsFile.close()
    cleanedResults = validateResultTable(testResults)
    return cleanedResults


def validateResultTable(rawResultTable: typing.List[typing.Tuple[int, TestResult]]):
    cleanedResults = []
    invalidZipWarnings = []
    invalidDateTimeWarnings = []
    for currentLine, result in rawResultTable:
        invalidZips = result.getInvalidZips()
        invalidDateTimes = result.getInvalidDateTimes()
        if invalidZips or invalidDateTimes:
            for invalidZip in invalidZips:
                errorLine = "Line %s: Zip: %s - %s" % (currentLine, invalidZip[0], invalidZip[1])
                invalidZipWarnings.append(errorLine)
            for invalidDateTime in invalidDateTimes:
                errorLine = "Line %s: %s" % (currentLine, invalidDateTime)
                invalidDateTimeWarnings.append(errorLine)
        cleanedResults.append(result)
    if invalidZipWarnings or invalidDateTimeWarnings:
        confirmProceedWithInvalidZipsOrDateTimes(invalidZipWarnings, invalidDateTimeWarnings)
    return cleanedResults


def loadRawDataTable(filePath: str, cdphCSV:bool=False):
    if filePath.lower().endswith(".csv"):
        return loadCSVDataTable(filePath, cdphCSV)
    else:
        return loadTextDataTable(filePath)

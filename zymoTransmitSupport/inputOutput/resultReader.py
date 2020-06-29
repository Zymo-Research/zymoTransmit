import os
import datetime
import re
import zipcodes


class TestResult(object):
    expectedElements = 32

    def __init__(self, rawLine: str, delimiter: str = "\t"):
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
         self.note
         ) = self.elementArray
        self.patientDateOfBirth = self.processDateAndTime(patientDateOfBirth, "")
        self.collectionDateTime = self.processDateAndTime(collectionDate, collectionTime)
        self.receivedDateTime = self.processDateAndTime(receivedDate, receivedTime)
        self.analysisDateTime = self.processDateAndTime(analysisDate, analysisTime)
        self.reportedDateTime = self.processDateAndTime(reportedDate, reportedTime)

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
            errorMessageLines.append("Expecting %s elements, but only got %s." % (self.expectedElements, len(rawLine)))
            errorMessageLines.append("Elements: %s" % rawLine)
            raise ValueError("\n".join(errorMessageLines))
        return rawLine

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
                month = dateString[:2]
                day = dateString[2:4]
                year = dateString[4:]
            else:
                errorMessageLines = []
                errorMessageLines.append("Unable to process date value")
                errorMessageLines.append("Attempting to process '%s' as a date failed." % dateString)
                errorMessageLines.append("Elements: %s" % self.elementArray)
                raise ValueError("\n".join(errorMessageLines))
        else:
            dateSplit = dateString.split(dateDelimiter)
            if not len(dateSplit) == 3:
                errorMessageLines = []
                errorMessageLines.append("Unable to process date value")
                errorMessageLines.append(
                    "Attempting to process '%s' as a date with delimiter '%s' failed." % (dateString, dateDelimiter))
                errorMessageLines.append("Elements: %s" % self.elementArray)
                raise ValueError("\n".join(errorMessageLines))
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
                raise ValueError("\n".join(errorMessageLines))
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
                raise ValueError("\n".join(errorMessageLines))
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
                raise ValueError("\n".join(errorMessageLines))
        return datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

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


def confirmProceedWithInvalidZips(invalidZipWarnings:list):
    print("Invalid zipcodes were found. Please fix if possible. Invalid zip(s):")
    for invalidZipWarning in invalidZipWarnings:
        print(invalidZipWarning)
    proceedAnyway = yesAnswer("Do you wish to proceed anyway?")
    if not proceedAnyway:
        print()
        quit("Please correct zipcode issues and resume")
    else:
        return True


def loadRawDataTable(filePath: str):
    testResults = []
    invalidZipWarnings = []
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
        result = TestResult(line)
        invalidZips = result.getInvalidZips()
        if invalidZips:
            for invalidZip in invalidZips:
                errorLine = "Line %s: Zip: %s - %s" % (currentLine, invalidZip[0], invalidZip[1])
                invalidZipWarnings.append(errorLine)
        testResults.append(result)
        line = resultsFile.readline()
        currentLine += 1
    resultsFile.close()
    if invalidZipWarnings:
        confirmProceedWithInvalidZips(invalidZipWarnings)
    return testResults

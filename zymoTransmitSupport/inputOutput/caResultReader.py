import os
import datetime
import re
import zipcodes
import collections
import csv
import typing
from . import resultReader

loincRegex = re.compile(r"^\d{5}-\d$")

def makeSpecimenRegexes():
    nasalTerms = ["NASO", "NOSE", "NASAL", "NPNX", r"\WNP\W", r"^NP\W", r"\WNP$", r"^NP$"]
    oralTerms = ["THROAT", "OROPHARYN", r"\WOP\W", r"^OP\W", r"\WOP$", r"^OP$"]
    bloodTerms = ["BLOOD", "SERUM", "PLASMA"]
    nasalRegexList = [re.compile(term, re.IGNORECASE) for term in nasalTerms]
    oralRegexList = [re.compile(term, re.IGNORECASE) for term in oralTerms]
    bloodRegexList = [re.compile(term, re.IGNORECASE) for term in bloodTerms]
    return nasalRegexList, oralRegexList, bloodRegexList

nasalRegexList, oralRegexList, bloodRegexList = makeSpecimenRegexes()
swabRegex = re.compile("SWAB", re.IGNORECASE)


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
         reportedDateAndTime,
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
         self.patientCountry,
         self.patientPhone,
         self.okToContact,
         self.insurance,
         self.expedited,
         self.providerFirstName,
         self.providerLastName,
         self.providerPhone,
         self.specimenID,
         collectionDate,
         self.specimenType,
         self.specimenSite,
         self.testName,
         self.resultString,
         self.note,
         self.accession,
         self.testCode,
         self.resultCode,
         self.unused
         ) = self.elementArray
        if not self.specimenID:
            self.specimenID = self.accession
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
            errorMessageLines.append("Expecting %s elements, but only got %s." % (self.expectedElements, len(rawLine)))
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

    def processDateAndTime(self, dateString: str, timeString: str, possibleDateDelimiters="/-. ",
                           possibleTimeDelimiters=":"):
        if not dateString.strip():
            return datetime.datetime(1, 1, 1, 0, 0, 0)
        if not timeString:
            timeString = "00:00"
        tzInfo = None
        dateDelimiter = None
        for possibleDelimiter in possibleDateDelimiters:
            if possibleDelimiter in dateString:
                if possibleDelimiter == "-":
                    if dateString.count(possibleDelimiter) == 1:
                        continue
                dateDelimiter = possibleDelimiter
                break
        if not dateDelimiter:
            if len(dateString) == 8:
                month = dateString[:4]
                day = dateString[4:6]
                year = dateString[6:]
            elif len(dateString) == 14:
                month = dateString[:4]
                day = dateString[4:6]
                year = dateString[6:8]
                hour = dateString[8:10]
                minute = dateString[10:12]
                second = dateString[12:14]
                timeString = ":".join([hour, minute, second])
            elif len(dateString) == 19 and "-" in dateString:
                month = dateString[:4]
                day = dateString[4:6]
                year = dateString[6:8]
                hour = dateString[8:10]
                minute = dateString[10:12]
                second = dateString[12:14]
                timeString = ":".join([hour, minute, second])
                offset = timeString.split("-")[1]
                offset = offset[:2]
                offset = int(offset)
                tzInfo = datetime.timedelta(hours=offset)
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
        try:
            dateTimeObject = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=tzInfo)
        except ValueError as err:
            dateTimeObject = (dateString, timeString, str(err))
        return dateTimeObject


    def revertDateTimeObject(self, revertant:[datetime.datetime, datetime.date, datetime.time]):
        if not revertant:
            return ("", "")
        if type(revertant) == datetime.datetime:
            dateString = "%s/%s/%s" %(revertant.month, revertant.day, revertant.year)
            timeString = "%s:%s:%s" %(revertant.hour, revertant.minute, revertant.second)
        elif type(revertant) == datetime.date:
            dateString = "%s/%s/%s" %(revertant.month, revertant.day, revertant.year)
            timeString = ""
        elif type(revertant) == datetime.time:
            dateString = ""
            timeString = "%s:%s:%s" %(revertant.hour, revertant.minute, revertant.second)
        else:
            raise ValueError("Got an invalid value trying to revert a datetime object to a string: %s of type %s" %(revertant, type(revertant)))
        return (dateString, timeString)


    def findTestLoinc(self):
        if loincRegex.match(self.testCode):
            return self.testCode
        if loincRegex.match(self.testName):
            return self.testName
        else:
            return ""


    def determineSampleType(self):
        def checkFields(regexList:list):
            for field in fields:
                for regex in regexList:
                    if regex.search(field):
                        return True
            return False
        nasopharyngealSwabSNOMED = "258500001"
        throatSwabSNOMED = "258529004"
        bloodSNOMED = "788707000"
        swabNotOtherwiseSpecifiedSNOMED = "257261003"
        fields = [self.specimenType, self.specimenSite]
        nasal = checkFields(nasalRegexList)
        swab = checkFields([swabRegex])
        oral = checkFields(oralRegexList)
        blood = checkFields(bloodRegexList)
        if swab:
            if nasal and oral:
                return swabNotOtherwiseSpecifiedSNOMED
            elif nasal:
                return nasopharyngealSwabSNOMED
            elif oral:
                return throatSwabSNOMED
            else:
                return swabNotOtherwiseSpecifiedSNOMED
        elif blood:
            return bloodSNOMED
        else:
            return ""


    def convertToStandardResultObject(self):
        resultArray = [
             self.patientID,
             self.patientLastName,
             self.patientFirstName,
             "",
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
             "",
             "",
             "",
             "",
             self.providerPhone,
             self.specimenID,
             self.collectionDate,
             self.collectionTime,
             "",
             "",
             self.specimenSNOMED,
             self.testLOINC,
             "",
             "",
             self.resultString,
             self.reportedDate,
             self.reportedTime,
             self.note,
             self.race,
             self.ethnicity
        ]
        resultObject = resultReader.TestResult(resultArray)
        auxiliaryData = {
            NEED VALUES HERE
        }
        resultObject.auxiliaryData = auxiliaryData.copy()





    def __str__(self):
        return ", ".join([str(item) for item in self.elementArray])


def loadCSVDataTable(filePath: str):
    testResults = []
    if not os.path.isfile(filePath):
        raise FileNotFoundError("Unable to find input file at %s" % filePath)
    probeFile = open(filePath, 'rb')
    probeBytes = probeFile.read(3)
    probeFile.close()
    if probeBytes == b'\xef\xbb\xbf':
        resultsFile = open(filePath, 'r', encoding='utf-8-sig')
        utf8 = True
        #print("WARNING: This CSV appears to use UTF-8 encoding. This may cause errors. Please use plain ASCII (standard) CSV format in the future.") #This is probably unnecessary, although it does open the way for people to potentially use weird characters
    else:
        resultsFile = open(filePath, 'r')
        utf8 = False
    csvHandle = csv.reader(resultsFile)
    currentLine = 0
    line = next(csvHandle)
    currentLine += 1
    if line[0].strip() == "Sending Application":
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
        testResults.append((currentLine, TestResult(line)))
        try:
            line = next(csvHandle)
        except StopIteration:
            line = []
        currentLine += 1
    resultsFile.close()
    cleanedResults = validateResultTable(testResults)
    return cleanedResults

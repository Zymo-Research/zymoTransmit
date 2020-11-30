import datetime
import re
import json
import os
import zipcodes
import time
from .. import config

def loadFIPSData():
    thisFileDirectory = os.path.split(os.path.abspath(__file__))[0]
    theDirectoryAbove = os.path.split(thisFileDirectory)[0]
    infoFile = os.path.join(theDirectoryAbove, "fipsCounties.json")
    inputFile = open(infoFile)
    data = json.load(inputFile)
    inputFile.close()
    return data


fipsData = loadFIPSData()


class Delimiters(object):
    line = "|"
    field = "^"
    subfield = "&"
    repeat = "~"


delimiterEscapes = {
    Delimiters.line : "\\F\\",
    Delimiters.field : "\\R\\",
    Delimiters.subfield : "\\T\\",
    Delimiters.repeat : "\\R\\"
}


class Hl7Field(object):

    delimiter = "^"

    def __init__(self):
        self.subfields = []

    def __str__(self):
        subfieldStrings = [str(item).replace(self.delimiter, delimiterEscapes[self.delimiter]).replace(Delimiters.repeat, delimiterEscapes[Delimiters.repeat]) for item in self.subfields]
        return self.delimiter.join(subfieldStrings)


class Hl7Subfield(Hl7Field):
    delimiter = "&"
    pass


class Hl7Line(object):
    expectEncodingField = None
    delimiter = "|"

    def __init__(self):
        self.fields = []

    def __str__(self):
        if self.expectEncodingField is None:
            fieldStrings = [str(item).replace(self.delimiter, delimiterEscapes[self.delimiter]).replace(Delimiters.repeat, delimiterEscapes[Delimiters.repeat]) for item in self.fields]
            return self.delimiter.join(fieldStrings)
        else:
            cleanedFields = []
            for field in self.fields:
                if field == self.expectEncodingField:
                    cleanedFields.append(str(field))
                else:
                    cleanedField = str(field)
                    cleanedField = cleanedField.replace(self.delimiter, delimiterEscapes[self.delimiter]).replace(Delimiters.repeat, delimiterEscapes[Delimiters.repeat])
                    cleanedFields.append(cleanedField)
            return self.delimiter.join(cleanedFields)


class SingleValueField(Hl7Field):

    lengthLimit = None
    default = ""

    def __init__(self, value:str=None):
        if value is None:
            if self.default is None:
                raise AttributeError("No default value set for this single value field object")
            self.value = self.default
        else:
            self.value = value
        if self.lengthLimit:
            self.subfields = [str(self.value)[:self.lengthLimit]]
        else:
            self.subfields = [self.value]


def makeCurrentTimeString(timezone:str = None):
    if not timezone:
        timezone = datetime.timezone.utc
    currentTime = datetime.datetime.now(timezone)
    return makeTimeString(currentTime)


def makeTimeString(datetimeObject:datetime.datetime):
    year = datetimeObject.year
    month = datetimeObject.month
    day = datetimeObject.day
    hour = datetimeObject.hour
    minute = datetimeObject.minute
    second = datetimeObject.second
    timeList = [year, month, day, hour, minute, second]
    timeList = [str(number).zfill(2) for number in timeList]
    return "".join(timeList)


class Date(Hl7Field):

    def __init__(self, year:int, month:int, day:int):
        if not (day and month and year):
            dateString = ""
        elif year == 1:
            dateString = "00000000"
        else:
            self.day = str(day).zfill(2)
            self.month = str(month).zfill(2)
            self.year = str(year).zfill(4)
            dateString = self.year + self.month + self.day
        self.subfields = [dateString]


class Time(Hl7Field):

    includeSeconds = None

    def __init__(self, hour:int, minute:int, second:int=0, gmtOffset:[str, int, tuple]=config.LabInfo.gmt_offset, includeSeconds:bool=True, includeOffset:bool=True):
        self.hour = str(hour).zfill(2)
        self.minute = str(minute).zfill(2)
        self.second = str(second).zfill(2)
        if not self.includeSeconds is None:
            includeSeconds = self.includeSeconds
        if includeSeconds:
            secondString = self.second
        else:
            secondString = ""
        if not includeOffset:
            offsetString = ""
        else:
            self.offSet = self.processOffset(gmtOffset)
            offsetString = "%s" %(self.offSet)
        timeString = self.hour + self.minute + secondString + "-" + offsetString
        self.subfields = [timeString]

    def processOffset(self, gmtOffset:[str, int, float, tuple]=0):
        if type(gmtOffset) == float:
            gmtOffset = int(gmtOffset)
        if type(gmtOffset) == str:
            if len(gmtOffset) == 0:
                return "0000"
            elif len(gmtOffset) == 1:
                return "0" + gmtOffset + "00"
            elif len(gmtOffset) == 2:
                return gmtOffset + "00"
            elif len(gmtOffset) == 3:
                return "0" + gmtOffset
            elif len(gmtOffset) == 4:
                return gmtOffset
            else:
                raise ValueError("Offset cannot be more than 4 characters")
        if type(gmtOffset) == int:
            if gmtOffset < 100:
                hours = str(gmtOffset).zfill(2)
                return hours + "00"
            elif gmtOffset < 1500:
                return str(gmtOffset).zfill(4)
            else:
                raise ValueError("Offset cannot be greater than 1500")
        else:
            if len(gmtOffset) == 0:
                return "0000"
            elif len(gmtOffset) == 1:
                return str(gmtOffset[0]).zfill(2) + "00"
            elif len(gmtOffset) == 2:
                hours, minutes = gmtOffset
                hours = str(hours).zfill(2)
                if minutes:
                    minutes = str(minutes).zfill(2)
                else:
                    minutes = "00"
                return hours + minutes
            else:
                raise ValueError("Offset cannot have more than two elements in the tuple")


class DateAndTime(Hl7Field):

    includeSeconds = None

    def __init__(self, year:int, month:int, day:int, hour:int=0, minute:int=0, second:int=0, gmtOffset:int=config.LabInfo.gmt_offset, includeSeconds:bool=False, includeOffset:bool=True):
        if not self.includeSeconds is None:
            includeSeconds = self.includeSeconds
        dateString = str(Date(year, month, day))
        timeString = str(Time(hour, minute, second, gmtOffset, includeSeconds, includeOffset))
        dateAndTimeString = dateString + timeString
        self.subfields = [dateAndTimeString]


usPhoneNumberRegex = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{4})\D*(\d*)$')  #compile at load to avoid repeated RE compile
emailValidationRegex = re.compile(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,24}$') #kids, don't try this @ home


class SubjectName(Hl7Field):

    def __init__(self,
                 family:str,
                 given:str,
                 middle:str="",
                 suffix:str="",
                 prefix:str="",
                 nameType:str="L",
                 professionalSuffix:str=""):
        self.family = family
        self.given = given
        self.middle = middle
        self.suffix = suffix
        self.prefix = prefix
        self.stateValueSet = ""
        self.nameType = nameType
        self.nameRepCode = ""
        self.nameContext = ""
        self.nameValidityRange = ""
        self.nameAssemblyOrder = ""
        self.effectiveDate = ""
        self.expirationDate = ""
        self.professionalSuffix = professionalSuffix
        self.subfields = [
            self.family[:50],
            self.given[:30],
            self.middle[:30],
            self.suffix[:30],
            self.prefix[:30],
            self.stateValueSet,
            self.nameType[:5],
            self.nameRepCode,
            self.nameContext,
            self.nameValidityRange,
            self.nameAssemblyOrder,
            self.effectiveDate,
            self.expirationDate,
            self.professionalSuffix[:50]
        ]


class Address(Hl7Field):

    defaultAddressType = "H"

    def __init__(self, streetAddress:str, city:str, state:str, zip:str, country:str="USA", addressType:str=None):
        self.streetAddress = streetAddress
        self.otherDesignation = ""
        self.city = city
        self.state = state
        self.zip = correctLostLeadingZeroZipcode(zip, state)
        self.country = country
        if not addressType is None:
            self.addressType = addressType
        else:
            self.addressType = self.defaultAddressType
        self.otherGeoDesignation = ""
        self.countyCode = zip2FIPS(self.zip)
        self.subfields = [
            self.streetAddress[:120],
            self.otherDesignation[:120],
            self.city[:50],
            self.state[:50],
            self.zip[:12],
            self.country[:3],
            self.addressType[:3],
            self.otherGeoDesignation,
            self.countyCode[:20]
        ]


def correctLostLeadingZeroZipcode(zip:str, expectedState:str):
    if not zip:
        return zip
    if not expectedState:
        return zip
    try:
        zipData = zipcodes.matching(zip)
    except ValueError:
        return zip
    if zipData:
        return zip
    if len(zip) < 5:
        proposedZip = zip.zfill(5)
        try:
            proposedZipInfo = zipcodes.matching(proposedZip)
        except ValueError:
            return zip
        proposedState = proposedZipInfo[0]["state"]
        if proposedState.upper().strip() == expectedState.upper().strip():
            return proposedZip
        else:
            return zip
    return zip


def zip2FIPS(zip:str):
    if not zip:
        return ""
    try:
        zipData = zipcodes.matching(zip)
    except ValueError:
        return ""
    if not zipData:
        print("Warning: Zipcode %s does not have any associated information." % zip)
        return ""
    state = zipData[0]["state"]
    county = zipData[0]["county"]
    try:
        return fipsData[state][county]
    except KeyError:
        return ""


class TelephoneNumberOrEmail(Hl7Field):

    def __init__(self, value:str=None, countryCode:str= "1"):
        if not value:
            self.subfields = []
        else:
            value = str(value)
            value = value.strip()
            if re.search(emailValidationRegex, value):
                parsable = self.processEmailAddress(value)
            else:
                parsable = self.processPhoneNumber(value, countryCode)
            if parsable:
                self.subfields = [
                    self.depricatedPhoneNumber,
                    self.useCode,
                    self.equipmentType,
                    self.emailAddress,
                    self.countryCode,
                    self.areaCode,
                    self.localNumber,
                    self.extension
                ]
            else:
                self.subfields = []

    def processEmailAddress(self, email:str):
        self.depricatedPhoneNumber = ""
        self.useCode = "NET"
        self.equipmentType = "Internet"
        self.emailAddress = email
        self.countryCode = ""
        self.areaCode = ""
        self.localNumber = ""
        self.extension = ""
        return True

    def processPhoneNumber(self, phoneNumber:str, countryCode:str):
        countryCode = str(countryCode).strip()
        try:
            parsedPhone = re.search(usPhoneNumberRegex, phoneNumber)
        except AttributeError:
            return False
        if not parsedPhone:
            return False
        areaCode, trunk, subscriber, extension = parsedPhone.groups()
        self.depricatedPhoneNumber = ""
        self.useCode = "PRN"
        self.equipmentType = "PH"
        self.emailAddress = ""
        self.countryCode = countryCode
        self.areaCode = areaCode
        self.localNumber = trunk + subscriber
        self.extension = extension
        return True


class AssigningAuthority(Hl7Subfield):

    def __init__(self, name:str, oid:str="", oidSource:str="ISO"):
        self.name = name
        if oid:
            self.oid = oid
        else:
            self.oid = getOID(name)
        self.oidSource = oidSource
        self.subfields = [self.name, self.oid, self.oidSource]


class ProviderInfo(Hl7Field):

    def __init__(self,
                 family:str,
                 given:str,
                 middle:str="",
                 suffix:str="",
                 prefix:str="DR",
                 nameType:str="L",
                 professionalSuffix:str="",
                 idNumber:str="",
                 assigningAuthority:[str, AssigningAuthority]=""):
        self.idNumber = idNumber
        self.family = family
        self.given = given
        self.middle = middle
        self.suffix = suffix
        self.prefix = prefix
        self.degree = ""
        self.sourceTable = ""
        if not self.idNumber:
            self.assigningAuthority = ""
        else:
            self.assigningAuthority = assigningAuthority
        self.nameType = nameType
        self.identifierCheckDigit = ""
        self.checkDigitScheme = ""
        if self.idNumber and hasattr(assigningAuthority, "name"):
            self.identifierTypeCode = "NPI"
        else:
            self.identifierTypeCode = ""
        self.assigningFacility = ""
        self.nameRepCode = ""
        self.nameContext = ""
        self.nameValidityRange = ""
        self.nameAssemblyOrder = ""
        self.effectiveDate = ""
        self.expirationDate = ""
        self.professionalSuffix = professionalSuffix
        self.subfields = [
            self.idNumber[:15],
            self.family[:50],
            self.given[:30],
            self.middle[:30],
            self.suffix[:30],
            self.prefix[:30],
            self.degree,
            self.sourceTable,
            self.assigningAuthority,
            self.nameType[:5],
            self.identifierCheckDigit,
            self.checkDigitScheme,
            self.identifierTypeCode,
            self.assigningFacility,
            self.nameRepCode,
            self.nameContext,
            self.nameValidityRange,
            self.nameAssemblyOrder,
            self.effectiveDate,
            self.expirationDate,
            self.professionalSuffix[:50]
        ]


class SystemCode(Hl7Field):

    def __init__(self,
                 code: str,
                 text: str,
                 coding: str,
                 codingSystemDateOrVersion: str = "",
                 codingSystemOID: str = ""
                 ):
        self.code = code
        self.text = text
        self.coding = self.encodeCodingSystemName(coding)
        self.altID = ""
        self.altIDText = ""
        self.altIDSystem = ""
        if not codingSystemDateOrVersion:
            self.codingSystemDate = getCodingSystemVersion(self.coding)
        else:
            self.codingSystemDate = codingSystemDateOrVersion
        self.altIDSystemVersion = ""
        self.originalText = ""
        self.secondAltID = ""
        self.secondAltText = ""
        self.secondAltIDSystem = ""
        self.secondAltIDSystemVersion = ""
        if codingSystemOID:
            self.codingSystemOID = codingSystemOID
        else:
            self.codingSystemOID = getOID(self.coding)
        self.subfields = [
            self.code,
            self.text,
            self.coding,
            self.altID,
            self.altIDText,
            self.altIDSystem,
            self.codingSystemDate,
            self.altIDSystemVersion,
            self.originalText,
            self.secondAltID,
            self.secondAltText,
            self.secondAltIDSystem,
            self.secondAltIDSystemVersion,
            self.codingSystemOID
            ]

    def encodeCodingSystemName(self, codingSystem:str):
        originalEntry = codingSystem
        codingSystem = codingSystem.upper()
        codingSystem = re.sub("\W", "", codingSystem)
        if codingSystem in ["ICD10", "10"]:
            return "I10"
        elif codingSystem in ["ICD9", "9"]:
            return "I9CDX"
        elif codingSystem in ["LOINC"]:
            return "LN"
        elif codingSystem in ["SNO", "SNOMED"]:
            return "SCT"
        else:
            return originalEntry


def getOID(system:str):
    oidTable = {
        "I10" : "2.16.840.1.113883.6.90",
        "I9CDX" : "2.16.840.1.113883.6.103",
        "LN" : "2.16.840.1.113883.6.1",
        "SCT": "2.16.840.1.113883.6.96",
        "HL70078": "2.16.840.1.113883.12.78",
        "CLIA": "2.16.840.1.113883.19.4.6",
        "NPI": "2.16.840.1.113883.4.6"
    }
    if system in oidTable:
        return oidTable[system]
    else:
        return ""


def getCodingSystemVersion(systemCodeName:str):
    versionTable = {
        "I10": "2019",
        "I9CDX": "10",
        "LN": "2.67",
        "SCT": "20170310"
    }
    if systemCodeName in versionTable:
        return versionTable[systemCodeName]
    else:
        return "NS"

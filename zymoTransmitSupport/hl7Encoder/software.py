from .. import supportData
from .generics import Hl7Field
from . import generics
import os
import datetime


lineStart = "SFT"


class VendorOrg(Hl7Field):

    def __init__(self):
        self.orgName = "Zymo Research"
        self.orgType = "L"  #TODO: Make sure JC is good with this being listed as our legal name
        self.idNumber = ""
        self.checkDigit = ""
        self.checkDigitScheme = ""
        self.assigningAuthority = ""
        self.namespaceID = ""
        self.universalID = ""
        self.universalIDType = ""
        self.identifierTypeCode = ""
        self.assigningFacility = ""
        self.nameRepresentationCode = ""
        self.organizationIdentifier = ""
        self.subfields = [
            self.orgName,
            self.orgType,
            self.idNumber,
            self.checkDigit,
            self.checkDigitScheme,
            self.assigningAuthority,
            self.namespaceID,
            self.universalID,
            self.universalIDType,
            self.identifierTypeCode,
            self.assigningFacility,
            self.nameRepresentationCode,
            self.organizationIdentifier
        ]


class Version(Hl7Field):

    def __init__(self):
        self.softwareVersion = supportData.softwareVersion
        self.subfields = [self.softwareVersion]


class Name(Hl7Field):

    def __init__(self):
        self.softwareName = "Zymo Transmission"
        self.subfields = [self.softwareName]


class BinaryID(Hl7Field):

    def __init__(self):
        self.softwareBinaryID = "Binary ID unknown"
        self.subfields = [self.softwareBinaryID]


class ProductInformation(Hl7Field):
    pass


class InstallDate(Hl7Field):

    def __init__(self):
        thisFileDirectory = os.path.split(os.path.abspath(__file__))[0]
        theDirectoryAbove = os.path.split(thisFileDirectory)[0]
        infoFile = os.path.join(theDirectoryAbove, "supportData.py")
        timeStamp = os.path.getmtime(infoFile)
        parsedTime = datetime.datetime.fromtimestamp(timeStamp)
        timeString = generics.makeTimeString(parsedTime)
        self.subfields = [timeString]


class SoftwareLine(generics.Hl7Line):

    def __init__(self):
        self.vendorOrg = VendorOrg()
        self.version = Version()
        self.name = Name()
        self.binaryID = BinaryID()
        self.productInformation = ProductInformation()
        self.installDate = InstallDate()
        self.fields = [
            lineStart,
            self.vendorOrg,
            self.version,
            self.name,
            self.binaryID,
            self.productInformation,
            self.installDate
        ]

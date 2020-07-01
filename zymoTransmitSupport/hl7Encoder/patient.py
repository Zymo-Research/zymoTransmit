from .generics import Hl7Field
from . import generics
from .. import config


lineStart = "PID"


class SetID(Hl7Field):

    def __init__(self):
        self.value = "1"
        self.subfields = [self.value]


class PatientIdentifierDeprecated(Hl7Field):
    pass


class IDAssignerSubfield(generics.Hl7Subfield):

    def __init__(self, name:str, universalID:str, authority:str):
        self.name = name
        self.universalID = universalID
        self.authority = authority
        self.subfields = [self.name[:20], self.universalID[:199], self.authority[:6]]

    def fromDict(assignerDict:dict):
        name = assignerDict["name"]
        id = assignerDict["id"]
        idType = assignerDict["idType"]
        return IDAssignerSubfield(name, id, idType)

    def fromObject(assigner:config.Configuration.PID.IDAssigner):
        name = assigner.name
        id = assigner.id
        idType = assigner.idType
        return IDAssignerSubfield(name, id, idType)


class FacilitySubfield(generics.Hl7Subfield):

    def __init__(self, name:str, universalID:str, authority:str):
        self.name = name
        self.universalID = universalID
        self.authority = authority
        self.subfields = [self.name[:20], self.universalID[:199], self.authority[:6]]

    def fromDict(facilityDict:dict):
        name = facilityDict["name"]
        id = facilityDict["id"]
        idType = facilityDict["idType"]
        return FacilitySubfield(name, id, idType)

    def fromObject(facility:config.Configuration.PID.Facility):
        name = facility.name
        id = facility.id
        idType = facility.idType
        return FacilitySubfield(name, id, idType)


class PatientIdentifierList(Hl7Field):

    def __init__(self, idNumber:str, idAssigner:IDAssignerSubfield, facility:FacilitySubfield, idType:str="PI"):
        self.idNumber = idNumber
        self.checkDigit = ""
        self.checkDigitScheme = ""
        self.idAssigner = idAssigner
        self.idType = idType
        self.facility = facility
        self.subfields = [self.idNumber[:15], self.checkDigit, self.checkDigitScheme, self.idAssigner, self.idType[:5], self.facility]


class AlternatePatientID(Hl7Field):
    pass


class PatientName(generics.SubjectName):
    pass


class MotherMaidenName(Hl7Field): #TODO: Find out chance any of my users will ever use this
    pass


class DateOfBirth(generics.Date):
    pass


class Sex(Hl7Field):

    def __init__(self, sex:str=None):
        sexMap = {
            "M": "M",
            "F": "F",
            "MALE": "M",
            "FEMALE": "F"
        }
        if not sex:
            sexString = ""
        else:
            sex = sex.upper()
            sexString = sexMap[sex]
        self.subfields = [sexString]


class PatientAlias(Hl7Field):
    pass


class Race(Hl7Field): #TODO: Figure out if other labs are collecting this
    pass


class Address(generics.Address):
    pass


class CountryCode(Hl7Field):
    pass


class TelephoneNumberOrEmail(generics.TelephoneNumberOrEmail):
    pass


class PrimaryLanguage(Hl7Field): #TODO: Find out if any of my intended users will use this
    pass


class MaritalStatus(Hl7Field):
    pass


class Religion(Hl7Field):
    pass


class PatientAccountNumber(Hl7Field):
    pass


class SocialSecurityNumber(Hl7Field):
    pass


class DriversLicenseNumber(Hl7Field):
    pass


class MothersIdentifier(Hl7Field):
    pass


class EthnicGroup(Hl7Field):
    pass


class BirthPlace(Hl7Field):
    pass


class MultipleBirthIndicator(Hl7Field):
    pass


class BirthOrder(Hl7Field):
    pass


class Citizenship(Hl7Field):
    pass


class VeteransMilitaryStatus(Hl7Field):
    pass


class Nationality(Hl7Field):
    pass


class TimeOfDeath(Hl7Field):
    pass


class IdentityUnknownIndicator(Hl7Field):
    pass


class IdentityReliabilityIndicator(Hl7Field):
    pass


class LastUpdatedDemographics(Hl7Field):
    pass


class LastUpdatedFacility(Hl7Field):
    pass


class Species(Hl7Field):
    pass


class PatientIDLine(generics.Hl7Line):

    def __init__(self, patientIdentifierList:PatientIdentifierList, patientName:PatientName, dateOfBirth:DateOfBirth, sex:Sex, address:Address, primaryContact:TelephoneNumberOrEmail, secondaryContact:TelephoneNumberOrEmail=TelephoneNumberOrEmail()):
        self.setID = SetID()
        self.patientIdentifierDeprecated = PatientIdentifierDeprecated()
        self.patientIdentifierList = patientIdentifierList
        self.alternatePatientID = AlternatePatientID()
        self.patientName = patientName
        self.motherMaidenName = MotherMaidenName()
        self.dateOfBirth = dateOfBirth
        self.sex = sex
        self.patientAlias = PatientAlias()
        self.race = Race()
        self.address = address
        self.countryCode = CountryCode()
        self.primaryContact = primaryContact
        self.secondaryContact = secondaryContact
        self.primaryLanguage = PrimaryLanguage()
        self.maritalStatus = MaritalStatus()
        self.religion = Religion()
        self.patientAccountNumber = PatientAccountNumber()
        self.socialSecurity = SocialSecurityNumber()
        self.driversLicense = DriversLicenseNumber()
        self.mothersID = MothersIdentifier()
        self.ethnicGroup = EthnicGroup()
        self.birthPlace = BirthPlace()
        self.multipleBirths = MultipleBirthIndicator()
        self.birthOrder = BirthOrder()
        self.citizenship = Citizenship()
        self.veteransMilitaryStatus = VeteransMilitaryStatus()
        self.nationality = Nationality()
        self.timeOfDeath = TimeOfDeath()
        self.identityUnknownIndicator = IdentityReliabilityIndicator()
        self.lastUpdatedDemos = LastUpdatedDemographics()
        self.lastUpdatedFacility = LastUpdatedFacility()
        self.species = Species()
        self.fields = [
            lineStart,
            self.setID,
            self.patientIdentifierDeprecated,
            self.patientIdentifierList,
            self.alternatePatientID,
            self.patientName,
            self.motherMaidenName,
            self.dateOfBirth,
            self.sex,
            self.patientAlias,
            self.race,
            self.address,
            self.countryCode,
            self.primaryContact,
            self.secondaryContact,
            self.primaryLanguage,
            self.maritalStatus,
            self.religion,
            self.patientAccountNumber,
            self.socialSecurity,
            self.driversLicense,
            self.mothersID,
            self.ethnicGroup,
            self.birthPlace,
            self.multipleBirths,
            self.birthOrder,
            self.citizenship,
            self.veteransMilitaryStatus,
            self.nationality,
            self.timeOfDeath,
            self.identityUnknownIndicator,
            self.lastUpdatedDemos,
            self.lastUpdatedFacility,
            self.species,
        ]
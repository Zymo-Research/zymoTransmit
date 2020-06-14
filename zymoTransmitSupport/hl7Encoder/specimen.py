from .generics import Hl7Field
from . import generics


lineStart = "SPM"


class SetID(generics.SingleValueField):
    default = 1


class SpecimenIDNumber(generics.Hl7Subfield):

    def __init__(self, specimenNumber:str, numberAssigner:str, assignerOID:str="2.16.840.1.114222.xxxxx", oidType:str="ISO"):
        self.specimenNumber = specimenNumber
        self.numberAssigner = numberAssigner
        self.assignerOID = assignerOID
        self.oidType = oidType
        self.subfields=[
            self.specimenNumber[:199],
            self.numberAssigner[:20],
            self.assignerOID[:199],
            self.oidType
        ]


class FillerAssignedIdentifier(Hl7Field):
    delimiter = "&"
    '''
    Should be identical to ORC3
    '''
    def __init__(self, orderID:str, assignerName:str, universalID:str, idType:str="ISO"):
        self.orderID = orderID
        self.name = assignerName
        self.universalID = universalID
        self.idType = idType
        self.subfields = [self.orderID[:199],
                          self.name[:20],
                          self.universalID[:199],
                          self.idType[:6]]


class SpecimenID(Hl7Field):

    def __init__(self, specimenIDNumber:SpecimenIDNumber, fillerAssignedIdentifier:FillerAssignedIdentifier):
        self.specimenIDNumber = specimenIDNumber
        self.fillerSpecimenID = fillerAssignedIdentifier
        self.subfields = [
            self.specimenIDNumber,
            self.fillerSpecimenID
        ]


class SpecimenParentIDs(Hl7Field):
    pass


class SpecimenType(generics.SystemCode):
    '''
    Use SNOMED code
    '''
    pass


class SpecimenTypeModifier(Hl7Field):
    pass


class SpecimenAdditives(Hl7Field):
    pass


class SpecimenCollectionMethod(Hl7Field):
    pass


class SpecimenSourceSite(generics.SystemCode):
    pass


class SpecimenSourceSiteModifier(Hl7Field):
    pass


class SpecimenCollectionSite(Hl7Field):
    pass


class SpecimenRole(Hl7Field):
    pass


class SpecimenCollectionAmount(Hl7Field):
    pass


class GroupedSpecimenCount(Hl7Field):
    pass


class SpecimenDescription(Hl7Field):
    pass


class SpecimenHandlingCode(Hl7Field):
    pass


class SpecimenRiskCode(Hl7Field):
    pass


class SpecimenCollectionDateTime(generics.DateAndTime):
    includeSeconds = True


class SpecimenReceivedDateTime(generics.DateAndTime):
    includeSeconds = True


class SpecimenExpirationDate(Hl7Field):
    pass


class SpecimenAvailability(Hl7Field):
    pass


class SpecimenRejectReason(Hl7Field):
    pass


class SpecimenQuality(Hl7Field):
    pass


class SpecimenAppropriateness(Hl7Field):
    pass


class SpecimenCondition(Hl7Field):
    pass


class SpecimenLine(generics.Hl7Line):
    
    def __init__(self, specimenID:SpecimenID, specimenType:SpecimenType, specimenCollectionDateTime:SpecimenCollectionDateTime, specimenReceivedDateTime:SpecimenReceivedDateTime, specimenSourceSite:SpecimenSourceSite=""):
        self.setID = SetID()
        self.specimenID = specimenID
        self.specimenParentIDs = SpecimenParentIDs()
        self.specimenType = specimenType
        self.specimenTypeModifier = SpecimenTypeModifier()
        self.specimenAdditives = SpecimenAdditives()
        self.specimenCollectionMethod = SpecimenCollectionMethod()
        self.specimenSourceSite = specimenSourceSite
        self.specimenSourceSiteModifier = SpecimenSourceSiteModifier()
        self.specimenCollectionSite = SpecimenCollectionSite()
        self.specimenRole = SpecimenRole()
        self.specimenCollectionAmount = SpecimenCollectionAmount()
        self.groupedSpecimenCount = GroupedSpecimenCount()
        self.specimenDescription = SpecimenDescription()
        self.specimenHandlingCode = SpecimenHandlingCode()
        self.specimenRiskCode = SpecimenRiskCode()
        self.specimenCollectionDateTime = specimenCollectionDateTime
        self.specimenReceivedDateTime = specimenReceivedDateTime
        self.specimenExpirationDate = SpecimenExpirationDate()
        self.specimenAvailability = SpecimenAvailability()
        self.specimenRejectionReason = SpecimenRejectReason()
        self.specimenQuality = SpecimenQuality()
        self.specimenAppropriateness = SpecimenAppropriateness()
        self.specimenCondition = SpecimenCondition()
        self.fields = [
            lineStart,
            self.setID,
            self.specimenID,
            self.specimenParentIDs,
            self.specimenType,
            self.specimenTypeModifier,
            self.specimenAdditives,
            self.specimenCollectionMethod,
            self.specimenSourceSite,
            self.specimenSourceSiteModifier,
            self.specimenCollectionSite,
            self.specimenRole,
            self.specimenCollectionAmount,
            self.groupedSpecimenCount,
            self.specimenDescription,
            self.specimenHandlingCode,
            self.specimenRiskCode,
            self.specimenCollectionDateTime,
            self.specimenReceivedDateTime,
            self.specimenExpirationDate,
            self.specimenAvailability,
            self.specimenRejectionReason,
            self.specimenQuality,
            self.specimenAppropriateness,
            self.specimenCondition,
        ]
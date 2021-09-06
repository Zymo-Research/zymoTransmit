from .generics import Hl7Field
from . import generics


lineStart = "ORC"


class OrderControl(generics.SingleValueField):
    lengthLimit = 3
    default = "RE"


class OrderPlacerNumber(Hl7Field): #TODO: Find out if this is likely to be wanted
    pass


class FillerOrderNumber(Hl7Field):

    def __init__(self, orderID:str, assignerName:str, universalID:str, idType:str="ISO"):
        self.orderID = orderID
        self.name = assignerName
        self.universalID = universalID
        self.idType = idType
        self.subfields = [self.orderID[:199],
                          self.name[:20],
                          self.universalID[:199],
                          self.idType[:6]]


class PlacerGroupNumber(Hl7Field):
    pass


class OrderStatus(generics.SingleValueField):
    lengthLimit = 3
    default = "CM"


class ResponseFlag(Hl7Field):
    pass


class QuantityTiming(Hl7Field):
    pass


class Parent(Hl7Field):
    pass


class TransactionTime(Hl7Field):
    pass


class EnteredBy(Hl7Field):
    pass


class VerifiedBy(Hl7Field):
    pass


class OrderingProvider(generics.ProviderInfo):
    pass


class EntererLocation(Hl7Field):
    pass


class ProviderContact(generics.TelephoneNumberOrEmail):
    pass


class OrderEffectiveTime(generics.DateAndTime):
    includeSeconds = True


class OrderControlCodeReason(Hl7Field):
    pass


class EnteringOrganization(Hl7Field):
    pass


class EnteringDevice(Hl7Field):
    pass


class ActionBy(Hl7Field):
    pass


class AdvancedBeneficiaryNotice(Hl7Field):
    pass


class OrderingFacilityAssigningAuthority(generics.AssigningAuthority):
    pass


class OrderingFacilityName(Hl7Field):
    
    def __init__(self, name:str, assigningAuthority:OrderingFacilityAssigningAuthority, organizationID:str, nameType:str="L", identifierTypeCode:str="XX"):
        self.name = name
        self.nameType = nameType
        self.idNumber = ""
        self.checkDigit = ""
        self.checkDigitScheme = ""
        self.assigningAuthority = assigningAuthority
        self.identifierTypeCode = identifierTypeCode
        self.assigningFacility = ""
        self.nameRepCode = ""
        self.organizationID = organizationID
        self.subfields = [
            self.name,
            self.nameType,
            self.idNumber,
            self.checkDigit,
            self.checkDigitScheme,
            self.assigningAuthority,
            self.identifierTypeCode,
            self.assigningFacility,
            self.nameRepCode,
            self.organizationID
        ]


class OrderingFacilityAddress(generics.Address):
    pass


class OrderingFacilityPhone(generics.TelephoneNumberOrEmail):
    pass


class ProviderAddress(generics.Address):
    pass


class OrderHeaderLine(generics.Hl7Line):
    
    def __init__(self, fillerOrderNumber:FillerOrderNumber,
                 orderingProvider:OrderingProvider,
                 providerContact:ProviderContact,
                 orderingFacilityName:OrderingFacilityName,
                 orderingFacilityAddress:OrderingFacilityAddress,
                 orderingFacilityPhone:OrderingFacilityPhone,
                 orderEffectiveTime:OrderEffectiveTime,
                 providerAddress:ProviderAddress=""):
        self.orderControl = OrderControl()
        self.orderPlacerNumber = OrderPlacerNumber()
        self.fillerOrderNumber = fillerOrderNumber
        self.placerGroupNumber = PlacerGroupNumber()
        self.orderStatus = OrderStatus()
        self.responseFlag = ResponseFlag()
        self.quantityTiming = QuantityTiming()
        self.parent = Parent()
        self.transactionTime = TransactionTime()
        self.enteredBy = EnteredBy()
        self.verifiedBy = VerifiedBy()
        self.orderingProvider = orderingProvider
        self.entererLocation = EntererLocation()
        self.providerContact = providerContact
        self.orderEffectiveTime = orderEffectiveTime
        self.orderControlCodeReason = OrderControlCodeReason()
        self.enteringOrganization = EnteringOrganization()
        self.enteringDevice = EnteringDevice()
        self.actionBy = ActionBy()
        self.advancedBeneficiary = AdvancedBeneficiaryNotice()
        self.orderingFacilityName = orderingFacilityName
        self.orderingFacilityAddress = orderingFacilityAddress
        self.orderingFacilityPhone = orderingFacilityPhone
        self.providerAddress = providerAddress
        self.fields = [
            lineStart,
            self.orderControl,
            self.orderPlacerNumber,
            self.fillerOrderNumber,
            self.placerGroupNumber,
            self.orderStatus,
            self.responseFlag,
            self.quantityTiming,
            self.parent,
            self.transactionTime,
            self.enteredBy,
            self.verifiedBy,
            self.orderingProvider,
            self.entererLocation,
            self.providerContact,
            self.orderEffectiveTime,
            self.orderControlCodeReason,
            self.enteringOrganization,
            self.enteringDevice,
            self.actionBy,
            self.advancedBeneficiary,
            self.orderingFacilityName,
            self.orderingFacilityAddress,
            self.orderingFacilityPhone,
            self.providerAddress
        ]

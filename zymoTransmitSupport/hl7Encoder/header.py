from .generics import Hl7Field
from . import generics
from .. import config
fieldSeparator = "|"

encodingCharacters = r"^~\&"

lineStart = "MSH"

systemName = "Zymo_Transmit"

stagingOID = "2.16.840.1.114222.xxxxx"


class SendingApplication(Hl7Field):

    def __init__(self):
        self.subfields = [systemName[:20], stagingOID[:199], "ISO"]


class SendingFacility(Hl7Field):

    def __init__(self, facilityName:str, labID:str, labIDType:str = "CLIA"):
        self.facilityName = facilityName[:20]
        self.labID = labID
        self.labIDType = labIDType
        self.subfields = [self.facilityName[:20], self.labID[:199], self.labIDType[:6]]
        
    def fromDict(sendingFacilityDict:dict):
        name = sendingFacilityDict["name"]
        id = sendingFacilityDict["id"]
        idType = sendingFacilityDict["idType"]
        return SendingFacility(name, id, idType)

    def fromObject(sendingFacility:config.Configuration.MSH.SendingFacility):
        name = sendingFacility.name
        id = sendingFacility.id
        idType = sendingFacility.idType
        return SendingFacility(name, id, idType)


class ReceivingApplication(Hl7Field):

    def __init__(self, appName: str, appID: str, appIDType: str = "ISO"):
        self.appName = appName
        self.appID = appID
        self.appIDType = appIDType
        self.subfields = [self.appName[:20], self.appID[:199], self.appIDType[:6]]

    def fromDict(receivingApplicationDict:dict):
        name = receivingApplicationDict["name"]
        id = receivingApplicationDict["id"]
        idType = receivingApplicationDict["idType"]
        return ReceivingApplication(name, id, idType)

    def fromObject(receivingApplication:config.Configuration.MSH.ReceivingApplication):
        name = receivingApplication.name
        id = receivingApplication.id
        idType = receivingApplication.idType
        return ReceivingApplication(name, id, idType)


class ReceivingFacility(Hl7Field):
    
    def __init__(self, facilityName: str, facilityID: str, facilityIDType: str = "ISO"):
        self.facilityName = facilityName
        self.facilityID = facilityID
        self.facilityIDType = facilityIDType
        self.subfields = [self.facilityName[:20], self.facilityID[:199], self.facilityIDType[:6]]

    def fromDict(receivingFacilityDict:dict):
        name = receivingFacilityDict["name"]
        id = receivingFacilityDict["id"]
        idType = receivingFacilityDict["idType"]
        return ReceivingApplication(name, id, idType)

    def fromObject(receivingFacility:config.Configuration.MSH.ReceivingFacility):
        name = receivingFacility.name
        id = receivingFacility.id
        idType = receivingFacility.idType
        return ReceivingApplication(name, id, idType)


class TimeStamp(Hl7Field):

    def __init__(self):
        timestamp = generics.makeCurrentTimeString()
        offset = "0000"
        outputString = "%s-%s" %(timestamp, offset)
        self.subfields = [outputString[:24]]


class Security(Hl7Field):
    pass


class MessageType(Hl7Field):

    def __init__(self, messageCode:str, triggerEvent:str, messageStructure:str):
        self.messageCode = messageCode
        self.triggerEvent = triggerEvent
        self.messageStructure = messageStructure
        self.subfields = [self.messageCode, triggerEvent, messageStructure]

    def fromDict(messageTypeDict:dict):
        mType = messageTypeDict["type"]
        triggerEvent = messageTypeDict["triggerEvent"]
        structure = messageTypeDict["structure"]
        return MessageType(mType[:3], triggerEvent[:3], structure[:7])

    def fromObject(messageType:config.Configuration.MSH.MessageType):
        mType = messageType.code
        triggerEvent = messageType.triggerEvent
        structure = messageType.structure
        return MessageType(mType[:3], triggerEvent[:3], structure[:7])


class UniqueID(Hl7Field):

    def __init__(self, id:str, prependTime:bool=True):
        self.id = id
        if prependTime:
            self.id = generics.makeCurrentTimeString() + self.id
        self.subfields = [self.id[:199]]


class ProcessingID(generics.SingleValueField):
    lengthLimit = 1
    default = None


class VersionID(generics.SingleValueField):
    lengthLimit = 5
    default = "2.5.1"


class SequenceNumber(Hl7Field):
    pass


class ContinuationPtr(Hl7Field):
    pass


class AcceptAcknowledgementType(generics.SingleValueField):
    lengthLimit = 2
    default = "NE"


class ApplicationAcknowledgementType(generics.SingleValueField):
    lengthLimit = 2
    default = "NE"


class CountryCode(generics.SingleValueField):
    lengthLimit = 3
    default = "USA"


class CharacterSet(Hl7Field):
    pass


class PrincipleLanguageOfMessage(Hl7Field):
    pass


class AlternateCharacterHandling(Hl7Field):
    pass


class MessageProfileIdentifier(Hl7Field):

    def __init__(self, entityID:str, namespace:str, universalID:str, universalIDType:str):
        self.entityID = entityID
        self.namespace = namespace
        self.universalID = universalID
        self.universalIDType = universalIDType
        self.subfields = [self.entityID[:199], self.namespace[:20], self.universalID[:199], self.universalIDType[:6]]

    def fromDict(profileIDDict:dict):
        entityID = profileIDDict["entity"]
        nameSpace = profileIDDict["namespace"]
        universalID = profileIDDict["universalID"]
        universalIDType = profileIDDict["type"]
        return MessageProfileIdentifier(entityID, nameSpace, universalID, universalIDType)

    def fromObject(profileID:config.Configuration.MSH.MessageProfileIdentifier):
        entityID = profileID.entity
        nameSpace = profileID.nameSpace
        universalID = profileID.universalID
        universalIDType = profileID.idType
        return MessageProfileIdentifier(entityID, nameSpace, universalID, universalIDType)


class MSH(generics.Hl7Line):

    expectEncodingField = encodingCharacters

    def __init__(self,
                 sendingFacility:SendingFacility,
                 receivingApplication:ReceivingApplication,
                 receivingFacility:ReceivingFacility,
                 security:Security,
                 messageType:MessageType,
                 uniqueID:UniqueID,
                 processingID:ProcessingID,
                 versionID:VersionID,
                 sequenceNumber:SequenceNumber,
                 continuationPtr:ContinuationPtr,
                 acceptAcknowledgementType:AcceptAcknowledgementType,
                 applicationAcknowledgementType:ApplicationAcknowledgementType,
                 countryCode:CountryCode,
                 characterSet:CharacterSet,
                 principleLanguageOfMessage:PrincipleLanguageOfMessage,
                 alternateCharacterHandling:AlternateCharacterHandling,
                 messageProfileIdentifier:MessageProfileIdentifier
                 ):
        self.sendingApplication = SendingApplication()
        self.sendingFacility = sendingFacility
        self.receivingAppliation = receivingApplication
        self.receivingFacility = receivingFacility
        self.messageDateTime = TimeStamp()
        self.security = security
        self.messageType = messageType
        self.uniqueID = uniqueID
        self.processingID = processingID
        self.versionID = versionID
        self.sequenceNumber = sequenceNumber
        self.continuationPtr = continuationPtr
        self.acceptAcknowledgementType = acceptAcknowledgementType
        self.applicationAcknowledgementType = applicationAcknowledgementType
        self.countryCode =countryCode
        self.characterSet = characterSet
        self.principleLanguageOfMessage = principleLanguageOfMessage
        self.alternateCharacterHandling = alternateCharacterHandling
        self.messageProfileIdentifier = messageProfileIdentifier
        self.fields = [
            lineStart,
            encodingCharacters,
            self.sendingApplication,
            self.sendingFacility,
            self.receivingAppliation,
            self.receivingFacility,
            self.messageDateTime,
            self.security,
            self.messageType,
            self.uniqueID,
            self.processingID,
            self.versionID,
            self.sequenceNumber,
            self.continuationPtr,
            self.acceptAcknowledgementType,
            self.applicationAcknowledgementType,
            self.countryCode,
            self.characterSet,
            self.principleLanguageOfMessage,
            self.alternateCharacterHandling,
            self.messageProfileIdentifier
        ]


class MSHFromConfig(generics.Hl7Line):

    expectEncodingField = encodingCharacters

    def __init__(self,
                 configDict:dict,
                 uniqueID: UniqueID,
                 production:bool,
                 ):
        self.sendingApplication = SendingApplication()
        self.sendingFacility = SendingFacility.fromDict(configDict["sendingFacility"])
        self.receivingAppliation = ReceivingApplication.fromDict(configDict["receivingApplication"])
        self.receivingFacility = ReceivingFacility.fromDict(configDict["receivingFacility"])
        self.messageDateTime = TimeStamp()
        self.security = Security()
        self.messageType = MessageType.fromDict(configDict["messageType"])
        self.uniqueID = uniqueID
        if production:
            self.processingID = ProcessingID(configDict["processingID"]["production"])
        else:
            self.processingID = ProcessingID(configDict["processingID"]["testing"])
        self.versionID = VersionID()
        self.sequenceNumber = SequenceNumber()
        self.continuationPtr = ContinuationPtr()
        self.acceptAcknowledgementType = AcceptAcknowledgementType()
        self.applicationAcknowledgementType = ApplicationAcknowledgementType()
        self.countryCode = CountryCode()
        self.characterSet = CharacterSet()
        self.principleLanguageOfMessage = PrincipleLanguageOfMessage()
        self.alternateCharacterHandling = AlternateCharacterHandling()
        self.messageProfileIdentifier = MessageProfileIdentifier.fromDict(configDict["messageProfileIdentifier"])
        self.fields = [
            lineStart,
            encodingCharacters,
            self.sendingApplication,
            self.sendingFacility,
            self.receivingAppliation,
            self.receivingFacility,
            self.messageDateTime,
            self.security,
            self.messageType,
            self.uniqueID,
            self.processingID,
            self.versionID,
            self.sequenceNumber,
            self.continuationPtr,
            self.acceptAcknowledgementType,
            self.applicationAcknowledgementType,
            self.countryCode,
            self.characterSet,
            self.principleLanguageOfMessage,
            self.alternateCharacterHandling,
            self.messageProfileIdentifier
        ]


class MSHFromObject(generics.Hl7Line):

    expectEncodingField = encodingCharacters

    def __init__(self,
                 mshObject:config.Configuration.MSH,
                 uniqueID: UniqueID,
                 production:bool,
                 ):
        self.sendingApplication = SendingApplication()
        self.sendingFacility = SendingFacility.fromObject(mshObject.SendingFacility)
        self.receivingAppliation = ReceivingApplication.fromObject(mshObject.ReceivingApplication)
        self.receivingFacility = ReceivingFacility.fromObject(mshObject.ReceivingFacility)
        self.messageDateTime = TimeStamp()
        self.security = Security()
        self.messageType = MessageType.fromObject(mshObject.MessageType)
        self.uniqueID = uniqueID
        if production:
            self.processingID = ProcessingID(mshObject.ProcessingID.production)
        else:
            self.processingID = ProcessingID(mshObject.ProcessingID.testing)
        self.versionID = VersionID()
        self.sequenceNumber = SequenceNumber()
        self.continuationPtr = ContinuationPtr()
        self.acceptAcknowledgementType = AcceptAcknowledgementType()
        self.applicationAcknowledgementType = ApplicationAcknowledgementType()
        self.countryCode = CountryCode()
        self.characterSet = CharacterSet()
        self.principleLanguageOfMessage = PrincipleLanguageOfMessage()
        self.alternateCharacterHandling = AlternateCharacterHandling()
        self.messageProfileIdentifier = MessageProfileIdentifier.fromObject(mshObject.MessageProfileIdentifier)
        self.fields = [
            lineStart,
            encodingCharacters,
            self.sendingApplication,
            self.sendingFacility,
            self.receivingAppliation,
            self.receivingFacility,
            self.messageDateTime,
            self.security,
            self.messageType,
            self.uniqueID,
            self.processingID,
            self.versionID,
            self.sequenceNumber,
            self.continuationPtr,
            self.acceptAcknowledgementType,
            self.applicationAcknowledgementType,
            self.countryCode,
            self.characterSet,
            self.principleLanguageOfMessage,
            self.alternateCharacterHandling,
            self.messageProfileIdentifier
        ]
from .generics import Hl7Field
from . import generics


lineStart = "OBR"


class OBRSet(generics.SingleValueField):
    default = 1


class PlacerOrderNumber(Hl7Field):
    '''
    Should be identical to ORC2
    '''
    pass


class FillerOrderNumber(Hl7Field):
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


class UniversalServiceIdentifier(generics.SystemCode):
    '''
    Use a LOINC code here
    '''
    pass


class Priority(Hl7Field):
    pass


class RequestedDateTime(Hl7Field):
    pass


class ObservedDateTime(generics.DateAndTime):
    includeSeconds = True


class ObservationEndDateTime(Hl7Field):
    pass


class CollectionVolume(Hl7Field):
    pass


class CollectorIdentifier(Hl7Field):
    pass


class SpecimenActionCode(Hl7Field):
    pass


class DangerCode(Hl7Field):
    pass


class RelevantClinicalInformation(generics.SingleValueField):
    lengthLimit = 300


class SpecimenReceivedDateTime(Hl7Field):
    pass


class SpecimenSource(Hl7Field):
    pass


class OrderingProvider(generics.ProviderInfo):
    pass


class OrderCallBackNumber(generics.TelephoneNumberOrEmail):
    pass


class PlacerField1(Hl7Field):
    pass


class PlacerField2(Hl7Field):
    pass


class FillerField1(Hl7Field):
    pass


class FillerField2(Hl7Field):
    pass


class ResultsReported(generics.DateAndTime):
    includeSeconds = True


class ChargeToPractice(Hl7Field):
    pass


class DiagnosticServiceSectID(generics.SingleValueField):
    lengthLimit = 3


class ResultStatus(generics.SingleValueField):
    lengthLimit = 1
    default = "F"


class ParentResult(Hl7Field):
    pass


class QuantityTiming(Hl7Field):
    pass


class CopiesTo(Hl7Field):
    pass


class ParentOrders(Hl7Field):
    pass


class TransportationMode(Hl7Field):
    pass


class ReasonForStudy(generics.SystemCode):
    pass


class PrincipleResultInterpreter(Hl7Field):
    pass


class OrderRequestLine(generics.Hl7Line): #Making you describe your specific test type. Because I <3 good epidemiology data and quality metrics.

    def __init__(self, fillerOrderNumber:FillerOrderNumber,
                 universalServiceIdentifier:UniversalServiceIdentifier,
                 observedDateAndTime:ObservedDateTime, 
                 orderingProvider:OrderingProvider, 
                 orderCallBackNumber:OrderCallBackNumber, 
                 resultsReported:ResultsReported, 
                 reasonForStudy:ReasonForStudy=ReasonForStudy(
                     code = "Z11.5",
                     text = "Special screening examination for other viral diseases (SARS-CoV2)",
                     coding = "I10",
                     codingSystemDateOrVersion = "03/25/2020",
                     codingSystemOID = "2.16.840.1.113883.6.90"
                 ),
                 relevantClinicalInformation:RelevantClinicalInformation=RelevantClinicalInformation()
                 ):
        self.obrSet = OBRSet()
        self.PlacerOrderNumber = PlacerOrderNumber()
        self.fillerOrderNumber = fillerOrderNumber
        self.universalServiceIdentifier = universalServiceIdentifier
        self.priority = Priority()
        self.requestedDateTime = RequestedDateTime()
        self.observedDateTime = observedDateAndTime
        self.observationEndDateTime = ObservationEndDateTime()
        self.collectionVolume = CollectionVolume()
        self.collectorIdentifier = CollectorIdentifier()
        self.specimenActionCode = SpecimenActionCode()
        self.dangerCode = DangerCode() #someone call Kenny Loggins, cause...
        self.relevantClinicalInformation = relevantClinicalInformation
        self.specimenReceivedDateTime = SpecimenReceivedDateTime()
        self.specimenSource = SpecimenSource()
        self.orderingProvider = orderingProvider
        self.orderCallBackNumber = orderCallBackNumber
        self.placerField1 = PlacerField1()
        self.placerField2 = PlacerField2()
        self.fillerField1 = FillerField1()
        self.fillerField2 = FillerField2()
        self.resultsReported = resultsReported
        self.chargeToPractice = ChargeToPractice()
        self.diagnosticServiceSectID = DiagnosticServiceSectID()
        self.resultStatus = ResultStatus()
        self.parentResult = ParentResult()
        self.quantityTiming = QuantityTiming()
        self.copiesTo = CopiesTo()
        self.parentOrders = ParentOrders()
        self.transportationMode = TransportationMode()
        self.reasonForStudy = reasonForStudy
        self.principleResultInterpreter = PrincipleResultInterpreter()
        self.fields = [
            lineStart,
            self.obrSet,
            self.PlacerOrderNumber,
            self.fillerOrderNumber,
            self.universalServiceIdentifier,
            self.priority,
            self.requestedDateTime,
            self.observedDateTime,
            self.observationEndDateTime,
            self.collectionVolume,
            self.collectorIdentifier,
            self.specimenActionCode,
            self.dangerCode,
            self.relevantClinicalInformation,
            self.specimenReceivedDateTime,
            self.specimenSource,
            self.orderingProvider,
            self.orderCallBackNumber,
            self.placerField1,
            self.placerField2,
            self.fillerField1,
            self.fillerField2,
            self.resultsReported,
            self.chargeToPractice,
            self.diagnosticServiceSectID,
            self.resultStatus,
            self.parentResult,
            self.quantityTiming,
            self.copiesTo,
            self.parentOrders,
            self.transportationMode,
            self.reasonForStudy,
            self.principleResultInterpreter,
        ]

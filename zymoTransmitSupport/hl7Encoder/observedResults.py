from .generics import Hl7Field
from . import generics


lineStart = "OBX"


class OBXSet(generics.SingleValueField):
    default = 1
    lengthLimit = 4


class ValueType(generics.SingleValueField):
    default = "CWE"
    lengthLimit = 3


class ObservationIdentifier(generics.SystemCode):
    '''
    Use LOINC code
    '''
    pass


class ObservationSubID(Hl7Field):
    pass


def getObservationValue(result:str):
    '''
    Returns the appropriate object to code the test result
    :param result: String describing the result. Must be in ["detected", "indeterminate", "negative"]
    :return: An appropriate result as a generics.SystemCode object
    '''
    validResults = ["detected", "indeterminate", "negative", "unsatisfactory", ""]
    if not result in validResults:
        raise ValueError("Result type must be in: " %validResults)
    if result == "detected":
        return generics.SystemCode(code="260373001", text="Detected", coding="SNOMED", codingSystemDateOrVersion="2.7")
    elif result == "indeterminate":
        return generics.SystemCode(code="419984006", text="Inconclusive", coding="SNOMED", codingSystemDateOrVersion="2.7")
    elif result == "negative":
        return generics.SystemCode(code="260415000", text="Not detected", coding="SNOMED", codingSystemDateOrVersion="2.7")
    elif result == "unsatisfactory":
        return generics.SystemCode(code="125154007", text="Specimen unsatisfactory", coding="SNOMED", codingSystemDateOrVersion="2.7")
    elif result == "":
        return ""
    else:
        raise RuntimeError("This code should be unreachable if result validations is working properly and how we got here needs to be investigated")


class ObservedUnits(Hl7Field):
    pass


class ReferenceRange(Hl7Field):
    pass


def getAbnormalityObject(result:str):
    '''
    Returns the appropriate object to code the test result
    :param result: String describing the result. Must be in ["detected", "indeterminate", "negative"]
    :return: An appropriate result as a generics.SystemCode object
    '''
    validResults = ["detected", "indeterminate", "negative", "unsatisfactory", ""]
    if not result in validResults:
        raise ValueError("Result type must be in: " %validResults)
    if result == "detected":
        return generics.SystemCode(code="260373001", text="Detected", coding="SNOMED", codingSystemDateOrVersion="2.7")
    elif result == "indeterminate":
        return generics.SystemCode(code="419984006", text="Inconclusive", coding="SNOMED", codingSystemDateOrVersion="2.7")
    elif result == "negative":
        return generics.SystemCode(code="260415000", text="Not detected", coding="SNOMED", codingSystemDateOrVersion="2.7")
    elif result == "unsatisfactory":
        return generics.SystemCode(code="125154007", text="Specimen unsatisfactory", coding="SNOMED", codingSystemDateOrVersion="2.7")
    elif result == "":
        return ""
    else:
        raise RuntimeError("This code should be unreachable if result validations is working properly and how we got here needs to be investigated")


class Probability(Hl7Field):
    pass


class NatureOfAbnormalTest(Hl7Field):
    pass


class ObservationResultStatus(generics.SingleValueField):
    '''
    Defaults to final, enter "X" for being unable to get a result and P for preliminary result
    '''
    lengthLimit = 1
    default = "F"


class EffectiveDateOfRefRange(Hl7Field):
    pass


class UserDefinedAccessChecks(Hl7Field):
    pass


class ObservationDateTime(generics.DateAndTime):
    includeSeconds = True


class ProducersID(Hl7Field):
    pass


class ResponsibleObserver(Hl7Field):
    pass


class ObservationMethod(Hl7Field): #Going to see if I can leave this one out for now
    pass


class EquipmentInstanceIdentifier(Hl7Field):
    pass


class AnalysisDateAndTime(generics.DateAndTime):
    includeSeconds = True


class Deprecated1(Hl7Field):
    pass


class Deprecated2(Hl7Field):
    pass


class Deprecated3(Hl7Field):
    pass
        

class PerformingOrganization(Hl7Field):

    def __init__(self, orgName:str, cliaNumber:str, nameType:str="L"):
        self.orgName = orgName
        self.nameType = nameType
        self.deprecatedID = ""
        self.checkDigit = ""
        self.checkDigitScheme = ""
        self.assigningAuthority = generics.AssigningAuthority("CLIA")
        self.identifierType = "XX"
        self.assigningFacility = ""
        self.nameRepresentationCode = ""
        self.organizationIdentifier = cliaNumber
        self.subfields = [
            self.orgName[:50],
            self.nameType[:20],
            self.deprecatedID,
            self.checkDigit,
            self.checkDigitScheme,
            self.assigningAuthority,
            self.identifierType[:5],
            self.assigningFacility,
            self.nameRepresentationCode,
            self.organizationIdentifier,
        ]


class PerformingOrganizationLabAddress(generics.Address):
    defaultAddressType = "B"


class MedicalDirectorNumberAssignmentAuthority(generics.AssigningAuthority):
    pass


class PerformingOrganizationMedicalDirector(generics.ProviderInfo):
    pass


class ObservedResultsLine(generics.Hl7Line):
    
    def __init__(self,
                 observationIdentifier:ObservationIdentifier,
                 observationValue:generics.SystemCode,
                 abnormalityValue:generics.SystemCode,
                 observationDateAndTime:ObservationDateTime,
                 analysisDateAndTime:AnalysisDateAndTime,
                 performingOrganization:PerformingOrganization,
                 performingOrganizationAddress:PerformingOrganizationLabAddress,
                 performingOrganizationMedicalDirector:PerformingOrganizationMedicalDirector,
                 observationResultStatus:ObservationResultStatus=ObservationResultStatus()
                 ):
        self.obxSet = OBXSet()
        self.valueType = ValueType()
        self.observationIdentifier = observationIdentifier
        self.observationSubID = ObservationSubID()
        self.observationValue = observationValue
        self.observedUnits = ObservedUnits()
        self.referenceRange = ReferenceRange()
        self.result = abnormalityValue
        self.probability = Probability()
        self.natureOfAbnormalTest = NatureOfAbnormalTest()
        self.observationResultStatus = observationResultStatus
        self.effectiveDateOfRefRange = EffectiveDateOfRefRange()
        self.userDefinedAccessChecks = UserDefinedAccessChecks()
        self.observationDateAndTime = observationDateAndTime
        self.producersID = ProducersID()
        self.responsibleObserver = ResponsibleObserver()
        self.observationMethod = ObservationMethod()
        self.equipmentInstanceIdentifier = EquipmentInstanceIdentifier()
        self.analysisDateAndTime = analysisDateAndTime
        self.deprecated1 = Deprecated1()
        self.deprecated2 = Deprecated2()
        self.deprecated3 = Deprecated3()
        self.performingOrganization = performingOrganization
        self.performingOrganizationAddress = performingOrganizationAddress
        self.performingOrganizationMedicalDirector = performingOrganizationMedicalDirector
        self.fields = [
            lineStart,
            self.obxSet,
            self.valueType,
            self.observationIdentifier,
            self.observationSubID,
            self.observationValue,
            self.observedUnits,
            self.referenceRange,
            self.result,
            self.probability,
            self.natureOfAbnormalTest,
            self.observationResultStatus,
            self.effectiveDateOfRefRange,
            self.userDefinedAccessChecks,
            self.observationDateAndTime,
            self.producersID,
            self.responsibleObserver,
            self.observationMethod,
            self.equipmentInstanceIdentifier,
            self.analysisDateAndTime,
            self.deprecated1,
            self.deprecated2,
            self.deprecated3,
            self.performingOrganization,
            self.performingOrganizationAddress,
            self.performingOrganizationMedicalDirector
        ]




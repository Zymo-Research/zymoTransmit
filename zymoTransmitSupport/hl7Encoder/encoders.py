from .. import config as defaultConfig
from .. import inputOutput
from . import header
from . import software
from . import patient
from . import orderHeader
from . import orderRequest
from . import observedResults
from . import specimen
from . import noteLine
from . import loinc
from . import snomed
from . import generics

config = defaultConfig

def makeMSHLine():
    uniqueID = header.UniqueID(config.LabInfo.name, prependTime=True)
    return header.MSHFromObject(config.Configuration.MSH, uniqueID, config.Configuration.productionReady)


def makeSFTLine():
    return software.SoftwareLine()


def makePIDLine(result:inputOutput.resultReader.TestResult):
    idAssigner = patient.IDAssignerSubfield.fromObject(config.Configuration.PID.IDAssigner)
    facility = patient.FacilitySubfield.fromObject(config.Configuration.PID.Facility)
    patientIdentifierList = patient.PatientIdentifierList(
        result.patientID,
        idAssigner,
        facility)
    patientName = patient.PatientName(
        result.patientLastName,
        result.patientFirstName,
        result.patientMiddleName
    )
    dateOfBirth = patient.DateOfBirth(
        result.patientDateOfBirth.year,
        result.patientDateOfBirth.month,
        result.patientDateOfBirth.day
    )
    sex = patient.Sex(result.patientSex)
    address = patient.Address(
        result.patientStreetAddress,
        result.patientCity,
        result.patientState,
        result.patientZip
    )
    primaryContact = patient.TelephoneNumberOrEmail(result.patientPhone)
    return patient.PatientIDLine(patientIdentifierList,
                                                                patientName,
                                                                dateOfBirth,
                                                                sex,
                                                                address,
                                                                primaryContact)


def makeORCLine(result:inputOutput.resultReader.TestResult):
    fillerOrderNumber = orderHeader.FillerOrderNumber(
        "%s.%s" %(result.patientID, result.specimenID),
        config.LabInfo.name,
        config.LabInfo.clia,
        "CLIA"
    )
    orderingProvider = orderHeader.OrderingProvider(
        result.providerLastName,
        result.providerFirstName,
        result.providerMiddleName
    )
    providerContact = orderHeader.ProviderContact(result.providerPhone)
    orderingFacilityAssigningAuthority = orderHeader.OrderingFacilityAssigningAuthority(
        "CLIA"
    )
    orderingFacilityName = orderHeader.OrderingFacilityName(
        config.LabInfo.name,
        orderingFacilityAssigningAuthority,
        config.LabInfo.clia
    )
    orderingFacilityAddress = orderHeader.OrderingFacilityAddress(
        config.LabInfo.street,
        config.LabInfo.city,
        config.LabInfo.state,
        config.LabInfo.zip
    )
    orderingFacilityPhone = orderHeader.OrderingFacilityPhone(config.LabInfo.phone)

    return orderHeader.OrderHeaderLine(
        fillerOrderNumber,
        orderingProvider,
        providerContact,
        orderingFacilityName,
        orderingFacilityAddress,
        orderingFacilityPhone
    )


def makeOBRLine(result:inputOutput.resultReader.TestResult):
    fillerOrderNumber = orderRequest.FillerOrderNumber(
        "%s.%s" %(result.patientID, result.specimenID),
        config.LabInfo.name,
        config.LabInfo.clia,
        "CLIA"
    )
    serviceData = loinc.loincTable[result.testLOINC]
    universalServiceIdentifier = orderRequest.UniversalServiceIdentifier(
        result.testLOINC,
        serviceData.commonName,
        coding="LOINC"
    )
    observedDateAndTime = orderRequest.ObservedDateTime(
        result.analysisDate.year,
        result.analysisDate.month,
        result.analysisDate.day
    )
    orderingProvider = orderRequest.OrderingProvider(
        result.providerLastName,
        result.providerFirstName,
        result.providerMiddleName
    )
    orderCallBackNumber = orderRequest.OrderCallBackNumber(
        result.providerPhone
    )
    resultsReported = orderRequest.ResultsReported(
        result.reportedDate.year,
        result.reportedDate.month,
        result.reportedDate.day
    )
    return orderRequest.OrderRequestLine(
        fillerOrderNumber,
        universalServiceIdentifier,
        observedDateAndTime,
        orderingProvider,
        orderCallBackNumber,
        resultsReported
    )


def makeOBXLine(result:inputOutput.resultReader.TestResult):
    def makeObservationValueAndAbnormalityObjects(resultString:str):
        resultStringUpper = resultString.upper()
        if resultStringUpper in config.ResultTerms.indeterminateResultTerms:
            resultTerm = "indeterminate"
        elif resultStringUpper in config.ResultTerms.positiveResultTerms:
            resultTerm = "detected"
        elif resultStringUpper in config.ResultTerms.negativeResultTerms:
            resultTerm = "negative"
        else:
            raise ValueError("Unable to classify result '%s'. Preferred terms are: detected, indeterminate, and negative." %resultString)
        return (observedResults.getObservationValue(resultTerm),
                observedResults.getAbnormalityObject(resultTerm))

    observationData = loinc.loincTable[result.testLOINC]
    observationIdentifier = observedResults.ObservationIdentifier(
        result.testLOINC,
        observationData.commonName,
        coding="LOINC"
    )
    observationValue, abnormalityObject = makeObservationValueAndAbnormalityObjects(result.resultString)
    observationDateTime = observedResults.ObservationDateTime(
        result.collectionDate.year,
        result.collectionDate.month,
        result.collectionDate.day
    )
    analysisDateTime = observedResults.AnalysisDateAndTime(
        result.analysisDate.year,
        result.analysisDate.month,
        result.analysisDate.day
    )
    performingOrganization = observedResults.PerformingOrganization(
        config.LabInfo.name,
        config.LabInfo.clia
    )
    labAddress = observedResults.PerformingOrganizationLabAddress(
        config.LabInfo.street,
        config.LabInfo.city,
        config.LabInfo.state,
        config.LabInfo.zip
    )
    if config.LabDirectorInfo.assigningAuthority:
        medicalDirectorAssignmentAuthority = observedResults.MedicalDirectorNumberAssignmentAuthority(
            config.LabDirectorInfo.assigningAuthority
        )
    else:
        medicalDirectorAssignmentAuthority = ""
    performingOrganizationMedicalDirector = observedResults.PerformingOrganizationMedicalDirector(
        config.LabDirectorInfo.lastName,
        config.LabDirectorInfo.firstName,
        config.LabDirectorInfo.middleName,
        config.LabDirectorInfo.suffix,
        config.LabDirectorInfo.prefix,
        professionalSuffix = config.LabDirectorInfo.professionalSuffix,
        idNumber = config.LabDirectorInfo.identifier,
        assigningAuthority = medicalDirectorAssignmentAuthority
    )
    return observedResults.ObservedResultsLine(
        observationIdentifier,
        observationValue,
        abnormalityObject,
        observationDateTime,
        analysisDateTime,
        performingOrganization,
        labAddress,
        performingOrganizationMedicalDirector
    )


def makeSPMLine(result:inputOutput.resultReader.TestResult):
    specimenData = snomed.snomedTable[result.specimenSNOMED]
    specimenIDNumber = specimen.SpecimenIDNumber(
        result.specimenID,
        config.LabInfo.name
    )
    fillerAssignedIdentifier = specimen.FillerAssignedIdentifier(
        "%s.%s" %(result.patientID, result.specimenID),
        config.LabInfo.name,
        config.LabInfo.clia,
        "CLIA"
    )
    specimenID = specimen.SpecimenID(
        specimenIDNumber,
        fillerAssignedIdentifier
    )
    specimenType = specimen.SpecimenType(
        result.specimenSNOMED,
        specimenData.preferredName,
        "SNOMED"
    )
    specimenCollectionDateTime = specimen.SpecimenCollectionDateTime(
        result.collectionDate.year,
        result.collectionDate.month,
        result.collectionDate.day
    )
    specimenReceivedDateTime = specimen.SpecimenReceivedDateTime(
        result.receivedDate.year,
        result.receivedDate.month,
        result.receivedDate.day
    )
    return specimen.SpecimenLine(
        specimenID,
        specimenType,
        specimenCollectionDateTime,
        specimenReceivedDateTime
    )


def makeNTELine(result:inputOutput.resultReader.TestResult):
    noteText = noteLine.NoteText(result.note)
    return noteLine.NoteLine(noteText)

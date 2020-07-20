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

def makeMSHLine(result:inputOutput.resultReader.TestResult):
    uniqueID = header.UniqueID(config.LabInfo.name, prependTime=True)
    return header.MSHFromObject(config.Configuration.MSH, uniqueID, config.Configuration.productionReady, result.auxiliaryData)


def makeSFTLine(passThruMode:bool=False):
    return software.SoftwareLine(passThruMode)


def makePIDLine(result:inputOutput.resultReader.TestResult):
    if "labName" in result.auxiliaryData or "labCLIA" in result.auxiliaryData:
        if not ("labName" in result.auxiliaryData and "labCLIA" in result.auxiliaryData):
            raise ValueError("Lab name and lab CLIA must both be either present or absent in auxiliary data")
        idAssigner = patient.IDAssignerSubfield(result.auxiliaryData["labName"], result.auxiliaryData["labCLIA"], "CLIA")
        facility = patient.FacilitySubfield(result.auxiliaryData["labName"], result.auxiliaryData["labCLIA"], "CLIA")
    else:
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
    return patient.PatientIDLine(
        patientIdentifierList,
        patientName,
        dateOfBirth,
        sex,
        address,
        primaryContact,
        result.race,
        result.ethnicity
    )


def makeORCLine(result:inputOutput.resultReader.TestResult):
    if "labName" in result.auxiliaryData or "labCLIA" in result.auxiliaryData:
        if not ("labName" in result.auxiliaryData and "labCLIA" in result.auxiliaryData):
            raise ValueError("Lab name and lab CLIA must both be either present or absent in auxiliary data")
        fillerOrderNumber = orderHeader.FillerOrderNumber(
            "%s.%s" % (result.patientID, result.specimenID),
            result.auxiliaryData["labName"],
            result.auxiliaryData["labCLIA"],
            "CLIA"
        )
    else:
        fillerOrderNumber = orderHeader.FillerOrderNumber(
            "%s.%s" % (result.patientID, result.specimenID),
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
    if "labName" in result.auxiliaryData or "labCLIA" in result.auxiliaryData:
        if not ("labName" in result.auxiliaryData and "labCLIA" in result.auxiliaryData):
            raise ValueError("Lab name and lab CLIA must both be either present or absent in auxiliary data")
        orderingFacilityName = orderHeader.OrderingFacilityName(
            result.auxiliaryData["labName"],
            orderingFacilityAssigningAuthority,
            result.auxiliaryData["labCLIA"]
        )
    else:
        orderingFacilityName = orderHeader.OrderingFacilityName(
            config.LabInfo.name,
            orderingFacilityAssigningAuthority,
            config.LabInfo.clia,
        )
    if "labStreet" in result.auxiliaryData or "labCity" in result.auxiliaryData or "labState" in result.auxiliaryData or "labZip" in result.auxiliaryData:
        if not (
                "labStreet" in result.auxiliaryData and "labCity" in result.auxiliaryData and "labState" and result.auxiliaryData or "labZip" in result.auxiliaryData):
            raise ValueError(
                "All or no elements of lab address (street, city, state, zip) must be defined in auxiliary data")
        orderingFacilityAddress = orderHeader.OrderingFacilityAddress(
            result.auxiliaryData["labStreet"],
            result.auxiliaryData["labCity"],
            result.auxiliaryData["labState"],
            result.auxiliaryData["labZip"]
        )
    else:
        orderingFacilityAddress = orderHeader.OrderingFacilityAddress(
            config.LabInfo.street,
            config.LabInfo.city,
            config.LabInfo.state,
            config.LabInfo.zip
        )
    if "labPhone" in result.auxiliaryData:
        orderingFacilityPhone = orderHeader.OrderingFacilityPhone(result.auxiliaryData["labPhone"])
    else:
        orderingFacilityPhone = orderHeader.OrderingFacilityPhone(config.LabInfo.phone)

    orderingProviderAddress = orderHeader.ProviderAddress(
        result.providerStreet,
        result.providerCity,
        result.providerState,
        result.providerZip
    )
    return orderHeader.OrderHeaderLine(
        fillerOrderNumber,
        orderingProvider,
        providerContact,
        orderingFacilityName,
        orderingFacilityAddress,
        orderingFacilityPhone,
        orderingProviderAddress
    )


def makeOBRLine(result:inputOutput.resultReader.TestResult):
    if "labName" in result.auxiliaryData or "labCLIA" in result.auxiliaryData:
        if not ("labName" in result.auxiliaryData and "labCLIA" in result.auxiliaryData):
            raise ValueError("Lab name and lab CLIA must both be either present or absent in auxiliary data")
        fillerOrderNumber = orderRequest.FillerOrderNumber(
            "%s.%s" % (result.patientID, result.specimenID),
            result.auxiliaryData["labName"],
            result.auxiliaryData["labCLIA"],
            "CLIA"
        )
    else:
        fillerOrderNumber = orderRequest.FillerOrderNumber(
            "%s.%s" % (result.patientID, result.specimenID),
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
        result.analysisDateTime.year,
        result.analysisDateTime.month,
        result.analysisDateTime.day,
        result.analysisDateTime.hour,
        result.analysisDateTime.minute,
        result.analysisDateTime.second
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
        result.reportedDateTime.year,
        result.reportedDateTime.month,
        result.reportedDateTime.day,
        result.reportedDateTime.hour,
        result.reportedDateTime.minute,
        result.reportedDateTime.second
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
        if "NOT DETECTED" in resultStringUpper:
            resultTerm = "negative"
        elif resultStringUpper in config.ResultTerms.indeterminateResultTerms:
            resultTerm = "indeterminate"
        elif resultStringUpper in config.ResultTerms.positiveResultTerms:
            resultTerm = "detected"
        elif resultStringUpper in config.ResultTerms.negativeResultTerms:
            resultTerm = "negative"
        elif resultStringUpper in config.ResultTerms.unsatisfactorySpecimenResultTerms:
            resultTerm = "unsatisfactory"
        else:
            print("Unable to classify result '%s' for patient %s specimen %s. Preferred terms are: detected, indeterminate, negative, and unsatisfactory specimen." %(resultString, result.patientID, result.specimenID))
            resultTerm = ""
            result.okToTransmit = False
            result.reasonForFailedTransmission.append("Failed to interpret result value. Please modify config.py to interpret the result value or modify the result value to something that is already interpreted.")
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
        result.collectionDateTime.year,
        result.collectionDateTime.month,
        result.collectionDateTime.day,
        result.collectionDateTime.hour,
        result.collectionDateTime.minute,
        result.collectionDateTime.second
    )
    analysisDateTime = observedResults.AnalysisDateAndTime(
        result.analysisDateTime.year,
        result.analysisDateTime.month,
        result.analysisDateTime.day,
        result.analysisDateTime.hour,
        result.analysisDateTime.minute,
        result.analysisDateTime.second
    )
    if "labName" in result.auxiliaryData or "labCLIA" in result.auxiliaryData:
        if not ("labName" in result.auxiliaryData and "labCLIA" in result.auxiliaryData):
            raise ValueError("Lab name and lab CLIA must both be either present or absent in auxiliary data")
        performingOrganization = observedResults.PerformingOrganization(
            result.auxiliaryData["labName"],
            result.auxiliaryData["labCLIA"]
        )
    else:
        performingOrganization = observedResults.PerformingOrganization(
            config.LabInfo.name,
            config.LabInfo.clia
        )
    if "labStreet" in result.auxiliaryData or "labCity" in result.auxiliaryData or "labState" in result.auxiliaryData or "labZip" in result.auxiliaryData:
        if not ("labStreet" in result.auxiliaryData and "labCity" in result.auxiliaryData and "labState" and result.auxiliaryData or "labZip" in result.auxiliaryData):
            raise ValueError("All or no elements of lab address (street, city, state, zip) must be defined in auxiliary data")
        labAddress = observedResults.PerformingOrganizationLabAddress(
            result.auxiliaryData["labStreet"],
            result.auxiliaryData["labCity"],
            result.auxiliaryData["labState"],
            result.auxiliaryData["labZip"]
        )
    else:
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
    if "labName" in result.auxiliaryData:
        assignerName = result.auxiliaryData["labName"]
    else:
        assignerName = config.LabInfo.name
    specimenIDNumber = specimen.SpecimenIDNumber(
        result.specimenID,
        assignerName
    )
    if "labName" in result.auxiliaryData or "labCLIA" in result.auxiliaryData:
        if not ("labName" in result.auxiliaryData and "labCLIA" in result.auxiliaryData):
            raise ValueError("Lab name and lab CLIA must both be either present or absent in auxiliary data")
        fillerAssignedIdentifier = specimen.FillerAssignedIdentifier(
            "%s.%s" % (result.patientID, result.specimenID),
            result.auxiliaryData["labName"],
            result.auxiliaryData["labCLIA"],
            "CLIA"
        )
    else:
        fillerAssignedIdentifier = specimen.FillerAssignedIdentifier(
            "%s.%s" % (result.patientID, result.specimenID),
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
        result.collectionDateTime.year,
        result.collectionDateTime.month,
        result.collectionDateTime.day,
        result.collectionDateTime.hour,
        result.collectionDateTime.minute,
        result.collectionDateTime.second
    )
    specimenReceivedDateTime = specimen.SpecimenReceivedDateTime(
        result.receivedDateTime.year,
        result.receivedDateTime.month,
        result.receivedDateTime.day,
        result.receivedDateTime.hour,
        result.receivedDateTime.minute,
        result.receivedDateTime.second
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

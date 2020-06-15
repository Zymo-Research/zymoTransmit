import time

class LabInfo:
    name = ""
    phone = ""
    email = ""
    street = ""
    city = ""
    state = ""
    zip = ""
    country = "USA"
    clia = ""
    iso = ""
    gmt_offset = time.timezone/(60*60)


class LabDirectorInfo:
    firstName = ""
    lastName = ""
    middleName = ""
    prefix = ""
    suffix = ""
    professionalSuffix = ""
    phone = ""
    email = ""
    street = ""
    city = ""
    state = ""
    zip = ""
    country = "USA"
    identifier = ""
    assigningAuthority = "NPI"


class Connection:
    wsdlURL = "https://hiegateway.cdph.ca.gov/submit/CDPH_transfer.wsdl"
    submissionURL = 'https://hiegateway.cdph.ca.gov/submit/services/CDPH_transfer.CDPH_transferHttpsSoap12Endpoint'
    certificateFolder = "certificates"
    certificateFileName = "certificate.pem"
    userName = ""
    password = ""


class Configuration:
    productionReady = False
    logFolder = "transmissionLogs"
    class MSH:
        class SendingFacility:
            name = LabInfo.name
            id = LabInfo.clia
            idType = "CLIA"

        class ReceivingApplication:
            name = "CDPH CA REDIE"
            id = "2.16.840.1.114222.4.3.3.10.1.1"
            idType = "ISO"

        class ReceivingFacility:
            name = "CDPH_CID"
            id = "2.16.840.1.114222.4.1.214104"
            idType = "ISO"

        class MessageType:
            code = "ORU"
            triggerEvent = "R01"
            structure = "ORU_R01"

        class ProcessingID:
            testing = "T"
            production = "P"

        class MessageProfileIdentifier:
            entity = "PHLabReport-NoAck"
            nameSpace = ""
            universalID = "2.16.840.1.113883.9.10"
            idType = "ISO"

    class PID:
        class IDAssigner:
            name = LabInfo.name
            id = LabInfo.clia
            idType = "CLIA"

        class Facility:
            name = LabInfo.name
            id = LabInfo.clia
            idType = "CLIA"

class ResultTerms:
    positiveResultTerms = ["POSITIVE", "DETECTED", "POS"]
    indeterminateResultTerms = ["INDETERMINATE", "N/A", "UNKNOWN"]
    negativeResultTerms = ["ND", "NEG", "NEGATIVE"]
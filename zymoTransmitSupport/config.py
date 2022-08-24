import time
import pytz
import os
import re

trueRE = re.compile("true", re.IGNORECASE)
falseRE = re.compile("false", re.IGNORECASE)

def readConfigLine(line:str):
    line = line.strip()
    if not line:
        return False
    if line.startswith("#"):
        return False
    line = line.split(":")
    key = line[0]
    if len(line) > 1:
        value = ":".join(line[1:])
    else:
        value = ""
    value = value.strip()
    if value.lower() == "true":
        value = True
    elif value.lower() == "false":
        value = False
    return key, value


def readConfigurationFile(configurationPath:str=None):
    if not configurationPath:
        thisFolder = os.path.split(__file__)[0]
        containingFolder = os.path.split(thisFolder)[0]
        configurationPath = os.path.join(containingFolder, "config.txt")
    configDictBuild = {}
    configFile = open(configurationPath, 'r')
    for line in configFile:
        line = line.strip()
        if not line:
            continue
        keyValue = readConfigLine(line)
        if not keyValue:
            continue
        key, value = keyValue
        key = key.lower()
        if key in configDictBuild:
            raise RuntimeError("Got a duplicated value '%s' from configuration file. This is likely an error." %key)
        configDictBuild[key] = value
    configFile.close()
    return configDictBuild


configDict = readConfigurationFile()


class LabInfo:
    name = configDict.setdefault("lab name", "")
    phone = configDict.setdefault("lab phone", "")
    email = configDict.setdefault("lab email", "")
    street = configDict.setdefault("lab street", "")
    suite = configDict.setdefault("lab suite", "")
    city = configDict.setdefault("lab city", "")
    state = configDict.setdefault("lab state", "")
    zip = configDict.setdefault("lab zip", "")
    country = configDict.setdefault("lab country", "")
    clia = configDict.setdefault("lab clia id", "")
    iso = configDict.setdefault("lab iso", "")
    timezone = configDict.setdefault("timezone", "US/Pacific")


class LabDirectorInfo:
    firstName = configDict.setdefault("md first name", "")
    lastName = configDict.setdefault("md last name", "")
    middleName = configDict.setdefault("md middle name", "")
    prefix = configDict.setdefault("md prefix", "")
    suffix = configDict.setdefault("md personal suffix", "")
    professionalSuffix = configDict.setdefault("md professional suffix", "")
    phone = configDict.setdefault("md phone", "")
    email = configDict.setdefault("md email", "")
    street = configDict.setdefault("md street", "")
    city = configDict.setdefault("md city", "")
    state = configDict.setdefault("md state", "")
    zip = configDict.setdefault("md zip", "")
    country = configDict.setdefault("md country", "")
    identifier = configDict.setdefault("md identifier number", "")
    assigningAuthority = configDict.setdefault("md assigning authority", "")


class TestInformation:
    testID = configDict.setdefault("test id code", "")
    testDescription = configDict.setdefault("test description", "")
    testEquipmentID = configDict.setdefault("test equipment id", "")


class Connection:
    wsdlURL = configDict.setdefault("wsdl url", "")
    submissionURL = configDict.setdefault("submission url", "")
    certificateFolder = configDict.setdefault("certificate folder", "")
    certificateFileName = configDict.setdefault("certificate file name", "")
    userName = configDict.setdefault("gateway user", "")
    password = configDict.setdefault("gateway password", "")
    usingOptum = configDict.setdefault("using optum", True)
    localWSDLFolder = configDict.setdefault("local wsdl folder", "")
    optumTestingWSDL = configDict.setdefault("optum testing wsdl file", "")
    optumProductionWSDL = configDict.setdefault("optum production wsdl file", "")
    optumTestingCertificate = configDict.setdefault("optum testing certificate", "")
    optumTestingKey = configDict.setdefault("optum testing key", "")
    optumProductionCertificate = configDict.setdefault("optum production certificate", "")
    optumProductionKey = configDict.setdefault("optum production key", "")
    usingSaphire = configDict.setdefault("using saphire", False)
    saphireProductionURL = configDict.setdefault("saphire production url", "")
    saphireStagingURL = configDict.setdefault("saphire staging url", "")
    saphireProductionWSDLURL = configDict.setdefault("saphire production wsdl url", "")
    saphireStagingWSDLURL = configDict.setdefault("saphire staging wsdl url", "")
    saphireCertificate = configDict.setdefault("saphire certificate", "")
    saphireKey = configDict.setdefault("saphire key", "")


class Configuration:
    productionReady = not configDict.setdefault("in testing", True)
    logFolder = configDict.setdefault("log folder", "")
    class MSH:
        class SendingFacility:
            name = LabInfo.name
            id = LabInfo.clia
            idType = "CLIA"

        class ReceivingApplication:
            name = configDict.setdefault("receiver name", "")
            id = configDict.setdefault("receiver id", "")
            idType = configDict.setdefault("receiver id type", "")

        class ReceivingFacility:
            name = configDict.setdefault("receiving facility", "")
            id = configDict.setdefault("receiving facility id", "")
            idType = configDict.setdefault("receiving facility id type", "")

        class MessageType:
            code = configDict.setdefault("message type code", "")
            triggerEvent = configDict.setdefault("message trigger event", "")
            structure = configDict.setdefault("message structure", "")

        class ProcessingID:
            testing = configDict.setdefault("testing environment id", "")
            production = configDict.setdefault("production environment id", "")

        class MessageProfileIdentifier:
            entity = configDict.setdefault("message profile entity", "")
            nameSpace = configDict.setdefault("message profile namespace", "")
            universalID = configDict.setdefault("message profile universal id", "")
            idType = configDict.setdefault("message profile universal id type", "")

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
    positiveResultTerms = ["POSITIVE", "DETECTED", "POS", "260373001", "SARS-COV-2 NUCLEIC ACID DETECTED BY BDMAX", "POSITIVE SARS-COV-2", "DETECT", "REACTIVE", "DETECT", "2019-NCOV NUCLEIC ACID DETECTED BY GENEXPERT"]
    indeterminateResultTerms = ["INDETERMINATE", "N/A", "UNKNOWN", "INCONCLUSIVE", "INVALID", "419984006"]
    negativeResultTerms = ["ND", "NEG", "NEGATIVE", "NOT DETECTED", "260415000", "NOTDET", "NONE DETECTED", "NONREACTIVE", "NON-REACTIVE", "NOT_DETECTED", "COVID-19 (SARS-COV-2) RNA: NOT DETECTED"]
    unsatisfactorySpecimenResultTerms = ["UNSATISFACTORY SPECIMEN", "SPECIMEN UNSATISFACTORY", "UNSATISFACTORY", "125154007"]
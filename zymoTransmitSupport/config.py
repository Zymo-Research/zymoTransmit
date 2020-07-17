import time
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
    name = configDict["lab name"]
    phone = configDict["lab phone"]
    email = configDict["lab email"]
    street = configDict["lab street"]
    city = configDict["lab city"]
    state = configDict["lab state"]
    zip = configDict["lab zip"]
    country = configDict["lab country"]
    clia = configDict["lab clia id"]
    iso = configDict["lab iso"]
    gmt_offset = time.timezone/(60*60)


class LabDirectorInfo:
    firstName = configDict["md first name"]
    lastName = configDict["md last name"]
    middleName = configDict["md middle name"]
    prefix = configDict["md prefix"]
    suffix = configDict["md personal suffix"]
    professionalSuffix = configDict["md professional suffix"]
    phone = configDict["md phone"]
    email = configDict["md email"]
    street = configDict["md street"]
    city = configDict["md city"]
    state = configDict["md state"]
    zip = configDict["md zip"]
    country = configDict["md country"]
    identifier = configDict["md identifier number"]
    assigningAuthority = configDict["md assigning authority"]


class Connection:
    wsdlURL = configDict["wsdl url"]
    submissionURL = configDict["submission url"]
    certificateFolder = configDict["certificate folder"]
    certificateFileName = configDict["certificate file name"]
    userName = configDict["gateway user"]
    password = configDict["gateway password"]


class Configuration:
    productionReady = not configDict["in testing"]
    logFolder = configDict["log folder"]
    class MSH:
        class SendingFacility:
            name = LabInfo.name
            id = LabInfo.clia
            idType = "CLIA"

        class ReceivingApplication:
            name = configDict["receiver name"]
            id = configDict["receiver id"]
            idType = configDict["receiver id type"]

        class ReceivingFacility:
            name = configDict["receiving facility"]
            id = configDict["receiving facility id"]
            idType = configDict["receiving facility id type"]

        class MessageType:
            code = configDict["message type code"]
            triggerEvent = configDict["message trigger event"]
            structure = configDict["message structure"]

        class ProcessingID:
            testing = configDict["testing environment id"]
            production = configDict["production environment id"]

        class MessageProfileIdentifier:
            entity = configDict["message profile entity"]
            nameSpace = configDict["message profile namespace"]
            universalID = configDict["message profile universal id"]
            idType = configDict["message profile universal id type"]

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
    indeterminateResultTerms = ["INDETERMINATE", "N/A", "UNKNOWN", "INCONCLUSIVE", "INVALID"]
    negativeResultTerms = ["ND", "NEG", "NEGATIVE", "NOT DETECTED"]
    unsatisfactorySpecimenResultTerms = ["UNSATISFACTORY SPECIMEN", "SPECIMEN UNSATISFACTORY", "UNSATISFACTORY"]
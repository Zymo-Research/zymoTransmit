import zeep
from .. import config as defaultConfig
from . import resultReader
import typing

config = defaultConfig

class SubmissionStatus:

    def __init__(self, patientID:str, specimenID:str, successfullyTransmitted:[bool, None], notes:str):
        self.patientID = patientID
        self.specimenID = specimenID
        self.success = successfullyTransmitted
        self.notes = notes

    def logList(self):
        logList = [self.patientID, self.specimenID]
        if self.success:
            logList.append("Success")
        elif self.success is None:
            logList.append("ERROR")
        else:
            logList.append("REJECTED")
        noteLines = self.notes.split("\n")
        for line in noteLines:
            logList.append(line.strip())
        return logList

    def __str__(self):
        outputLines = []
        if self.success:
            statusStatement = "Successfully transmitted"
        elif self.success is None:
            statusStatement = "TRANSMISSION ERROR"
        else:
            statusStatement = "TRANSMISSION FAILED"
        firstLine = "%s:%s - %s" %(self.patientID, self.specimenID, statusStatement)
        outputLines.append(firstLine)
        if self.notes:
            outputLines.append("\t%s" %self.notes)
        outputBlock = "\n".join(outputLines)
        return outputBlock


def transmitBlocks(client:zeep.Client, hl7Blocks:dict, resultList:typing.List[resultReader.TestResult]=None):
    def makeResultKey():
        resultKey = {}
        for index, result in enumerate(resultList):
            key = (result.patientID, result.specimenID)
            resultKey[key] = index
        return resultKey
    if resultList is None:
        resultKey = {}
    else:
        resultKey = makeResultKey()
    client.raw_response = True
    submissionResults = []
    if config.Configuration.productionReady:
        productionCode = config.Configuration.MSH.ProcessingID.production
    else:
        productionCode = config.Configuration.MSH.ProcessingID.testing
    for resultID, text in hl7Blocks.items():
        patientID, specimenID = resultID
        try:
            response = client.service.submitMessage(
                userid = config.Connection.userName,
                password = config.Connection.password,
                dataownerid = config.Connection.userName,
                cdphprogramid = 1,
                cdphprogramenvironment = productionCode,
                action = "SEND",
                messagecontent = "<![CDATA[%s]]" %text
            )
        except Exception as err:
            submissionStatus = SubmissionStatus(patientID, specimenID, None, str(err))
            print("ERROR: attempted to submit %s:%s, but it failed to return an error. See submission log for more details." %(patientID, specimenID))
            if resultID in resultKey:
                resultList[resultKey[resultID]].transmittedSuccessfully = False
                resultList[resultKey[resultID]].reasonForFailedTransmission.append("Gateway failed to respond. This is likely a gateway issue and may self-resolve if given some time.")
        else:
            if response.status == "VALID":
                submissionStatus = SubmissionStatus(patientID, specimenID, True, getattr(response, "return"))
                print("Successfully submitted %s:%s" %(patientID, specimenID))
                if resultID in resultKey:
                    resultList[resultKey[resultID]].transmittedSuccessfully = True
            else:
                submissionStatus = SubmissionStatus(patientID, specimenID, False, getattr(response, "return"))
                print("ERROR: attempted to submit %s:%s, but it was rejected. See submission log for more details." %(patientID, specimenID))
                if resultID in resultKey:
                    resultList[resultKey[resultID]].transmittedSuccessfully = False
                    resultList[resultKey[resultID]].reasonForFailedTransmission.append("Gateway rejected transmission. This indicates a likely error in the data and requires some correction before attempting to transmit again. See the log file for specific errors.")
        submissionResults.append(submissionStatus)
    return submissionResults
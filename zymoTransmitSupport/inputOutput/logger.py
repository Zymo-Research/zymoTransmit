import datetime
from . import soapAPI
import typing
import os

columns = ["#Accession", "Status", "Notes"]


def timeStamp():
    currentTime = datetime.datetime.now()
    timeList = [currentTime.year, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second]
    timeList = [str(item).zfill(2) for item in timeList]
    return "".join(timeList)


def makeNoteBlock(submissionResults:typing.List[soapAPI.SubmissionStatus], delimiter: str = "\t"):
    headerString = delimiter.join(columns)
    resultLines = [headerString]
    for result in submissionResults:
        lineString = delimiter.join(result.logList())
        resultLines.append(lineString)
    return "\n".join(resultLines)


def writeLogFile(logFolder:str, submissionResults: typing.List[soapAPI.SubmissionStatus], resultText: str):
    timeIdentifier = timeStamp()
    logFileName = "submissionLog%s.txt" % timeIdentifier
    resultFileName = "resultText%s.hl7" % timeIdentifier
    filePath = os.path.join(logFolder, logFileName)
    outputText = makeNoteBlock(submissionResults)
    outputFile = open(filePath, 'w')
    outputFile.write(outputText)
    outputFile.close()
    filePath = os.path.join(logFolder, resultFileName)
    outputFile = open(filePath, 'w', encoding="utf-8")
    outputFile.write(resultText)
    outputFile.close()
    return outputText

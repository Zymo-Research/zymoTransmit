import datetime
from . import soapAPI
import typing
import os

columns = ["#Patient", "Specimen", "Status", "Notes"]


def timeStamp():
    currentTime = datetime.datetime.now()
    timeList = [currentTime.year, currentTime.month, currentTime.day, currentTime.hour, currentTime.minute, currentTime.second]
    timeList = [str(item).zfill(2) for item in timeList]
    return "".join(timeList)


def makeNoteBlock(submissionResults:typing.List[soapAPI.SubmissionStatus], delimiter:str="\t"):
    headerString = delimiter.join(columns)
    resultLines = [headerString]
    for result in submissionResults:
        lineString = delimiter.join(result.logList())
        resultLines.append(lineString)
    return "\n".join(resultLines)

def writeLogFile(logFolder:str, submissionResults:typing.List[soapAPI.SubmissionStatus]):
    logFileName = "submissionLog%s.txt" %(timeStamp())
    filePath = os.path.join(logFolder, logFileName)
    outputText = makeNoteBlock(submissionResults)
    outputFile = open(filePath, 'w')
    outputFile.write(outputText)
    outputFile.close()
    return outputText

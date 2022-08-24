from .. import config as defaultConfig
import requests
import os
import uuid

config = defaultConfig

def lowLevelBlockTransmitter(session:requests.Session, hl7Blocks:dict):
    headers = {'SOAPAction': '"urn:cdc:iisb:2011:submitMessage"',
     'Content-Type': 'application/soap+xml; charset=utf-8; action="urn:cdc:iisb:2011:submitMessage"'}
    certificateFile = os.path.join(config.Connection.certificateFolder, config.Connection.certificateFileName)
    if config.Configuration.productionReady:
        productionCode = config.Configuration.MSH.ProcessingID.production
    else:
        productionCode = config.Configuration.MSH.ProcessingID.testing
    for patientID, text in hl7Blocks.items():
        fillers = (
            config.Connection.userName,
            config.Connection.password,
            config.Connection.userName,
            1,
            productionCode,
            "SEND",
            text
        )
        message = '\
            <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:urn="urn:cdc:iisb:2011">\
            <soap:Header/>\
            <soap:Body>\
            <urn:submitMessage>\
            <urn:userid>%s</urn:userid>\
            <urn:password>%s</urn:password>\
            <urn:dataownerid>%s</urn:dataownerid>\
            <urn:cdphprogramid>%s</urn:cdphprogramid>\
            <urn:cdphprogramenvironment>%s</urn:cdphprogramenvironment >\
            <urn:action >%s</urn:action >\
            <urn:messagecontent ><![CDATA[%s]]></urn:messagecontent >\
            </urn:submitMessage>\
            </soap:Body>\
            </soap:Envelope>' %fillers
        message = message.replace("    ", "")
        if config.Connection.usingSaphire:
            if config.Configuration.productionReady:
                submissionURL = config.Connection.saphireProductionURL
            else:
                submissionURL = config.Connection.saphireStagingURL
        elif config.Connection.usingOptum:
            submissionURL = config.Connection.submissionURL
        request = requests.Request("POST", submissionURL, data=message)
        preparedRequest = request.prepare()
        testResp = requests.get(config.Connection.wsdlURL, cert=certificateFile)
        response = session.send(preparedRequest, cert=certificateFile)
        print(response.text)
        print("Processed %s" %patientID)
    return True


def lowLevelBlockTransmitter2(session:requests.Session, hl7Blocks:dict):
    headers = {'SOAPAction': '"urn:cdc:iisb:2011:submitMessage"',
     'Content-Type': 'application/soap+xml; charset=utf-8; action="urn:cdc:iisb:2011:submitMessage"'}
    certificateFile = os.path.join(config.Connection.certificateFolder, config.Connection.certificateFileName)
    if config.Configuration.productionReady:
        productionCode = config.Configuration.MSH.ProcessingID.production
    else:
        productionCode = config.Configuration.MSH.ProcessingID.testing
    for patientID, text in hl7Blocks.items():
        fillers = (
            uuid.uuid1(),
            config.Connection.userName,
            config.Connection.password,
            config.Connection.userName,
            1,
            productionCode,
            "SEND",
            text
        )
        message = '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<soap-env:Envelope xmlns:soap-env="http://www.w3.org/2003/05/soap-envelope"><soap-env:Header xmlns:wsa="http://www.w3.org/2005/08/addressing"><wsa:Action>urn:cdc:iisb:2011:submitMessage</wsa:Action><wsa:MessageID>urn:uuid:%s3</wsa:MessageID><wsa:To>https://hiegateway.cdph.ca.gov/submit/services/CDPH_transfer.CDPH_transferHttpsSoap12Endpoint</wsa:To></soap-env:Header><soap-env:Body><ns0:submitMessage xmlns:ns0="urn:cdc:iisb:2011"><ns0:userid>%s</ns0:userid><ns0:password>%s</ns0:password><ns0:dataownerid>%s</ns0:dataownerid><ns0:cdphprogramid>%s</ns0:cdphprogramid><ns0:cdphprogramenvironment>%s</ns0:cdphprogramenvironment><ns0:action>%s</ns0:action><ns0:messagecontent></ns0:messagecontent><![CDATA[%s]]></ns0:submitMessage></soap-env:Body></soap-env:Envelope>' %fillers
        message = message.replace("&","&amp;")
        request = requests.Request("POST", config.Connection.submissionURL, headers=headers, data=message)
        preparedRequest = request.prepare()
        testResp = requests.get(config.Connection.wsdlURL, cert=certificateFile)
        response = session.send(preparedRequest, cert=certificateFile)
        #response = requests.post("http://www.dynadot.com", data = message, proxies={'http': 'http://127.0.0.1:8080'})
        print(response.text)
        print("Processed %s" %patientID)
    return True

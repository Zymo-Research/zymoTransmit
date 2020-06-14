import requests
import os
import zeep


def getSOAPClient(wsdlURL:str, clientCertificatePath:str=None, dumpClientInfo:bool=False, testOnly:bool=False):
    session = requests.Session()
    if clientCertificatePath:
        if not os.path.isfile(clientCertificatePath):
            raise FileNotFoundError("Unable to find client certificate path at %s" %clientCertificatePath)
        session.cert = clientCertificatePath
    transport = zeep.transports.Transport(session=session)
    client = zeep.Client(wsdlURL, transport=transport)
    #testUpload = client.service.connectivityTest("ping")
    if testOnly or dumpClientInfo:
        print("Server returned:")
        client.wsdl.dump()
        if testOnly:
            quit()
    return client, session
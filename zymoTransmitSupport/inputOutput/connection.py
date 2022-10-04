import xml.etree.ElementTree

import lxml.etree
import requests
import os
import zeep
import ssl
import requests.adapters
import requests.packages.urllib3
from xml import etree

strongSSLCipherSuiteEnforcement = True
permittedCipherSuites = 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256'
defaultSSLRules = (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1)


class TLSEnforcer(requests.adapters.HTTPAdapter):
    def __init__(self, sslRules=defaultSSLRules, **kwargs):
        self.sslRules = sslRules
        super(TLSEnforcer, self).__init__(**kwargs)

    def init_poolmanager(self, *pool_args, **pool_kwargs):
        sslSettings = requests.packages.urllib3.util.ssl_.create_urllib3_context(ciphers=permittedCipherSuites, cert_reqs=ssl.CERT_REQUIRED, options=self.sslRules)
        self.poolmanager = requests.packages.urllib3.poolmanager.PoolManager(*pool_args, ssl_context=sslSettings, **pool_kwargs)


class RawCdataSender(zeep.Transport):

    def post_xml(self, address, envelope, headers):
        message = xml.etree.ElementTree.tostring(envelope, encoding="unicode")
        message = message.replace("&lt;", "<")
        message = message.replace("&gt;", ">")
        message = message.replace("&amp;", "&")
        return self.post(address, message, headers)



def getSOAPClient(wsdlURL:str, clientCertificatePath:str=None, dumpClientInfo:bool=False, testOnly:bool=False):
    session = requests.Session()
    if strongSSLCipherSuiteEnforcement:
        session.mount("https://", adapter=TLSEnforcer())
    if clientCertificatePath:
        if type(clientCertificatePath) == str:
            if not os.path.isfile(clientCertificatePath):
                raise FileNotFoundError("Unable to find client certificate path at %s" %clientCertificatePath)
        else:
            if type(clientCertificatePath) in [tuple, list]:
                if len(clientCertificatePath) == 3:
                    certPath, keyPath, certChain = clientCertificatePath
                    clientCertificatePath = certPath, keyPath
                    if not os.path.isfile(certChain):
                        raise FileNotFoundError("Unable to find local certificate chain at %s" %certChain)
                    session.verify = certChain
                elif len(clientCertificatePath) == 2:
                    certPath, keyPath = clientCertificatePath
                else:
                    raise ValueError("List/tuple certificate paths should have exactly two or three elements with the first being the certificate and second being key. The third may be a cert chain if needed.")
                if not os.path.isfile(certPath) or not os.path.isfile(keyPath):
                    raise FileNotFoundError("Unable to find client certificate and/or key path.\nCert: %s\nKey: %s" %(certPath, keyPath))
        session.cert = clientCertificatePath
    transport = zeep.transports.Transport(session=session, timeout=30)
    try:
        #client = zeep.Client(wsdlURL, transport=transport)
        client = zeep.Client("file://C:/Users/mweinstein/PycharmProjects/zymoTransmit/wsdl/saphire_soap_wsdl.xml", transport=RawCdataSender(session=session, timeout=30))
    except OSError:
        wsdlURL = wsdlURL.replace("file:///", "file://")  # Seems like a weird quirk on windows where it wants to add a root / to the URI.  Might be a bug somewhere I need to report.  Actually, fixed in the latest zeep major release.
        client = zeep.Client(wsdlURL, transport=transport)
    #testUpload = client.service.connectivityTest("ping")
    if testOnly or dumpClientInfo:
        print("Server returned:")
        client.wsdl.dump()
        if testOnly:
            input("Press ENTER key to quit.")
            quit()
    return client, session

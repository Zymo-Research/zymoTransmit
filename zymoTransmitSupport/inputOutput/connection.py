import requests
import os
import zeep
import ssl
import requests.adapters
import requests.packages.urllib3

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



def getSOAPClient(wsdlURL:str, clientCertificatePath:str=None, dumpClientInfo:bool=False, testOnly:bool=False):
    session = requests.Session()
    if strongSSLCipherSuiteEnforcement:
        session.mount("https://", adapter=TLSEnforcer())
    if clientCertificatePath:
        if not os.path.isfile(clientCertificatePath):
            raise FileNotFoundError("Unable to find client certificate path at %s" %clientCertificatePath)
        session.cert = clientCertificatePath
    transport = zeep.transports.Transport(session=session, timeout=30)
    client = zeep.Client(wsdlURL, transport=transport)
    #testUpload = client.service.connectivityTest("ping")
    if testOnly or dumpClientInfo:
        print("Server returned:")
        client.wsdl.dump()
        if testOnly:
            input("Press ENTER key to quit.")
            quit()
    return client, session
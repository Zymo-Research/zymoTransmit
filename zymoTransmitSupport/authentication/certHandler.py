import os
import OpenSSL
import getpass


def convertPFX(pfxPath:str, outputDirectory:str, pfxPassword:str=None):
    defaultOutputFileName = "certificate.pem"
    if not os.path.isfile(pfxPath):
        raise FileNotFoundError("Unable to find PFX file at %s" %pfxPath)
    defaultFilePath = os.path.join(outputDirectory, defaultOutputFileName)
    if not os.path.isfile(defaultFilePath) or os.path.getsize(defaultFilePath) == 0:
        outputFileName = defaultOutputFileName
    else:
        pfxFileName = os.path.split(pfxPath)[1]
        outputFileName = ".".join(pfxFileName.split(".")[:-1]) + ".pem"
    outputPath = os.path.join(outputDirectory, outputFileName)
    outputFile = open(outputPath, 'wb')
    pfxStream = open(pfxPath, 'rb').read()
    if not pfxPassword:
        try:
            p12Load = OpenSSL.crypto.load_pkcs12(pfxStream)
        except OpenSSL.crypto.Error:
            pfxPassword = getpass.getpass("%s may be password protected.\nPassword: " %pfxPath)
            if not pfxPassword:
                quit("No password supplied")
            p12Load = OpenSSL.crypto.load_pkcs12(pfxStream, pfxPassword)
    else:
        p12Load = OpenSSL.crypto.load_pkcs12(pfxStream, pfxPassword)
    outputFile.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12Load.get_privatekey()))
    outputFile.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12Load.get_certificate()))
    ca = p12Load.get_ca_certificates()
    if ca:
        for caCert in ca:
            outputFile.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, caCert))
    outputFile.close()
    return outputPath




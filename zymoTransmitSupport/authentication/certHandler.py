import os
import re
import cryptography.x509
import cryptography.hazmat.backends
import cryptography.hazmat.primitives.serialization
import OpenSSL
import getpass

certStart = "-----BEGIN CERTIFICATE-----"
certEnd = "-----END CERTIFICATE-----"


def extractWholeCerts(path:str):
    if not os.path.isfile(path):
        raise FileNotFoundError("Unable to find file %s" %path)
    certText = open(path).read()
    certSplits = re.split("-+?END CERTIFICATE-+?", certText)
    certSplits = [certSplit.strip() for certSplit in certSplits if certSplit]
    return certSplits


def readCert(certBytes:[bytes, str], returnFalseOnFailure:bool=False):
    if type(certBytes) == bytes:
        pass
    elif type(certBytes) == str:
        certBytes = certBytes.encode()
    else:
        raise TypeError("Certificate bytes value should be passed in as bytes type (although string may work as well)")
    if not returnFalseOnFailure:
        try:
            cert = cryptography.x509.load_pem_x509_certificate(certBytes, cryptography.hazmat.backends.default_backend())
        except IndexError:
            cert = cryptography.x509.load_der_x509_certificate(certBytes, cryptography.hazmat.backends.default_backend())
        return cert
    else:
        try:
            try:
                cert = cryptography.x509.load_pem_x509_certificate(certBytes, cryptography.hazmat.backends.default_backend())
            except ValueError:
                cert = cryptography.x509.load_der_x509_certificate(certBytes, cryptography.hazmat.backends.default_backend())
            return cert
        except:
            return False



def readCertCollection(path:str):
    wholeCerts = extractWholeCerts(path)
    wholeCerts = [wholeCert.strip().encode() for wholeCert in wholeCerts if wholeCert]
    certCollection = []
    for cert in wholeCerts:
        certCollection.append(readCert(cert))
    return certCollection


def getNewCertsFromFiles(directory:str, certCollectionFile:str="cacert.pem"):
    if not os.path.isdir(directory):
        raise NotADirectoryError("Certificate directory %s was not found or is not a directory." %directory)
    files = os.listdir(directory)
    certCollection = {}
    for file in files:
        if file == certCollectionFile:
            continue
        fullPath = os.path.join(directory, file)
        if not os.path.isfile(fullPath):
            continue
        try:
            data = open(fullPath).read()
            data = data.encode()
        except UnicodeDecodeError:
            data = open(fullPath, 'rb').read()
        cert = readCert(data, returnFalseOnFailure=True)
        if not cert:
            continue
        certCollection[file] = cert
    return certCollection


def manageCertCollection(directory:str, certCollectionFile:str="cacert.pem"):
    if not os.path.isdir(directory):
        raise NotADirectoryError("Certificate directory %s was not found or is not a directory." % directory)
    certCollectionPath = os.path.join(directory, certCollectionFile)
    newCerts = getNewCertsFromFiles(directory, certCollectionFile)
    if not newCerts:
        if not os.path.isfile(certCollectionPath):
            raise FileNotFoundError("Unable to find certificate collection file at %s" %certCollectionPath)
        return False
    if os.path.isfile(certCollectionPath):
        existingCerts = readCertCollection(certCollectionPath)
    else:
        existingCerts = []
    serialNumbers = [cert.serial_number for cert in existingCerts]
    certsToAdd = []
    certFileNamesAdded = []
    for certFile, cert in newCerts.items():
        if cert.serial_number in serialNumbers:
            continue
        certsToAdd.append(cert)
        print("Adding certificate from %s to certificate collection." %certFile)
        certFileNamesAdded.append(certFile)
    if not certsToAdd:
        return False
    for cert in certsToAdd:
        existingCerts.append(cert)
    output = open(certCollectionPath, 'wb')
    for cert in existingCerts:
        #output.write("\n".encode())
        output.write(cert.public_bytes(cryptography.hazmat.primitives.serialization.Encoding.PEM))
        #output.write("\n".encode())
        #output.write(certEnd.encode())
    output.close()
    print("New certificate collection written")
    return certFileNamesAdded


def convertPFX(pfxPath:str, outputDirectory:str, pfxPassword:str=None):
    defaultOutputFileName = "certificate.pem"
    if not os.path.isfile(pfxPath):
        raise FileNotFoundError("Unable to find PFX file at %s" %pfxPath)
    defaultFilePath = os.path.join(outputDirectory, defaultOutputFileName)
    if not os.path.isfile(defaultFilePath):
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




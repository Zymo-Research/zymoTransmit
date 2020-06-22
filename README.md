# Zymo Research Transmit: Simple Public Health Data Transmission

We are honored to be playing an important role in the response to COVID-19.  To assist with that, we have chosen to make this program available as free, open-source software for all to use with our support.  Please contact us if you require assistance with this software or other portions of your pipeline ranging from sample collection and preservation to viral RNA extraction, detection, or analysis.  We have experts in high-throughput laboratory automation ready to help you scale-up as well.

     Be quick, but don't hurry.
                                 – John Wooden

At Zymo Research, our vision is, "*To have a positive impact in the biomedical field and to contribute to the greater good of humanity*," and it is with this vision guiding our efforts that we offer you this software package.


#### Publication
At present, there is not publication planned for this software.  If anybody in the public health field wishes to collaborate on one, please contact us.

## Quick Start Guide

This guide already assumes you have Python 3.6 or later installed on your system and available from the command line.
If your operating system is Windows, your commands will start with "python" as seen below.
If your OS is Mac or Linux, you will need to start with "python3" instead of "python"


#### Downloading and setting up the program

* You will need to download this program from Github.  If you know how to do this via command line git commands, please use those.
* Otherwise, you will need to click the download link above and download as a zip file.
* Once that is complete, you will want to extract the files to the desired folder.
* With the files extracted, open a command prompt go into the directory containing the zymoTransmit program, you should see a file called "zymoTransmit.py"
* Copy your health department-supplied certificate file (ending in .pfx) to this directory

Install required python packages on Windows:
```
pip install -r requirements.txt
```
Install the required python packages on MacOS or Linux:
```
pip3 install -r requirements.txt
```
Set up your config file and required folders (don't forget to put in userID and password from the document sent by the health department). A file editor window will appear to help with this if GUI functionality is available.

***Remember to save before exiting***

If you need to edit this file in the future, it can be found at ```zymoTransmit/zymoTransmitSupport/config.py``` 
```
python zymoTransmit.py
```
Convert your certificate for use (if you do not supply a file name, a file browser window will appear if GUI functionality is available)
```
python zymoTransmit.py -c [fileName.pfx]
```
Test your connection
```
python zymoTransmit.py -t
```
If the connection worked, you should see something similar to:
```
Server returned:

Prefixes:
     xsd: http://www.w3.org/2001/XMLSchema
     ns0: urn:cdc:iisb:2011

Global elements:

     ns0:MessageTooLargeFault(ns0:MessageTooLargeFaultType)
     ns0:SecurityFault(ns0:SecurityFaultType)
     ns0:UnsupportedOperationFault(ns0:UnsupportedOperationFaultType)
     ns0:connectivityTest(ns0:connectivityTestRequestType)
     ns0:connectivityTestResponse(ns0:connectivityTestResponseType)
     ns0:fault(ns0:soapFaultType)
     ns0:submitMessage(ns0:submitMessageRequestType)
     ns0:submitMessageResponse(ns0:submitMessageResponseType)
...
```
If you see an exception, please check your Internet connection and try again or reach out for support.  

If this works, you are ready to transmit!


#### Preparing a report
The program should have come packaged with a file called ```templateSubmission.txt``` this tab-delimited text file will open in Microsoft Excel and can help you start putting together reports for submission.  Please try to fill in all fields if possible to avoid having submissions rejected for missing data.  Fields that can accept telephone numbers can also accept emails if that is the preferred method of contact for the patient or provider.  

To find out an appropriate LOINC code to describe your test:
```
python zymoTransmit.py -l
```
To find out an appropriate SNOMED code to describe your specimen:
```
python zymoTransmit.py -s
```
There are several codes related to SARS-CoV-2 testing available, so please look carefully for the one that most closely describes your test method and sample.


#### Transmitting results
Once a report has been filled out correctly, submitting reports requires a simple command:
```
python zymoTransmit.py [reportName.txt]
```
Use the file name for your report in place of the bracketed text above. 

If you are unsure how to find the file, leave it blank and a file browser window will open on your screen to help you find it if GUI functionality is available.

#### Command line arguments
Commands are formulated as follows:
```
python zymoTransmit.py [argument] [filename if needed]
```

| Long Name        | Short Name           | Notes  
| --------------- |:--------------:|:--------|
--help	|	-h	|	Displays a list of arguments 
--convertCertificate	|	-c	|	Loads and converts a certificate. Requires a file and will prompt for one if missing. May ask for certificate password.
--editConfig	|	-e	|	Edit the configuration file.  ***Remember to save and exit with done***
--testConnection	|	-t	|	Tests the connection to the health department, run as a final step of setup
--snomed	|	-s	|	Display relevant SNOMED codes for specimen types
--loinc	|	-l	|	Display relevant LOINC codes for testing types


## OUTPUT
All outputs will be written to the designated output folder for the container, which will unmount upon completion of the run.

There will be two primary output files, one report in HTML format and one in JSON format.  Examples of these can be seen [here for HTML](https://github.com/Zymo-Research/miqScoreShotgunPublic/blob/master/exampleReport.html) and [here for JSON](https://github.com/Zymo-Research/miqScoreShotgunPublic/blob/master/exampleReport.json).  The HTML report is designed to be viewed in a browser and gives an overview of the results for the sample.  The JSON report, while human-readable, is designed primarily to facilitate analysis using an automated script.  It also provides much more detailed information on the results than the HTML report.  
In addition to the two primary files, there will be a log file that can be used in the event of a problem with analysis for additional information on the run.  Finally, there will be several files generated by the DADA2 pipeline.  If you are familiar with DADA2, you will be familiar with these outputs.

## Contributing

We welcome and encourage contributions to this project from the microbiomics community and will happily accept and acknowledge input (and possibly provide some free kits as a thank you).  We aim to provide a positive and inclusive environment for contributors that is free of any harassment or excessively harsh criticism. Our Golden Rule: *Treat others as you would like to be treated*.

## Versioning

We use a modification of [Semantic Versioning](https://semvar.org) to identify our releases.

Release identifiers will be *major.minor.patch*

Major release: Newly required parameter or other change that is not entirely backwards compatible
Minor release: New optional parameter
Patch release: No changes to parameters

## Authors

- **Michael M. Weinstein** - *Project Lead, Programming and Design* - [michael-weinstein](https://github.com/michael-weinstein)
 - For support, please contact mweinstein -atSymbol- zymoresearch.com or call us at (949) 679-1190 

See also the list of [contributors](https://github.com/Zymo-Research/zymoTransmit/contributors) who participated in this project.

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE](https://github.com/Zymo-Research/zymoTransmit/blob/master/LICENSE) file for details.
This license restricts the usage of this application for non-open sourced systems. Please contact the authors for questions related to relicensing of this software in non-open sourced systems.

## Acknowledgments

We would like to thank the following, without whom this would not have happened:
* The Python Foundation
* The staff at Zymo Research
* Pangea Laboratory
* The California Department of Public Health
* Our customers

---------------------------------------------------------------------------------------------------------------------

#### If you like this software, please let us know at info@zymoresearch.com.
#### Please support our continued development of free and open-source microbiomics and other applications by checking out the latest COVID-19 related offerings at [Zymo Research](https://www.zymoresearch.com/pages/covid-19-efforts) and our latest microbiomics offerings from [ZymoBIOMICS](https://www.zymoresearch.com/pages/zymobiomics-portfolio).

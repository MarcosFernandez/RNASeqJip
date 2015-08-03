#!/usr/bin/env python

import os
import json
import argparse
import sys
import re

class CreateDocumentationFiles(object):
    """Class which manages documentation builder"""

    def __init__(self):
        self.file_duplicates = []               #Vector of files from samtools flagstats output
        self.sampleLibDuplicates = []           #Vector of vector of stats each item: [sample,library,percen_duplication]   
        self.jsonDictionary = {}                #Dictionary to be printed as a json file  
        self.cssContents = []                   #Css Vector of contents
        self.cssHtml = []                       #HTML Vector of contents


    def register_parameters(self, parser):
        """Register script parameters with given
        argparse parser
        parser -- the argparse parser
        """
        general_group = parser.add_argument_group('Create HTML and JSON Duplicates Report')
        general_group.add_argument('--dup_stats', dest="files", nargs="+", help='Files of duplicates statistics from markdup sambamba. \
                                                                                  One per sample an library. Example  sample_1.library_1.rmdup.stats sample_1.library_2.rmdup.stats sample_2.library_1.rmdup.stats')

    def parseArguments(self,args):
        """ Parse arguments """
        self.file_duplicates = args.files
 

    def parserStatsFiles(self):
        """ Parser duplicates stats to vectors structures """


        for statsFile in self.file_duplicates:
            fieldsName = os.path.basename(statsFile).split('.')
            sample = fieldsName[0]
            library = fieldsName[1]
            total_reads = 0
            duplicates = 0
            mapped = 0
            properly_paired = 0
            inproper_pairs = 0
            
            #1. PARSE DUPLICATES FILE
            processLine = False        
            
            with open(statsFile, "r") as stFile:
                row = 0    
                for line in stFile:
                    vFields = re.split(' ',line.rstrip('\n'))
                   
                    if row == 0:
                        total_reads = int(vFields[0])
                    elif row == 1:
                        duplicates = int(vFields[0])
                    elif row == 2:
                        mapped = int(vFields[0])
                    elif row == 6:
                        properly_paired = int(vFields[0])
                    elif row == 7:
                        inproper_pairs = int(vFields[0]) - properly_paired
                       
                    row += 1
                    
            #2. APPEND TO GLOBAL VECTOR
            self.sampleLibDuplicates.append([sample,library,[total_reads,duplicates,mapped,properly_paired,inproper_pairs]])
            keyName = sample + "_" + library
            
            self.jsonDictionary[keyName] =  { 'sample' : sample,
                                              'library' : library,
                                              'total_reads' : total_reads,
                                              'duplicates_reads' : duplicates,
                                              'percent_duplicates' : (float(duplicates) / float(total_reads)) * 100,
                                              'mapped_reads' : mapped,
                                              'percent_mapped' : (float(mapped) / float(total_reads)) * 100,
                                              'properly_paired' : properly_paired,
                                              'percent_properly_paired' : (float(properly_paired) / float(total_reads)) * 100,
                                              'inproper_pairs' : inproper_pairs,
                                              'percent_inproper_pairs' : (float(inproper_pairs) / float(total_reads)) * 100
                                            }

    def check_parameters(self):
        """Check parameters consistency
        args -- set of parsed arguments
        return True if everithing is ok, otherwise false"""        

        if len(self.file_duplicates) == 0:
            print "No input files found. Please check --dup_stats parameter"
            return False
        
        return True       



    def buildStyleSheet(self):
        ''' Add HTML header to a given vector '''
        self.cssContents.append(" #title\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("   font-size: 20px;\n")
        self.cssContents.append("   text-align: center;\n")
        self.cssContents.append("   color: #039;\n")
        self.cssContents.append("   border-collapse: collapse;\n")
        self.cssContents.append(" }\n")
        self.cssContents.append(" #section\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("   font-size: 18px;\n")
        self.cssContents.append("   text-align: center;\n")
        self.cssContents.append("   color: #039;\n")
        self.cssContents.append("   border-collapse: collapse;\n")
        self.cssContents.append(" }\n")
        #LINKS TABLE
        self.cssContents.append("#linksTable-b\n")
        self.cssContents.append("{\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("	font-size: 12px;\n")
        self.cssContents.append("	background: #fff;\n")
        self.cssContents.append("	margin: 5px;\n")
        self.cssContents.append("	width: 200px;\n")
        self.cssContents.append("	border-collapse: collapse;\n")
        self.cssContents.append("	text-align: left;\n")
        self.cssContents.append("}\n")
        self.cssContents.append("#linksTable-b th\n")
        self.cssContents.append("{\n")
        self.cssContents.append("	font-size: 14px;\n")
        self.cssContents.append("	font-weight: normal;\n")
        self.cssContents.append("	color: #039;\n")
        self.cssContents.append("	padding: 10px 8px;\n")
        self.cssContents.append("	border-bottom: 2px solid #6678b1;\n")
        self.cssContents.append("}\n")
        self.cssContents.append("#linksTable-b td\n")
        self.cssContents.append("{\n")
        self.cssContents.append("	border-bottom: 1px solid #ccc;\n")
        self.cssContents.append("	color: #669;\n")
        self.cssContents.append("	padding: 6px 8px;\n")
        self.cssContents.append("}\n")
        self.cssContents.append("linksTable-b tbody tr:hover td\n")
        self.cssContents.append("{\n")
        self.cssContents.append("	color: #009;\n")
        self.cssContents.append("}\n")
        #BLUE TABLE
        self.cssContents.append(" #hor-zebra\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("   font-size: 12px;\n")
        self.cssContents.append("   margin: 0px;\n")
        self.cssContents.append("   width: 100%;\n")
        self.cssContents.append("   text-align: left;\n")
        self.cssContents.append("   border-collapse: collapse;\n")
        self.cssContents.append(" }\n")
        self.cssContents.append(" #hor-zebra th\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-size: 14px;\n")
        self.cssContents.append("   font-weight: normal;\n")
        self.cssContents.append("   padding: 10px 8px;\n")
        self.cssContents.append("   color: #039;\n")
        self.cssContents.append("   border-bottom: 2px solid #6678b1;\n")
        self.cssContents.append("   border-right: 1px solid #6678b1; \n")
        self.cssContents.append("	border-left: 1px solid #6678b1;\n")
        self.cssContents.append(" }\n")
        self.cssContents.append(" #hor-zebra td\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   padding: 8px;\n")
        self.cssContents.append("   color: #669;\n")
        self.cssContents.append("   border-right: 1px solid #6678b1; \n")
        self.cssContents.append("	border-left: 1px solid #6678b1;\n")
        self.cssContents.append(" }\n")
        self.cssContents.append(" #hor-zebra .odd\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   background: #e8edff;\n")
        self.cssContents.append("   border-right: 1px solid #6678b1; \n")
        self.cssContents.append("	border-left: 1px solid #6678b1;\n")
        self.cssContents.append(" }\n")
        #GREEN TABLE
        self.cssContents.append(" #green \n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("   font-size: 12px;\n")
        self.cssContents.append("   margin: 0px;\n")
        self.cssContents.append("   width: 100%;\n")
        self.cssContents.append("   text-align: left;\n")
        self.cssContents.append("   border-collapse: collapse;\n")
        self.cssContents.append(" }\n")
        self.cssContents.append(" #green th\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-size: 14px;\n")
        self.cssContents.append("   font-weight: normal;\n")
        self.cssContents.append("   padding: 10px 8px;\n")
        self.cssContents.append("   color: #2b9900;\n")
        self.cssContents.append("   border-bottom: 2px solid #66b16f;\n")
        self.cssContents.append("   border-right: 1px solid #66b16f; \n")
        self.cssContents.append("	border-left: 1px solid #66b16f;\n")
        self.cssContents.append(" }\n")
        self.cssContents.append(" #green td\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   padding: 8px;\n")
        self.cssContents.append("   color: #578055;\n")
        self.cssContents.append("   border-right: 1px solid #66b16f; \n")
        self.cssContents.append("	border-left: 1px solid #66b16f;\n")
        self.cssContents.append(" }\n")
        self.cssContents.append(" #green .odd\n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   background: #eaffe8;\n")
        self.cssContents.append("   border-right: 1px solid #66b16f; \n")
        self.cssContents.append("	border-left: 1px solid #66b16f;\n")
        self.cssContents.append(" }\n")
        #LINKS
        self.cssContents.append("a.link:link {font-family: \"Sans-Serif\";font-size: 12px;color: #039;text-decoration:none;}")
        self.cssContents.append("a.link:visited {font-family: \"Sans-Serif\";font-size: 12px;color: #039;text-decoration:none;}")
        self.cssContents.append("a.link:hover {font-family: \"Sans-Serif\";font-size: 12px;color: #039;text-decoration:underline;}")
        #P BLUE
        self.cssContents.append(" #descriptionBlue \n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("   font-size: 14px;\n")
        self.cssContents.append("   text-align: left;\n")
        self.cssContents.append("   color: #039;\n")
        self.cssContents.append("   border-collapse: collapse;\n")
        self.cssContents.append(" }\n")
        #P GREEN
        self.cssContents.append(" #descriptionGreen \n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("   font-size: 14px;\n")
        self.cssContents.append("   text-align: left;\n")
        self.cssContents.append("   color: #009900;\n")
        self.cssContents.append("   border-collapse: collapse;\n")
        self.cssContents.append(" }\n")
        #P SUBTITLE BLUE
        self.cssContents.append(" #subtitleBlue \n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("   font-size: 16px;\n")
        self.cssContents.append("   font-weight: bold;\n")
        self.cssContents.append("   text-decoration:underline;\n")
        self.cssContents.append("   text-align: left;\n")
        self.cssContents.append("   color: #039;\n")
        self.cssContents.append("   border-collapse: collapse;\n")
        self.cssContents.append(" }\n")
        #P SUBTITLE GREEN
        self.cssContents.append(" #subtitleGreen \n")
        self.cssContents.append(" {\n")
        self.cssContents.append("   font-family: \"Sans-Serif\";\n")
        self.cssContents.append("   font-size: 16px;\n")
        self.cssContents.append("   font-weight: bold;\n")
        self.cssContents.append("   text-decoration:underline;\n")
        self.cssContents.append("   text-align: left;\n")
        self.cssContents.append("   color: #009900;\n")
        self.cssContents.append("   border-collapse: collapse;\n")
        self.cssContents.append(" }\n")


    def addHtmlReportHeader(self):
        ''' Add HTML Report Header to a given vector'''
        self.cssHtml.append("<HTML>\n")

        self.cssHtml.append(" <HEAD>\n")
        self.cssHtml.append(" <STYLE TYPE=\"text/css\">\n")

        self.cssHtml.append("  <!--\n")
        self.cssHtml.append("   @import url(\"style.css\"); \n")
        self.cssHtml.append("  -->\n")

        self.cssHtml.append(" </STYLE>\n")
        self.cssHtml.append(" </HEAD>\n")

        self.cssHtml.append(" <BODY>\n")
	self.cssHtml.append(" <BODY> <BODY>\n")

        self.cssHtml.append("  <H1 id=\"title\"> <U> DUPLICATES REPORT </U> </H1>\n")


    def addHtmlTable(self):
        '''Add HTML Table'''
        self.cssHtml.append("  <TABLE id=\"hor-zebra\">\n")
        self.cssHtml.append("   <TR>\n")
	self.cssHtml.append("    <TH scope=\"col\"> SAMPLE </TH> <TH scope=\"col\"> LIBRARY </TH> \
                                 <TH scope=\"col\"> Total Reads </TH> \
                                 <TH scope=\"col\"> Duplicates Reads - %  </TH> \
                                 <TH scope=\"col\"> Mapped Reads - % </TH> \
                                 <TH scope=\"col\"> Properly Paired Reads - % </TH> \
                                 <TH scope=\"col\"> Improperly Paired Read  - % </TH>   \n")
        self.cssHtml.append("   </TR>\n")

        isOdd = False

        for sampleLibDup in self.sampleLibDuplicates:
            #Check row pairing
            if isOdd == True: 
               self.cssHtml.append("   <TR class=\"odd\">\n")
               isOdd = False
            else:
               self.cssHtml.append("   <TR>\n")
               isOdd = True
	
            self.cssHtml.append("     <TD> " + str(sampleLibDup[0]) + " </TD> <TD> " + str(sampleLibDup[1]) + " </TD> <TD> " + str(sampleLibDup[2][0]) + " </TD>\
                                 <TD> " + str(sampleLibDup[2][1]) + "  " + str( ( float(sampleLibDup[2][1]) / float(sampleLibDup[2][0]) )*100 ) + "% </TD> \
                                 <TD> " + str(sampleLibDup[2][2]) + "  " + str( ( float(sampleLibDup[2][2]) / float(sampleLibDup[2][0]) )*100 ) + "% </TD> \
                                 <TD> " + str(sampleLibDup[2][3]) + "  " + str( ( float(sampleLibDup[2][3]) / float(sampleLibDup[2][0]) )*100 ) + "% </TD> \
                                 <TD> " + str(sampleLibDup[2][4]) + "  " + str( ( float(sampleLibDup[2][4]) / float(sampleLibDup[2][0]) )*100 ) + "% </TD>")
	    self.cssHtml.append("   </TR>\n")

        self.cssHtml.append("  </TABLE>\n")
        self.cssHtml.append("\n")

    def closeHtmlReport(self):
        ''' CLOSE HTML header to a given vector object '''  
        self.cssHtml.append(" </BODY>\n")
        self.cssHtml.append("</HTML>\n")

    def buildHtmlJson(self):
        ''' Create HTML and JSON file report '''
        cssFile = os.path.dirname(self.file_duplicates[0]) + "/style.css"
        htmlFile = os.path.dirname(self.file_duplicates[0]) + "/duplicates.html"
        jsonFile = os.path.dirname(self.file_duplicates[0]) + "/duplicates.json"

        #1. Create CSS

        self.buildStyleSheet()
        with open(cssFile, 'w') as cssDocument:
            for line in self.cssContents:
                cssDocument.write(line+ '\n')

        #2. Create HTML
        self.addHtmlReportHeader()
        self.addHtmlTable()
        self.closeHtmlReport()
        with open(htmlFile, 'w') as htmlDocument:
            for line in self.cssHtml:
                htmlDocument.write(line+ '\n')

        #4. Store JSON file
        with open(jsonFile, 'w') as of:
            json.dump(self.jsonDictionary, of, indent=2)


#1.Create object class Documentation File
configManager = CreateDocumentationFiles()

#2.Create object for argument parsinng
parser = argparse.ArgumentParser(prog="create_doc",description="Duplicates report builder.", formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=350))
#parser.formatter.max_help_position = 50
#2.1 Updates arguments and parsing
configManager.register_parameters(parser)
args = parser.parse_args()
#2.2 Arguments parsing
configManager.parseArguments(args)
#2.3 Check Parameters
if not configManager.check_parameters():
    sys.exit()


#3. Parsing statistics Duplicates files
configManager.parserStatsFiles()

#4. Build output files
configManager.buildHtmlJson()





                       




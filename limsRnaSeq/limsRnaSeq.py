#!/usr/bin/env python

import os
import re
import sys
import argparse
import getopt
import glob
import requests
import json


class LimsRnaSeq():

    def __init__(self):
        '''Calls constructor'''
        self.loadedwithId = None
        self.mapping_uri = None     #Resource uri for posting data
        self.mapping_id = None      #id for quering data
        #self.server = "http://cn503/test"  # use this for the test server 
        #self.server = "http://cn503/lims_testing"  # use this for the test server 
        self.server = "http://cn503/lims" # uncomment this line  for the production lims server
        self.headers = {'content-type': 'application/json'}
        self.params = {'limit': 0}
        self.rnaseqmapping_url = None
        self.rnaseq_get = None
        self.rnaseqmapping_json = None

        self.rnaseq_library_url = None
        self.id_list_string = None   #List of ID mappings related to a given libary 
 
        self.rnaseq_aggregate_url = None
        self.rnaseq_aggregate_get = None
        self.library_id = None
        self.library_resource_uri = None

        self.get_library_url = None


        self.mappingReference = None #Genome reference used for mapping
        self.response = None         #Object response from the request package 
        self.method = None           #Method to apply when submitting data (POST or PUT) depending if we 
                                     #must create or update a new register        

        self.sample = None          #Sample name to be uploaded to lims database
        self.library = None         #Library name to be uploaded to lims database
        self.flowcell = None        #Flowcell name to be uploaded to lims database
        self.lane = None            #Lane number to be uploaded to lims database
     
        self.rna_mapping_dict =  {
                                  'total_reads' : None,
                                  'percent_mapped_reads' : None,
                                  'mapped_reads' : None,
                                  'percent_paired_mapped' : None,
                                  'paired_mapped' : None,
                                  'percent_single_mapped' : None,
                                  'single_mapped' : None,
                                  'percent_split_mapped' : None,
                                  'split_mapped' : None,
                                  'counted_reads' : None,
                                  'percent_unmapped' : None,
                                  'unmapped' : None,
                                  'percent_exonic' : None,
                                  'exonic' : None,
                                  'percent_intronic' : None,
                                  'intronic' : None,
                                  'percent_intergenic' : None,  
                                  'intergenic' : None,  
                                  'percent_protein_coding' : None,
                                  'protein_coding' : None,
                                  'percent_Mt_rRNA' : None,
                                  'mt_rrna' : None,
                                  'percent_processed_transcript' : None,
                                  'processed_transcript' : None,
                                  'percent_lincRNA' : None,
                                  'lincrna' : None,
                                  'percent_pseudogene' : None,
                                  'pseudogene' : None,
                                  'percent_antisense' : None,
                                  'antisense' : None,
                                  'percent_3prime_overlapping_ncrna' : None, 
                                  'three_prime_overlapping_ncrna' : None, 
                                  'percent_TR_V_gene' : None,
                                  'tr_v_gene': None,
                                  'percent_IG_V_gene' : None,
                                  'ig_v_gene' : None,
                                  'percent_sense_overlapping' : None,
                                  'sense_overlapping' : None,
                                  'percent_polymorphic_pseudogene' : None,
                                  'polymorphic_pseudogene' : None,
                                  'percent_sense_intronic' : None,
                                  'sense_intronic' : None,
                                  'percent_TR_C_gene' : None,
                                  'tr_c_gene' : None,
                                  'percent_IG_C_gene' : None,  
                                  'ig_c_gene' : None,  
                                  'percent_misc_RNA' : None,
                                  'misc_RNA' : None,
                                  'percent_IG_V_pseudogene' : None,
                                  'ig_v_pseudogene' : None,
                                  'percent_miRNA' : None,
                                  'mirna' : None,
                                  'percent_IG_C_pseudogene' : None, 
                                  'ig_c_pseudogene' : None,
                                  'percent_snRNA' : None,
                                  'snrna' : None,
                                  'percent_snoRNA' : None,
                                  'snorna' : None,
                                  'percent_TR_V_pseudogene' : None,
                                  'tr_v_pseudogene' : None,
                                  'percent_IG_J_gene' : None,
                                  'ig_j_gene' : None,
                                  'percent_rRNA' : None,
                                  'rrna' : None,
                                  'genes_detected' : None,
                                  'genes_25_percent_expression' : None,
                                  'percent_proper_pairs' : None,
                                  'proper_pairs' : None,
                                  'percent_improper_pairs' : None,
                                  'improper_pairs' : None,
                                  'percent_duplicates' : None, 
                                  'duplicates' : None, 
                                  'mapping':None,
                                  'annotation':None,
                                  'reference':None
        }

        self.rnaseq_aggregate_dict = {
                                  'sample' : None,
                                  'library' : None,
                                  'percent_proper_pairs' : None,
                                  'proper_pairs' : None,
                                  'percent_improper_pairs' : None,
                                  'improper_pairs' : None,
                                  'percent_duplicates' : None,
                                  'duplicates' : None,
                                  'mapping_ids' : None
        }

        self.runConfig()

    def runConfig(self):
        """ Check for config file exitance and get User and Key """
        try:
            username = ""
            key = "" 
            configFile = os.path.dirname(os.path.realpath(__file__)) + "/config"
            with open(configFile) as file_config:
                for line in file_config:
                    cleanLine = line.strip('\n') 
                    fields = re.split(' ',cleanLine)                   
                    username = fields[0]
                    key = fields[1]
     

            self.headers = {'content-type': 'application/json', 'Authorization: ApiKey %s:%s' %(username,key)}   
        except IOError as e:
            print "Unable to open config file. You need a config file to have acces to lims database. Write in this file a username and a password." 
            exit()

    def delStats(self):
        """ Reset stats values """
        self.rna_mapping_dict = dict.fromkeys(self.rna_mapping_dict, None)
        self.rnaseq_aggregate_dict = dict.fromkeys(self.rnaseq_aggregate_dict, None)

    def register_parameters(self, parser):
        """Register script parameters with given
        argparse parser
        parser -- the argparse parser
        """
        general_group = parser.add_argument_group('Input Files')
        general_group.add_argument('-d', dest="directory", help='RNASeq mapping directory.')
        config_group = parser.add_argument_group('Configuration')
        config_group.add_argument('--no_filter', dest="no_filter",action="store_true", default=False,help='Do not use filtered files for building stats.')     
   
    def checkFileName(self,nameJson=None,justLibrary = False,separator='_'):
        '''Checks if the file complies Name format Standard SAMPLE_LIBRARY_FLOWCELL_LANE...'''
        import re
        numberOfFields = 4
        if justLibrary:
            numberOfFields = 2

        fields = nameJson.split(separator)
        if fields < numberOfFields:
            return False
        return True

    def getSampleName(self,nameJson=None,separator='_'):
        ''' Return sample name from a Bam which complies the name format SAMPLE_LIBRARY_FLOWCELL_LANE...''' 
        return nameJson.split(separator)[0]

    def getLibraryName(self,nameJson=None,separator='_'):
        ''' Return library name from a Bam which complies the name format SAMPLE_LIBRARY_FLOWCELL_LANE...''' 
        return nameJson.split(separator)[1]

    def getFlowcellName(self,nameJson=None,separator='_'):
        ''' Return library name from a Bam which complies the name format SAMPLE_LIBRARY_FLOWCELL_LANE...''' 
        return nameJson.split(separator)[2]

    def getLaneName(self,nameJson=None,separator='_'):
        ''' Return library name from a Bam which complies the name format SAMPLE_LIBRARY_FLOWCELL_LANE...''' 
        return nameJson.split(separator)[3]

    def updateLaneLibraryNames(self,nameJson=None):
        ''' Check and get sample, library and lane names 
            return True if the names for sample, library, flowcell and lane can be retrieve, otherwise false'''        
        if self.checkFileName(nameJson):      
            self.sample = self.getSampleName(nameJson)
            self.library = self.getLibraryName(nameJson)
            self.flowcell = self.getFlowcellName(nameJson)
            self.lane  = self.getLaneName(nameJson)
            return True
        else:
            return False
     
    def updateSampleLibraryNames(self, sample_library = None):
        ''' Check and get sample, library and lane names 
            return True if the names for sample, library, flowcell and lane can be retrieve, otherwise false''' 
        if self.checkFileName(sample_library,justLibrary = True):  
            self.sample = self.getSampleName(sample_library)
            self.library = self.getLibraryName(sample_library)
            return True
        else:
            return False

    def parserJsonFile(jsonFile):
        '''Parser a json file and retorns a dictionary
        Parameters:
        jsonFile -- Path to the json file configuration
        Returns: Dictionary json representation
        '''
        import json
        with open(jsonFile) as json_file:
            return json.load(json_file)

    def getPercentage(self,value=None,total=None):
        ''' Return percentage value over total''' 
        return str((float(value) / float (total) * 100))

    def countMappingPatterns(self,mappingLocations = None, paired = True, criteria = None):
        ''' Look for a given pair or single pattern '''
        counter = 0;
       
        for key in mappingLocations.keys():
            
            if paired:
                fieldsKey = key.split('|') 
                 
                if len(fieldsKey) >= 2:
                    pairOne = fieldsKey[0].find(criteria)
                    pairTwo = fieldsKey[1].find(criteria)

                    if pairOne != -1 and pairTwo != -1 :
                        counter += int(mappingLocations[key])
                    elif (pairOne == -1 and pairTwo != -1) or (pairOne != -1 and pairTwo == -1) :
                        counter += int(mappingLocations[key])/2
                elif len(fieldsKey) == 1:
                    pairSingle = fieldsKey[0].find(criteria)
                    if pairSingle != -1 :
                        counter += int(mappingLocations[key])/2
            else:
                if key.find(criteria) != -1:
                    counter += int(mappingLocations[key])

        return counter


    def splitReads(self,mappingLocations = None,paired=True):
        '''Calculate split reads on those patterns were ^ is found '''
        return self.countMappingPatterns(mappingLocations = mappingLocations, paired = paired, criteria = '^')

    def exonReads(self,mappingLocations = None,paired=True):
        '''Calculate exon reads on those patterns were exone is found '''
        return self.countMappingPatterns(mappingLocations = mappingLocations, paired = paired, criteria = 'exon')

    def intronReads(self,mappingLocations = None,paired=True):
        '''Calculate intron reads on those patterns were exone is found '''
        return self.countMappingPatterns(mappingLocations = mappingLocations, paired = paired, criteria = 'intron')

    def notAnnotatedReads(self,mappingLocations = None,paired=True):
        '''Calculate notAnnotated reads on those patterns were exone is found '''
        return self.countMappingPatterns(mappingLocations = mappingLocations, paired = paired, criteria = 'na')

    def getGenesDetected(self,geneCounts=None):
        '''Get number of genes detected'''
        count = 0
        with open(geneCounts, "r") as counts:
            for line in counts:
                vFields = re.split('\t',line.rstrip('\n'))
                if float(vFields[1]) > 0:
                    count = count + 1
        return count


    def getGenes_25_expressed(self, geneCounts=None):
        '''Get 25 most expressed genes'''
        def getKey(item):
            return item[1]

        total_expression = 0
        geneList = []

        #1.LOAD ALL FILE
        with open(geneCounts, "r") as counts:
            for line in counts:
                vFields = re.split('\t',line.rstrip('\n'))
                geneList.append([vFields[0],float(vFields[1])])
                total_expression = total_expression + float(vFields[1])

        #2.SORT IT
        sorted(geneList, key=getKey,reverse=True)

        #3.COUNT NUMBER OF GENES OVER 25 %
        acumulated = 0
        count = 0

        for gene in geneList:
            count = count + 1
            acumulated = acumulated + gene[1]
            if (float(acumulated) / float(total_expression)) > 0.25:
                break

        return count

    def parseFlagstat(self,flagstatFile = None):
        ''' Parsing flagstats per lane'''
        #Parse flagstat file
        with open(flagstatFile, "r") as stFile:
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

        dictionary = {}
        dictionary['percent_proper_pairs'] = (float(properly_paired) / float(total_reads)) * 100
        dictionary['percent_improper_pairs'] = (float(inproper_pairs) / float(total_reads)) * 100
        dictionary['percent_duplicates'] = (float(duplicates) / float(total_reads)) * 100

        dictionary['proper_pairs'] = properly_paired
        dictionary['improper_pairs'] = inproper_pairs
        dictionary['duplicates'] = duplicates
        
        return dictionary
      
    def checkAndLoad(self,concept,percent_concept,mapping_concept,typeCountsDict,rna_mapping_dict,total):
        ''' Check in type counts the existance of the concept to be uploaded'''
        if concept in typeCountsDict.keys():
            rna_mapping_dict[percent_concept] = self.getPercentage(typeCountsDict[concept],total)
            rna_mapping_dict[mapping_concept] = typeCountsDict[concept]  

    def parseRawData(self,jsonFile = None, geneCounts = None, flagstatsFile = None,configuration=None):
        ''' Parsing JSON Structure '''
        jsonStructure = {}
        
        with open(jsonFile) as json_file:
            jsonStructure = json.load(json_file)

        #1.JSON GTF FILE STATS
        self.rna_mapping_dict['total_reads'] = jsonStructure["general"]["reads"]

        self.rna_mapping_dict['percent_mapped_reads'] = self.getPercentage(jsonStructure["general"]["mapped_reads"],jsonStructure["general"]["reads"])
        self.rna_mapping_dict['mapped_reads'] = jsonStructure["general"]["mapped_reads"]

        self.rna_mapping_dict['percent_paired_mapped'] = self.getPercentage(jsonStructure["general"]["mapped_paired_reads"],jsonStructure["general"]["reads"])
        self.rna_mapping_dict['paired_mapped'] = jsonStructure["general"]["mapped_paired_reads"]
        self.rna_mapping_dict['percent_single_mapped'] = self.getPercentage(jsonStructure["general"]["mapped_single_reads"],jsonStructure["general"]["reads"])
        self.rna_mapping_dict['single_mapped'] = jsonStructure["general"]["mapped_single_reads"]
        

        total_splits = self.splitReads(jsonStructure["pair_patterns"]) + self.splitReads(jsonStructure["single_patterns"],False)
        self.rna_mapping_dict['percent_split_mapped'] =  self.getPercentage(total_splits,jsonStructure["general"]["reads"])
        self.rna_mapping_dict['split_mapped'] =  total_splits
        self.rna_mapping_dict['counted_reads'] = jsonStructure["counts"]["total_counted_reads"]
        total_unmapped = jsonStructure["general"]["unmapped_reads"]
        self.rna_mapping_dict['percent_unmapped'] = self.getPercentage(total_unmapped,jsonStructure["general"]["reads"])
        self.rna_mapping_dict['unmapped'] = total_unmapped

        total_exon = self.exonReads(jsonStructure["pair_patterns"]) + self.exonReads(jsonStructure["pair_patterns"],False)
        self.rna_mapping_dict['percent_exonic'] = self.getPercentage(total_exon,jsonStructure["general"]["reads"])
        self.rna_mapping_dict['exonic'] = total_exon

        total_intron = self.intronReads(jsonStructure["pair_patterns"]) + self.intronReads(jsonStructure["pair_patterns"],False)
        self.rna_mapping_dict['percent_intronic'] = self.getPercentage(total_intron,jsonStructure["general"]["reads"])
        self.rna_mapping_dict['intronic'] = total_intron
      
        total_not_annotated = self.notAnnotatedReads(jsonStructure["pair_patterns"]) + self.notAnnotatedReads(jsonStructure["pair_patterns"],False)
        self.rna_mapping_dict['percent_intergenic'] = self.getPercentage(total_not_annotated,jsonStructure["general"]["reads"]) 
        self.rna_mapping_dict['intergenic'] = total_not_annotated

        typeCounts = jsonStructure["type_counts"]
        total_number_reads = jsonStructure["general"]["reads"]

        self.checkAndLoad('protein_coding','percent_protein_coding','protein_coding',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('Mt_rRNA','percent_Mt_rRNA','mt_rrna',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('processed_transcript','percent_processed_transcript','processed_transcript',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('lincRNA','percent_lincRNA','lincrna',typeCounts,self.rna_mapping_dict,total_number_reads)
      
        self.checkAndLoad('pseudogene','percent_pseudogene','pseudogene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('antisense','percent_antisense','antisense',typeCounts,self.rna_mapping_dict,total_number_reads)
    
        self.checkAndLoad('three_prime_overlapping_ncrna','percent_3prime_overlapping_ncrna','three_prime_overlapping_ncrna',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('TR_V_gene','percent_TR_V_gene','tr_v_gene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('IG_V_gene','percent_IG_V_gene','ig_v_gene',typeCounts,self.rna_mapping_dict,total_number_reads)        
       
        self.checkAndLoad('sense_overlapping','percent_sense_overlapping','sense_overlapping',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('polymorphic_pseudogene','percent_polymorphic_pseudogene','polymorphic_pseudogene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('sense_intronic','percent_sense_intronic','sense_intronic',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('TR_C_gene','percent_TR_C_gene','tr_c_gene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('IG_C_gene','percent_IG_C_gene','ig_c_gene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('misc_RNA','percent_misc_RNA','misc_RNA',typeCounts,self.rna_mapping_dict,total_number_reads)

        self.checkAndLoad('IG_V_pseudogene','percent_IG_V_pseudogene','ig_v_pseudogene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('miRNA','percent_miRNA','mirna',typeCounts,self.rna_mapping_dict,total_number_reads)   
        self.checkAndLoad('IG_C_pseudogene','percent_IG_C_pseudogene','ig_c_pseudogene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('snRNA','percent_snRNA','snrna',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('snoRNA','percent_snoRNA','snorna',typeCounts,self.rna_mapping_dict,total_number_reads)
        
        self.checkAndLoad('TR_V_pseudogene','percent_TR_V_pseudogene','tr_v_pseudogene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('IG_J_gene','percent_IG_J_gene','ig_j_gene',typeCounts,self.rna_mapping_dict,total_number_reads)
        self.checkAndLoad('rRNA','percent_rRNA','rrna',typeCounts,self.rna_mapping_dict,total_number_reads)

        
        #2.GEN COUNTS DATA
        self.rna_mapping_dict['genes_detected'] = self.getGenesDetected(geneCounts)
        self.rna_mapping_dict['genes_25_percent_expression'] = self.getGenes_25_expressed(geneCounts)

        #3.FLAGSTATS FILE FOR REMOVE DUPLICATES PER LANE
        flagstatFields = self.parseFlagstat(flagstatsFile)
        self.rna_mapping_dict['percent_proper_pairs'] = flagstatFields['percent_proper_pairs']
        self.rna_mapping_dict['proper_pairs'] = flagstatFields['proper_pairs']
        self.rna_mapping_dict['percent_improper_pairs'] = flagstatFields['percent_improper_pairs']
        self.rna_mapping_dict['improper_pairs'] = flagstatFields['improper_pairs']
        self.rna_mapping_dict['percent_duplicates'] = flagstatFields['percent_duplicates']
        self.rna_mapping_dict['duplicates'] = flagstatFields['duplicates']

        #4. PARSE MAPPING FIELD URI
        self.rna_mapping_dict['mapping'] = self.mapping_uri

        #5. REFERENCE NAME
        self.rna_mapping_dict['reference'] = os.path.basename(configuration["index"])
        self.rna_mapping_dict['annotation'] = os.path.basename(configuration["annotation"])
      

    def parseRawDataLibrary(self,key_name = None, dict_library = None):
        ''' From key sample_library name get stats from library dictionary and update rnaseq_aggregate_dict 
            which will be submitted to lims '''
      
        self.rnaseq_aggregate_dict['sample'] = dict_library [key_name]['sample']
        self.rnaseq_aggregate_dict['library'] = dict_library [key_name]['library']
        self.rnaseq_aggregate_dict['percent_proper_pairs'] = dict_library [key_name]["percent_properly_paired"]
        self.rnaseq_aggregate_dict['proper_pairs'] = dict_library [key_name]["properly_paired"]
        self.rnaseq_aggregate_dict['percent_improper_pairs'] = dict_library [key_name]["percent_inproper_pairs"]
        self.rnaseq_aggregate_dict['improper_pairs'] = dict_library [key_name]["inproper_pairs"]
        self.rnaseq_aggregate_dict['percent_duplicates'] = dict_library [key_name]["percent_duplicates"]
        self.rnaseq_aggregate_dict['duplicates'] = dict_library [key_name]["duplicates_reads"]

       
    def queryDataBase(self):
        ''' Query database for all mapping objects matching a flowcell, lane, and library 
            return True if the query was a success'''
        fc_name = self.flowcell
        lane_number = self.lane
        library_name = self.library  

        get_mapping_url = "%s/api/seq/mapping/?" % self.server
        get_mapping_url += "format=json"\
                           "&loadedwith__lane__flowcell__name=%s"\
                           "&loadedwith__lane__lane=%s" \
                           "&loadedwith__library__name=%s"  % (fc_name, lane_number, library_name)
     
      
        self.response = requests.get(url=get_mapping_url, headers=self.headers, params=self.params)
        
        if self.response.status_code == 200:
            self.mapping_uri = self.response.json()['objects'][0]['resource_uri']   
            self.mapping_id =  self.response.json()['objects'][0]['id']             
        else:
            raise Exception("Query lims database of flowcell %s , lane %s and library %s return a http error: %i" %(fc_name,lane_number,library_name,self.response.status_code))

    def checkRnaSeqAssociatedToMappingObject(self):
        ''' Check if we have an rnaseqmapping associated with that mapping object
            if YES then UPDATE otherwise CREATE A NEW ONE
            method is updated to update or create new register '''
        self.rnaseqmapping_url = "%s/api/seq/rnaseqmapping/"  % self.server
        self.rnaseq_get = self.rnaseqmapping_url + "?mapping=%s" % self.mapping_id
        #Querying database for existing rnaseq mappings
       
        self.response = requests.get(url=self.rnaseq_get, headers=self.headers, params=self.params)

        if self.response.status_code == 200:       
            self.rnaseqmapping_json = self.response.json()
            rnaseqmappings_returned = self.rnaseqmapping_json['meta']['total_count']
            self.method =  {0: 'POST', 1: 'PUT' }[rnaseqmappings_returned]
        else:
            raise Exception("http GET error when querying database for existing rnaseq mappings. Error code: %i" %(self.response.status_code))


    def updateLaneToLIMS(self):
        ''' Update Rnaseq data to LIMS Database'''    
        # convert python dictionary to json
        rna_mapping_json = json.dumps(self.rna_mapping_dict)
        
        if self.method == 'POST' :
            print " POST-ing data to %s\n\n"  %  self.rnaseqmapping_url
            self.response = requests.post(url=self.rnaseqmapping_url, headers=self.headers , data=rna_mapping_json)
            
            if self.response.status_code != 201:
	    	raise Exception(json.loads(self.response.content)['error_message'])

        elif self.method == 'PUT':
            # alter url, to include the id we are updating
            self.rnaseqmapping_url += "%s/" % self.rnaseqmapping_json['objects'][0]['id']
            print ' PUT-ing data to %s\n\n' %  self.rnaseqmapping_url
	
            self.response = requests.put(url=self.rnaseqmapping_url, headers=self.headers , data=rna_mapping_json)
            
            if self.response.status_code != 204:
                raise Exception(json.loads(self.response.content)['error_message'])

    ########################################################################
    ########### Update values per Library                   ################
    ########################################################################

    def checkRnaSeqAssociatedToLibraryObject(self): 
        ''' Check if we have an rnaseq libary associated with that library object
            if YES then UPDATE otherwise CREATE A NEW ONE
            method is updated to update or create new register '''
        self.rnaseq_library_url = "%s/api/seq/rnaseqmapping/"  % self.server
        self.rnaseq_library_url += "?format=json&loadedwith__library__name=%s"  % (self.library)
     
        self.response = requests.get(url=self.rnaseq_library_url, headers=self.headers, params=self.params)

        if self.response.status_code == 200:
            id_list = [str(mapping['id'])for mapping in self.response.json()['objects'] ]
            self.id_list_string = ','.join(id_list) 
            print "List of mapping id's %s" % self.id_list_string
        else:
            raise Exception("Response error to library request. http error: %i" % self.response.status_code)
        


    def checkRnaSeqMappingAssociatedToLibraryObject(self): 
        ''' Check if we have an rnaseqmapping associated with a library object
            if YES then UPDATE otherwise CREATE A NEW ONE
            method is updated to update or create new register '''
        self.rnaseq_aggregate_url = "%s/api/seq/rnaseqaggregatestats/"  % self.server
        self.rnaseq_aggregate_get = "%s?format=json&library__name=%s" % (self.rnaseq_aggregate_url , self.library)


        #Querying database for existing rnaseq mappings associated to library objects
        self.response = requests.get(url=self.rnaseq_aggregate_get, headers=self.headers, params=self.params)
  
        if self.response.status_code == 200:        
            self.rnaseq_aggregate_json = self.response.json()
            rnaseq_aggregates_returned = int(self.rnaseq_aggregate_json['meta']['total_count'])
            self.method =  {0: 'POST', 1: 'PUT' }[rnaseq_aggregates_returned]
        else:
            raise Exception("Sorry! GET method for checking rnaseq aggregate database returns error code %i " % self.response.status_code)


    def updateLibraryToLIMS(self):
        ''' Update Rnaseq data to LIMS Database'''
        self.get_library_url = "%s/api/seq/rnaseqaggregatestats/?" % self.server
        self.get_library_url += "format=json&library__name=%s"  % (self.library) 

        #Querying database for mappings, filtering by library name
        self.response = requests.get(url=self.get_library_url, headers=self.headers, params=self.params)

        if self.response.status_code == 200:        
            jsonResponse = self.response.json()
            if len(jsonResponse['objects']) > 0:
                self.library_resource_uri = jsonResponse['objects'][0]['library']
            else:
                #If we are creating a new rnaseqaggregatestats so then there is no object to get from there, we must look for the library id in libary table
                self.get_library_url = "%s/api/seq/library/?" % self.server
                self.get_library_url += "format=json&name=%s"  % (self.library)
                
                self.response = requests.get(url=self.get_library_url, headers=self.headers, params=self.params)
              
                if self.response.status_code == 200:
                    self.library_resource_uri = self.response.json()['objects'][0]['resource_uri']
                else:
                    raise Exception("Sorry! GET method to get library id from Library table returns an error code %i " % self.response.status_code)
        else:
            raise Exception("Sorry! GET method to get library id from rnaseqaggregatestats aggregate table returns an error code %i " % self.response.status_code)

        self.rnaseq_aggregate_dict['library'] = self.library_resource_uri 
        self.rnaseq_aggregate_dict['mapping_ids'] = self.id_list_string
 
        # convert python dictionary to json
        rnaseq_aggregate_json = json.dumps(self.rnaseq_aggregate_dict)
    

        if self.method == 'POST' :
            print " POST-ing data to %s\n%s\n\n"  % ( self.rnaseq_aggregate_url , rnaseq_aggregate_json ) 
            self.response = requests.post(url=self.rnaseq_aggregate_url,headers=self.headers,data=rnaseq_aggregate_json)
    
            if self.response.status_code != 201:
                json_content  = json.loads(self.response.content)
                
                if 'error' in json_content :
                    raise Exception(json_content['error'])
                else: 
                    raise Exception(json_content['error_message'] + "\n" + json_content['traceback'])

        elif self.method == 'PUT':
            #alter url, to include the id we are updating
            self.rnaseq_aggregate_url += "%s/" % self.rnaseq_aggregate_json['objects'][0]['id']
            print ' PUT-ing data to %s\n%s\n\n' % ( self.rnaseq_aggregate_url , rnaseq_aggregate_json )
            self.response = requests.put(url=self.rnaseq_aggregate_url, headers=self.headers , data=rnaseq_aggregate_json)

            if self.response.status_code not in [201, 204]:
                json_content  = json.loads(self.response.content)
                if 'error' in json_content :
                    raise Exception(json_content['error'])
                else: 
                    raise Exception(json_content['error_message'] + "\n" + json_content['traceback'])
      

#1.Create object class LimsRnaSeq File
configManager = LimsRnaSeq()

#2.Create object for argument parsinng
parser = argparse.ArgumentParser(prog="limsRnaSeq",description="LIMS Rna Pipeline submission", formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=350))

#2.1 Updates arguments and parsing
configManager.register_parameters(parser)
args = parser.parse_args()

#2.2 Select which mapping stats to use for build the report. Stats comming from filtered bam file or raw bam file.
gtf_stats_search = "/*.filtered.gtf.stats.json"
gtf_counts_txt = "/*.filtered.gtf.counts.txt"

if args.no_filter:
    gtf_stats_search = "/*[0-9].gtf.stats.json"
    gtf_counts_txt = "/*[0-9].gtf.counts.txt"


#3.1 Get files from RNASeq Mapping Directory
laneGtfStats = sorted(glob.glob(args.directory + gtf_stats_search))
laneGeneCounts = sorted(glob.glob(args.directory + gtf_counts_txt))
rmDupsFiles = sorted(glob.glob(args.directory + "/*.rmdup.lane.flagstat"))

rmDupsLibrary = {}

with open(args.directory + "/duplicates.json") as json_file:
    rmDupsLibrary = json.load(json_file)

configuration = {}
with open(args.directory + "/.config.gt") as json_file:
    configuration = json.load(json_file)


if len(laneGtfStats) != len(laneGeneCounts) or len(laneGtfStats) != len(rmDupsFiles) or len(laneGtfStats) == 0:
    raise Exception("""The number of gtf stats files is not the same as gene counts files or remove duplicates files. Please check \
           number of *.filtered.gtf.stats.json files, *.filtered.gtf.counts.txt files and *.rmdup.lane.flagstat files. \n
           Lane GTF Files %i \n
           Lane Gene Counts Files %i \n
           Lane Rm Duplicates Files %i \n """ %(len(laneGtfStats),len(laneGeneCounts),len(rmDupsFiles) ) )


#3.1 Process all input data
for gtfJsonFile, geneCounts,rmDupFile in zip (laneGtfStats,laneGeneCounts,rmDupsFiles):
    #3.1.1 Process each set of files [[gtfStats][geneCounts][flagStats]]
    if configManager.updateLaneLibraryNames(os.path.basename(gtfJsonFile)):
        configManager.delStats()
        configManager.queryDataBase()
        configManager.checkRnaSeqAssociatedToMappingObject()
        configManager.parseRawData(jsonFile = gtfJsonFile, geneCounts = geneCounts, flagstatsFile = rmDupFile, configuration=configuration)
        configManager.updateLaneToLIMS()
    else:
        raise Exception("Sorry!! File %s does not comply with the pattern SAMPLE_LIBRARY_FLOWCELL_LANE at the begining of the name. \
               This pattern must be respected to get sample, library and flowcell information")


if len(rmDupsLibrary) < 1:
    raise Exception("No remove duplicates files per library are found. Please check *.rmdup.library.flagstat files.")

#4.1 For each flagstat file
for libStats in sorted(rmDupsLibrary.keys()) :
    if configManager.updateSampleLibraryNames(libStats):
        configManager.delStats()   
        configManager.checkRnaSeqAssociatedToLibraryObject()
        configManager.checkRnaSeqMappingAssociatedToLibraryObject()
        configManager.parseRawDataLibrary(libStats,rmDupsLibrary)
        configManager.updateLibraryToLIMS()
    else:
        raise Exception("Sorry!! File %s does not comply with the pattern SAMPLE_LIBRARY at the begining of the name. \
               This pattern must be respected to get sample and library information" %(libFlagStats))











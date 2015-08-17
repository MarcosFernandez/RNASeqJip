===================
RnaSeq JIP Pipeline
===================

Set of JIP pipeline system scripts to manage the RNA Seq Pipeline using gemtools rnaseq for mapping, flux-capcitor for quantification and sambamba to calculate PCR Duplicates statistics. It also updates a temporary file to be processed by daemon lims in order to update the pipeline results to the Lims System.


RnaSeq JIP Pipeline uses the JIP pipeline system to perform all pipeline steps, controlling each step dependency and output. 
The pipeline expects to find [JIP pipeline system](https://github.com/thasso/pyjip) installed on your system.
   
Licensing
=========

RnaSeq JIP Pipeline scripts are licensed under GPL.

Installation
============

Download the scripts and follow documentation steps.

Documentation
=============

Documentation can be found at [RnaSeq JIP Pipeline] (http://statgen.cnag.cat/rnaseqjip/index.html)


Changelog:
==========
    0.2 No modules loaded
    0.1 Absolut fields added.
        Lims sort vector of input parameters files to force coordination between Lane GTF stats, Lane Gene Counts and Remove duplicates files.
        Fixed error when merging mapping files with more than one mapping file per Library (more than one lane per library).
    0.0 Initial Release  





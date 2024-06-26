hapROH
==================

Scope of the Method
**************************
This software identfies runs of homozygosity in human (ancient) DNA data.

Default parameters are optimized for human 1240K capture data (ca. 1.2 million SNPs used widely in human aDNA analysis) and using 1000 Genome haplotypes as reference panel. The software is tested on a wide range of aDNA data, both 1240K data and also whole genome sequencing data downsampled to 1240K SNPs. Successful cases include 45k year old Ust Ishim man, and a wide range of American, Eurasian and Oceanian ancient DNA, showing that the method generally works for split times of reference panel and target up to a few 10k years, which includes all out-of-Africa populations (Attention: Neanderthals and Denisovans do not fall into that range, additionally some Subsaharan hunter gatherer test cases did not give satisfactory results).

Currently, hapROH works on data for 1240K SNPs and in unpacked or packed eigenstrat format (which is widely used in human ancient DNA). The software assumes pseudo-haploid or diploid genotype data (the mode can be set, by default it is pseudo-haploid). The recommended coverage range is 400,000 or more 1240K SNPs covered at least once.

If you have whole genome data available, you have to downsample an create eigenstrat files for biallelic 1240k SNPs first.

In case you are planning applications to other kind of SNP or bigger SNP sets, or even other organisms, the method parameters have to be adjusted (the default parameters are specifically optimized for human 1240K data). You can mirror our procedure to find good parameters (described in the publication), and if you contact us for assistance - I am happy to share my own experience.


Getting started
**************************
To get started, we prepared a **quick start vignettes as jupyter notebooks** <https://www.dropbox.com/sh/eq4drs62tu6wuob/AABM41qAErmI2S3iypAV-j2da?dl=0>`_.

These showcase example usecases, that you can use as template for your own applications.

These notebooks walk you through examples for: 

1. How to use the core functions to call ROH from eigenstrat files, and generate ROH tables from results of multiple individuals ('callROH_vignette')

2. How to use functions for visualizing ROH results (*plotting_vignette* - warning: Some of these are experimental and require additional packages. You might want to consider creating your own plotting functions for visualizing the results in the way that works best for you)

3. How to call IBD on the X chromosome between two male X chromosomes (*callIBD_maleX_vignette*, warning: experimental)

Download reference Data
**************************

hapROH currently uses global 1000 Genome data (n=5008 haplotypes from 2504 individuals), filtered down to bi-allelic 1240K SNPs. 
We use .hdf5 format for the reference panel - containing also data for the genetic map.

You can download the prepared reference data (including a necessary metadata .csv) `here: <https://www.dropbox.com/s/0qhjgo1npeih0bw/1000g1240khdf5.tar.gz?dl=0>`_. 

and unpack it using 

``tar -xvf FILE.tar.gz``

You then have to link the paths in the hapROH run parameters (see vignette notebook)


Example Use Case: Vignettes
*****************************

Please find `example notebooks <https://www.dropbox.com/sh/eq4drs62tu6wuob/AABM41qAErmI2S3iypAV-j2da?dl=0>`_, walking you through a typical application to an eigenstrat file.

All you need is a Eigenstrat file, and the reference genome data (see link above), and you are good to go to run your own ROH calling!

There is a vignette notebook for...

1. walking you through the calling of ROH (callROH)

2. producing various figures from the output (plotROH)

3. describing the experimental functionality to identify IBD segements between pairs of male X chromosomes (callIBD_maleX)

4. estimating population sizes from inferred ROH, using a likelihood framework (estimateNe)


Development
*************

The code used to develop this package is deposited at the `github repository <https://github.com/hringbauer/hapROH>`_.
The actual code for the software package here is organized in the folder *./package/*. In addition, there are a large number of notebooks used to test and extensively use the functionalities in *./notebooks/*, which also contain the code run for the publication.

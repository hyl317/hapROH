hapROH
==================

Scope
**************************
This software identifies runs of homozygosity in human (ancient) DNA data.

Its default parameters are optimized for human 1240K SNP capture data (ca. 1.2 million SNPs used widely in human aDNA analysis) and using 1000 Genome haplotypes as reference panel. The software is tested on a wide range of aDNA data, including 1240K capture and whole genome sequencing data downsampled to 1240K SNPs. Successful use cases include the 45k-year-old Ust Ishim man and a wide range of ancient American, Eurasian, and Oceanian DNA. The method generally works for split times of reference panel and ancient genomes up to a few 10k years, which includes all out-of-Africa populations (Attention: Neanderthals and Denisovans do not fall into that range, additionally some Subsaharan hunter-gatherer test cases did not give satisfactory results).

Currently, hapROH works on data for 1240K SNPs in unpacked or packed ``eigenstrat`` format (widely used in ancient human DNA). The software assumes pseudo-haploid (as default settings) or diploid genotype data. The recommended coverage range is >400,000 of the 1240K SNPs covered at least once.

If you have whole genome data available, you must downsample and create ``eigenstrat`` files for biallelic 1240k SNPs first.

If you are planning applications to other SNP sets or even other organisms, the parameters must be adjusted: The default parameters are optimized explicitly for human 1240K data. You can mirror our procedure to find optimal parameters described in the hapROH publication. If you need help, we are happy to share our experience.


Getting started
**************************
To get started, we prepared **quick start vignettes** as `Jupyter notebooks <https://www.dropbox.com/sh/eq4drs62tu6wuob/AABM41qAErmI2S3iypAV-j2da?dl=0>`_.

These showcase applications of hapROH that you can use as application templates. These notebooks give examples of: 

1. How to use the core functions to call ROH from ``eigenstrat`` files and generate ROH tables from results of multiple individuals: **callROH_vignette**

2. How to produce figures from the output: **plotting_vignette** - Some require additional packages. You might want to consider creating your own functions for visualizing the results in the way that works best for you)

3. How to call IBD on the X chromosome between two male X chromosomes: **callIBD_maleX_vignette**

4. How to estimate effective population sizes from inferred ROH using a likelihood framework **estimateNe_vignette**


These notebooks walk you through typical applications of hapROH. All you need is your ``eigenstrat`` file and the reference genome data (available via the link below), and you are good to go to run your own ROH calling!


Downloading reference data
**************************

hapROH currently uses global 1000 Genome data (n=5008 haplotypes from 2504 individuals), filtered to bi-allelic 1240K SNPs.  We use the .hdf5 format for the reference panel, which also contains data for the genetic map.

You can download the prepared reference data, including the necessary metadata .csv file `here: <https://www.dropbox.com/s/0qhjgo1npeih0bw/1000g1240khdf5.tar.gz?dl=0>`_ 

and unpack it with 

``tar -xvf FILE.tar.gz``

You then have to link the paths in the hapROH run parameters, as shown in the vignette notebooks.


Development
*************

The code used to develop this package is deposited at the `GitHub repository <https://github.com/hringbauer/hapROH>`_.
The actual code for the software package here is organized in the folder *./package/*. This repository also contains the code run for the hapROH publication (mostly in *./notebooks/*).

hapCon_ROH
=================================================

Introduction
****************
Runs of Homozygosity (ROH) are haploid, just as male X chromosome, and therefore can in principle be used for estimating aDNA contamination. We have developed a version of hapROH to jointly model contamination while detecting ROH. We designed an iterative approach to jointly estimate ROH and contamination rate, described in detail in the Supplementary Section 2 in `Posth et.al <https://www.nature.com/articles/s41586-023-05726-0#Sec23>`_. The implementation is termed hapCon_ROH

Input
****************
hapCon_ROH can take as input:

1) The output of `samtools mpileup <http://www.htslib.org/doc/samtools-mpileup.html>`_ or
2) The output of `BamTable <https://bioinf.eva.mpg.de/BamTable/>`_. 

Generally, we recommend to use BamTable because it provides more flexibility for preprocessing your BAM file.

Usage
******************************************
Our algorithm is wrapped in a in a simple command line, invoked by "hapCon_ROH". For more details for how to use this method, please refer to the vignette linked below.

Scope of this method
******************************************
As is clear from the introduction, our method is limited to samples with long ROH blocks, ideally the total sum of ROH blocks should exceed ~25cM.
This usually occurs for individuals from close-kin unions, or individuals that come from populations with small effective population size, such as in `Paleolithic hunter-gatheres <https://www.nature.com/articles/s41467-021-25289-w>`_ and `pre-contact Carribeans <https://www.nature.com/articles/s41586-020-03053-2>`_.
We also require that, for 1240k capture data, at least 300k SNPs should be covered, and ideally at least 400k, otherwise one may get false positive ROH blocks which then drives up contamination estimates.


One thing to keep in mind that, the default hapROH algorithm (as presented in `Ringbauer et.al <https://www.nature.com/articles/s41467-021-25289-w>`_) assumes minimal contamination. For moderately contaminated samples (e.g, between 5-10% contamination), 
it may still detect ROH blocks, but they tend to be fragmented, which biases downstream analysis (e.g, deciding whether a sample is from a close-kin union or estimating effective population size from ROH block length distribution).
If you have prior belief that your sample is a close-kin union and you observe an excess of short ROH blocks, there might be appreciable level of contamination and this modified hapROH might be more suitable.

Example Usage 1: Identify ROH blocks for contaminated samples
***************************************************************

Please refer to our short `Vignettes <https://github.com/hyl317/hapROH/blob/master/Notebooks/Vignettes/ROH_contam_tutorial.ipynb>`_.

Example Usage 2: Identify false positive ROH blocks
*****************************************************

For samples with very low coverages (e.g, around 300k SNPs covered), the called ROH may be subject to false positives. If you suspect this is the case,
it is best to run hapROH using the diploid readcounts model and manually inspect the called ROH by using our plotting function :meth:`hapsburg.figures.plot_posterior.plot_posterior_cm`.
Briefly, it plots the posterior probability of not being in ROH state along the specified genomic region and indicates "apparent heterozygote sites", which is
controled by the parameter m. It will plot a little blue dot if a site is covered by at least m reads supporting the reference allele and m reads supporting the alternative allele. 
For more details, please see the second part of `Vignettes <https://github.com/hyl317/hapROH/blob/master/Notebooks/Vignettes/ROH_contam_tutorial.ipynb>`_.




Authors: Yilei Huang, Harald Ringbauer March 2022

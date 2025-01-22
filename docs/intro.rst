Overview
============
This software package contains two primary programs and a range of functions to visualize the results:

#. ``hapROH`` identifies so-called runs of homozygosity (ROH) in ancient and present-day DNA using a panel of reference haplotypes. It uses genotype files in eigenstate format as input. This module contains functions and wrappers to call ROH and functions for downstream analysis and visualization. For downward compatibility, this software uses ``hapsburg`` as the module name.

#. ``hapCON`` estimates contamination in aDNA data of genetic males using a panel of reference haplotypes. It works directly from .bam files or the output of ``samtools mpileup``. 


Citing
**********

If you want to cite the software, use these publications:

#. For ``hapROH``: `Parental relatedness through time revealed by runs of homozygosity in ancient DNA <https://doi.org/10.1038/s41467-021-25289-w>`_ 
#. For ``hapCON``: `hapCon: Estimating contamination of ancient genomes by copying from reference haplotypes <https://doi.org/10.1101/2021.12.20.473429>`_


Contact
**********

If you have bug reports, suggestions, or general comments, please do not hesitate to contact us. We are happy to hear from you! Bug reports and user suggestions will help us improve this software.

- harald_ringbauer AT eva mpg de
- yilei_huang AT eva mpg de

(fill in AT with @ and blanks with dots)

Acknowledgments
*****************

Thank you to the two original co-authors of hapROH, Matthias Steinrücken and John Novembre. This project and its follow-ups profited immensely from Matthias' deep knowledge of HMMs and John's extensive experience in developing population genetics software. Countless discussions with both have been key to moving forward with this project. Another big thanks goes to Nick Patterson, who informed me about the benefits of working with rescaled HMMs—substantially improving the runtime of hapROH. 

We also want to acknowledge everyone who found and reported software bugs (including Mélanie Pruvost, Ke Wang, and Ruoyun Hui) and all users who reached out with general questions and requests (including Rosa Fregel, Federico Sanchez). This feedback has helped to remove errors in the program and to improve its usability. Many thanks!


Authors:
Harald Ringbauer, Yilei Huang, 2022

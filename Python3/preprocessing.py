"""
Class for preprocessing and loading the Data.
Is the interface to the Folders
Has Potential for Sub-Classes for different Types of Data, as well as factory Method.
@ Author: Harald Ringbauer, 2019, All rights reserved
"""

import allel  # Scikit Allel
import h5py   # For Processing HDF5s
import numpy as np
import pandas as pd
import os   # For creating folders

# Write General PreProcessing Class:
# Inherits one for real HDF5 Dataset: PreProcessingHDF5
# Inherits one for simulated Data.


class PreProcessing(object):
    """Class for PreProcessing the Data.
    Standard: Intersect Reference Data with Individual Data
    Return the Intersection Dataset
    """
    ref_folder = ""
    ind_folder = ""

    iid = "MA89"             # Which Individual to Analyze
    ch = 3                   # Which Chromosome to analyze

    error_rate = 0.0  # The error rate for the SNPs

    def __init__(self):
        """Initialize Class"""
        raise NotImplementedError()

    def load_data(self):
        """Return Refererence Matrix [k,l], Genotype/Readcount Matrix [2,l]
        as well as linkage map [l] """
        raise NotImplementedError()


class PreProcessingHDF5(PreProcessing):
    """Class for PreProcessing the Data.
    Standard: Intersect Reference Data with Individual Data
    Return the Intersection Dataset
    """

    out_folder = ""    # Where to Save  to
    h5_path1000g = ""  # Path of the 1000 Genome Data (For right chromosome)
    meta_path = "./../ancient-sardinia/output/meta/meta_final.csv"
    h5_path_sard = "./../ancient-sardinia/output/h5/mod_reich_sardinia_ancients_mrg_dedup_3trm_anno.h5"

    save = True
    output = True
    readcounts = False   # Whether to return Readcounts

    def __init__(self, save=True, output=True):
        """Initialize Class.
        Ind_Folder: Where to find individual
        iid & chr: Individual and Chromosome.
        save: """
        self.save = save
        self.output = output

    def load_data(self, iid="MA89", ch=6, n_ref=503):
        """Return Matrix of reference [k,l], Matrix of Individual Data [2,l],
        as well as linkage Map [l]"""
        h5_path1000g = "./Data/1000Genomes/HDF5/1240kHDF5/Eur1240chr" + \
            str(ch) + ".hdf5"
        out_folder = "./Empirical/" + \
            str(iid) + "_chr" + str(ch) + "_1000G_ROH/"

        # Set important "Steady Paths":
        h5_path_sard = self.h5_path_sard
        meta_path = self.meta_path

        # Create Output Folder if needed
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        # Load and Merge the Data
        fs = self.load_h5(h5_path_sard)
        f1000 = self.load_h5(h5_path1000g)
        i1, i2 = self.merge_2hdf(fs, f1000)

        meta_df = pd.read_csv(meta_path)
        assert(len(meta_df) == np.shape(fs["calldata/GT"])[1])  # Sanity Check

        id_obs = np.where(meta_df["iid"] == iid)[0][0]

        # All 503 EUR Samples as Reference (first Chromosome)
        ids_ref = np.arange(n_ref)
        markers = np.arange(0, len(i1))  # Which Markers to Slice out

        # Do Downsampling if needed
        # sample = np.random.binomial(1, 0.5, size=len(markers)).astype("bool") # Boolean Sample Vector
        #markers = markers[sample]

        markers_obs = i1[markers]
        markers_ref = i2[markers]

        gts_ind, gts, read_counts, r_map = self.extract_snps(out_folder, f1000, fs, ids_ref, id_obs,
                                                             markers_ref, markers_obs)
        if self.save == True:
            self.save_info(out_folder, r_map,
                           gt_individual=gts_ind, read_counts=read_counts)

        return gts_ind, gts, r_map, out_folder

     ################################################
     # Some Helper Functions

    def load_h5(self, path):
        """Load and return the HDF5 File from Path"""
        f = h5py.File(path, "r")  # Load for Sanity Check. See below!
        print("\nLoaded %i variants" % np.shape(f["calldata/GT"])[0])
        print("Loaded %i individuals" % np.shape(f["calldata/GT"])[1])
        print(list(f["calldata"].keys()))
        print(list(f["variants"].keys()))
        print(f"HDF5 loaded from {path}")
        return f

    def merge_2hdf(self, f, g, ch=1):
        """ Merge two HDF 5 f and g. Return Indices of Overlap Individuals.
        f is Sardinian HDF5,
        g the Reference HDF5
        ch: Integer, which Chromosome to use"""

        pos1 = f["variants/POS"]
        pos2 = g["variants/POS"]

        # Check if in both Datasets
        b, i1, i2 = np.intersect1d(pos1, pos2, return_indices=True)

        # Sanity Check if Reference is the same
        ref1 = np.array(f["variants/REF"])[i1]
        ref2 = np.array(g["variants/REF"])[i2]
        alt1 = np.array(f["variants/ALT"])[i1]
        alt2 = np.array(g["variants/ALT"])[i2, 0]

        # Downsample to Site where both Ref and Alt are the same
        same = (ref1 == ref2)

        both_same = (ref1 == ref2) & (alt1 == alt2)
        i11 = i1[both_same]
        i22 = i2[both_same]

        if self.output == True:
            print(f"\nIntersection on Positions: {len(b)}")
            print(f"Nr of Matching Refs: {np.sum(same)} / {len(same)}")
            print(f"Full Intersection Ref/Alt Identical: {len(i11)} / {len(both_same)}")

        return i11, i22

    def save_info(self, folder, cm_map, gt_individual=[], read_counts=[]):
        """Save Linkage Map, Readcount and Genotype Data per Individual.
        (Needed for latter Plotting)
        Genotypes Individual: If given, save as well"""

        # Save the cmap
        np.savetxt(folder + "map.csv", cm_map, delimiter=",",  fmt='%.8f')

        if len(gt_individual) > 0:
            np.savetxt(folder + "hap.csv", gt_individual,
                       delimiter=",",  fmt='%i')
        if len(read_counts) > 0:
            np.savetxt(folder + "readcounts.csv", read_counts,
                       delimiter=",",  fmt='%i')

        if self.output == True:
            print(f"Successfully saved to {folder}")

    #######################################
    # Code for saving Haplotype
    def extract_snps(self, folder, ref_hdf5, obs_hdf5, ids_ref, id_obs,
                     marker_ref, marker_obs, only_calls=True):
        """Save Folder with all relevant Information.
        Folder: Where to save to
        ref_hdf5: Reference HDF5
        obs_hdf5: Observed HDF5
        ids_ref: Indices of reference Individuals to save
        ids_obs: Indices of observed Individuals
        marker_ref: Indices of reference Markers
        marker_obs: Indices of observed Markers
        error_rate: Whether to Include an Error Rate
        only_calls: Whether to Only Include Markers with Calls"""
        assert(len(marker_ref) == len(marker_obs)
               )  # If reference and observe dataset are the same

        # Extract Reference Individuals (first haplo)
        gts = ref_hdf5["calldata/GT"][:, ids_ref, 0]
        gts = gts[marker_ref, :].T       # Important: Swap of Dimensions!!

        if self.output == True:
            print(f"Extraction of {len(gts)} Individuals Complete!")

        # Extract target individual Genotypes
        gts_ind = obs_hdf5["calldata/GT"][:, id_obs, :]
        gts_ind = gts_ind[marker_obs, :].T

        # Extract Readcounts
        read_counts = obs_hdf5["calldata/AD"][:, id_obs, :]
        read_counts = read_counts[marker_obs, :].T

        # Extract Linkage map
        r_map = np.array(obs_hdf5["variants/MAP"]
                         )[marker_obs]  # Load the LD Map

        if only_calls == True:
            called = (gts_ind[0, :] > -1)  # Only Markers with calls
            gts_ind = gts_ind[:, called]
            gts = gts[:, called]
            r_map = r_map[called]

            if self.output == True:

                print(f"Markers called {np.sum(called)} / {len(called)}")

        if self.error_rate > 0:  # Do some Error Shennenigans if needed
            e_ids = np.random.binomial(1, error_rate,
                                       size=np.shape(gts_ind)).astype("bool")  # Boolean Sample Vector
            gts_ind[e_ids] = 1 - gts_ind[e_ids]  # Do a Flip

            if self.output == True:
                print(f"Introducing {np.sum(e_ids)} Random Genotype Errors")

        # Save which Individuals were used
        # np.savetxt(folder + "ind.csv", [id_obs], delimiter=",",  fmt='%i')
        # Return Genotypes/Readcounts Individual, Genotypes Reference and Recombination Map
        return gts_ind, gts, read_counts, r_map

############################################
############################################
# Do a Factory Method that can be imported.


def load_preprocessing(p_model="SardHDF5", iid="MA89", ch=6, save=True, output=True):
    """Load the Transition Model"""

    if p_model == "SardHDF5":
        p_obj = PreProcessingHDF5(iid="MA89", ch=6, save=True, output=True)

    else:
        raise NotImplementedError("Transition Model not found!")

    return t_obj


# For testing the Module
if __name__ == "__main__":
    pp = PreProcessingHDF5(save=False, output=True)
    gts_ind, gts, r_map, out_folder = pp.load_data(iid="MA89", ch=3, n_ref=503)
    print(gts_ind[:2, :4])
    print(np.shape(gts_ind))
    print(r_map[:5])
    print(np.shape(r_map))
    print(gts[:10, :2])
    print(np.shape(gts))
    print(out_folder)
"""
Class for calling ROH from Posterior Data. Saves results as a .csv
created by Pandas.
Contains Sub-Classes, as well as factory Method.
@ Author: Harald Ringbauer, 2019, All rights reserved
"""

import numpy as np
import pandas as pd
import os


class PostProcessing(object):
    """Class that does PostProcessing of HAPSBURG output.
    Has Methods to save the output as """
    folder = ""          # The Folder to operate in
    roh_df = []          # Dataframe for Runs of Homozygosity

    cutoff = 0.8  # Cutoff Probability for ROH State
    l_cutoff = 0.01  # Cutoff [in Morgan]
    max_gap = 0.01  # The Maximum Gap Length to be Merged [in Morgan]

    merge = True  # Whether to Merge ROH Blocks
    output = True
    save = True  # Whether to save output into Folder

    def __init__(self, folder="", load=False, output=True, save=True):
        """Initialize Class.
        Load: Whether to immediately Load the Posterior Data"""
        self.folder = folder
        self.output = output
        self.save = save

        if load == True:
            self.load_data()

    def set_params(self, **kwargs):
        """Set the Parameters.
        Takes keyworded arguments"""
        for key, value in kwargs.items():
            setattr(self, key, value)

    #def set_params(self, cutoff=0.8, l_cutoff=0.01, max_gap=0.01, merge=True):
    #    """Set Parameters from outside of Class"""
    #    self.cutoff = cutoff
    #    self.l_cutoff = l_cutoff
    #    self.merge = merge
    #    self.max_gap = max_gap

    def load_data(self, folder=""):
        """Load and return genetic Map and Posterior0"""
        if len(folder) == 0:
            folder = self.folder  # Use the Folder of the Class

        # Load Posterior
        post_path = folder + "posterior0.csv"
        posterior0 = np.loadtxt(post_path, dtype="float", delimiter=",")

        # Load Linkage Map
        map_path = folder + "map.csv"

        if os.path.exists(map_path):
            r_map = np.loadtxt(
                map_path, dtype="float", delimiter=",")
        else:
            # Eventually: Runtime Warning
            print("No Genetic Map found!!! Defaulting...")
            r_map = np.arange(len(self.posterior0))

        assert(len(r_map) == len(posterior0))  # Sanity Check
        print(f"Successfully loaded for PP. from {folder}")

        return r_map, posterior0

    def merge_called_blocks(self, df, max_gap=0):
        """Merge Blocks in Dataframe df and return merged Dataframe"""
        if len(df) == 0:
            return df  # In case of empty dataframe don't do anything

        if max_gap == 0:
            max_gap = self.max_gap

        df_n = df.drop(df.index)  # Create New Data frame with all raws removed
        row_c = df.iloc[0, :].copy()

        # Iterate over all rows, update blocks if gaps small enough
        for index, row in df.iterrows():
            if row["StartM"] - row_c["EndM"] < max_gap:
                row_c["End"] = row["End"]
                row_c["EndM"] = row["EndM"]
                row_c["length"] = row_c["End"] - row_c["Start"]
                row_c["lengthM"] = row_c["EndM"] - row_c["StartM"]

            else:  # Save and go to next row
                df_n.loc[len(df_n)] = row_c  # Append a row to new df
                row_c = row.copy()

        df_n.loc[len(df_n)] = row_c   # Append the last row

        if self.output == True:
            print(f"Merged n={len(df) - len(df_n)} gaps < {max_gap} M")
        return df_n

    def modify_posterior0(self, posterior0):
        """Load and return the posterior."""
        roh_post = 1 - np.exp(posterior0)  # Go to non-logspace probability
        return roh_post

    def call_roh(self, ch=0, iid=""):
        """Call ROH of Homozygosity from Posterior Data
        bigger than cutoff
        log: Whether Posterior is given in log space"""
        r_map, posterior0 = self.load_data()
        roh_post = self.modify_posterior0(posterior0)
        roh = roh_post > self.cutoff

        if self.output == True:
            frac_roh = np.mean(roh)
            print(f"Fraction Markers in ROH: {frac_roh:.4f}")

        # Identify Stretches by going up and going down:
        x1 = np.hstack([[False], roh, [False]]).astype("int")  # padding
        d = np.diff(x1)
        starts = np.where(d == 1)[0]
        ends = np.where(d == -1)[0]
        l = ends - starts

        ends_map = r_map[ends - 1]  # -1 to stay within bounds
        starts_map = r_map[starts]
        l_map = ends_map - starts_map

        full_df = pd.DataFrame({'Start': starts, 'End': ends,
                                'StartM': starts_map, 'EndM': ends_map, 'length': l,
                                'lengthM': l_map, 'iid': iid, "ch": ch})
        df = full_df[full_df["lengthM"] > self.l_cutoff]  # Cut out long blocks

        # Merge Blocks in Postprocessing Step
        if self.merge == True:
            df = self.merge_called_blocks(df)

        if self.output == True:
            print(f"Called n={len(df)} ROH Blocks > {self.l_cutoff * 100} cM")
            l = np.max(df["lengthM"])
            print(f"Longest Block: {l *100:.3f}")

        self.df = df
        if self.save == True:
            #save_folder = self.folder + "roh.csv"
            save_folder = os.path.join(self.folder, "roh.csv")
            df.to_csv(save_folder, index=False)

            if self.output == True:
                print(f"Successfully saved to {save_folder}")

        return df

    def clean_up(self, full=True):
        """Removes all additional Data other than the
        ROH Calls and the ROH Ground Truth (To save space)"""
        keep_files = ["roh.csv", "roh_gt.csv"]
        folder = self.folder

        for the_file in os.listdir(folder):   # Walk through the Files
            file_path = os.path.join(folder, the_file)

            if os.path.isfile(file_path) and (the_file not in keep_files):
                os.unlink(file_path)   # Delete the File


#######################################################


class MMR_PostProcessing(PostProcessing):
    """Class that does PostProcessing of HAPSBURG output.
    Same as PostProcessing but load Posterior differently"""

    def modify_posterior0(self, posterior0):
        """Load and return the posterior. Don't do anything"""
        roh_post = posterior0
        return roh_post

#######################################################
#######################################################


def load_Postprocessing(folder="", method="Standard", output=True, save=True):
    """Factory Method for PostProcessing class"""
    if method == "Standard":
        pp = PostProcessing(folder, output=output, save=save)
    elif method == "MMR":
        pp = MMR_PostProcessing(folder, output=output, save=save)
    else:
        raise RuntimeError(f"Postprocessing method {method} not available!")

    return pp


#######################################################
# Do testing
if __name__ == "__main__":
    # d05e e: Error Introduced. d05: Downsampled
    folder = "./Simulated/1000G_Mosaic/TSI/ch3_10cm/output/iid0/chr3/"
    pp = PostProcessing(folder=folder)
    pp.call_roh()
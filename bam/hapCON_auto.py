# run female hapCON estimate from mpileup results

import numpy as np
import argparse
import time
import sys
import os
import shutil

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run hapROH(on autosomes) from mpileup output')
    parser.add_argument('--mpileup', action="store", dest="mpath", type=str, required=False,
                        help="Basepath to a list of mpileup file")
    parser.add_argument('--bamTable', action="store", dest="bamTable", type=str, required=False,
                        help="Basepath to a list of BamTable file")          
    parser.add_argument('-i', action="store", dest="iid", type=str, required=True,
                        help="IID of the target individual.")
    parser.add_argument('-p', action="store", dest="processes", type=int, required=False, default=1,
                        help="Number of processes to use.")
    parser.add_argument('--niter', action="store", dest="niter", type=int, required=False, default=5,
                        help="Maximum number of iterations.")
    parser.add_argument('--tol', action="store", dest="tol", type=float, required=False, default=0.005,
                        help="Stopping criterion. If the estimated contamination rates between two consecutive iterations differ less than this value, stop iteration.")
    parser.add_argument('--prefix', action="store", dest="prefix", type=str, required=False, default=None,
                        help="prefix of the output.")
    args = parser.parse_args()

    #sys.path.insert(0, "/mnt/archgen/users/yilei/tools/hapROH/package")
    from hapsburg.PackagesSupport.hapsburg_run import hapsb_ind
    from hapsburg.PackagesSupport.hapsburg_run import hapsb_femaleROHcontam_preload
    from hapsburg.PackagesSupport.parallel_runs.helper_functions import multi_run
    from hapsburg.PackagesSupport.loadEigenstrat.saveHDF5 import mpileup2hdf5, bamTable2hdf5
    from multiprocessing import set_start_method
    set_start_method("spawn")


    iid = args.iid
    p = args.processes
    mpileup_path= args.mpath
    bamTable_path = args.bamTable

    if not mpileup_path and not bamTable_path:
        print('Need to at least provide one of pileup files or BamTable files.')
        sys.exit()

    basepath = ""
    input_path = mpileup_path if mpileup_path else bamTable_path
    if not input_path.endswith('/'):
        basepath = input_path[:input_path.rindex("/")]
        input_path += '/'
    else:
        basepath = input_path[:input_path.rindex("/", end=len(input_path)-1)]
    
    if not os.path.exists(f'{basepath}/hdf5'):
        os.makedirs(f'{basepath}/hdf5')
    print(f'saving hdf5 files in {basepath}/hdf5')

    t1 = time.time()
    if mpileup_path:
        prms = [ [input_path + f'{iid}.chr{ch}.mpileup', 
            f'/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/chr{ch}.hdf5',
            iid, -np.inf, np.inf, f'{basepath}/hdf5', False] for ch in range(1, 23)]
        results = multi_run(mpileup2hdf5, prms, p)
    else:
        prms = [ [input_path + f'{iid}.chr{ch}.BamTable', 
            f'/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/chr{ch}.hdf5',
            iid, -np.inf, np.inf, f'{basepath}/hdf5', False] for ch in range(1, 23)]
        results = multi_run(bamTable2hdf5, prms, p)
    err = np.mean(np.array([err for err, _, _ in results]))
    numSitesCovered = sum([n for _, n, _ in results])
    print(f'finished reading input files, takes {round(time.time()-t1, 3)}s')
    print(f'estimated genotyping error: {err}')

    ################################### call ROH ##################################
    hapsb_ind(iid, chs=range(1,23), 
        path_targets_prefix = f"{basepath}/hdf5",
        h5_path1000g = "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/chr", 
        meta_path_ref = "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/meta_df_all.csv",
        folder_out=f"{basepath}/hapRoh_iter/", prefix_out="",
        e_model="readcount_contam", p_model="SardHDF5", post_model="Standard",
        processes=args.processes, delete=True, output=True, save=True, save_fp=False, 
        n_ref=2504, diploid_ref=True, exclude_pops=[], readcounts=True, random_allele=False,
        c=0.05, roh_min_l_final=0.05, roh_in=1, roh_out=20, roh_jump=300, e_rate=err, e_rate_ref=1e-3, 
        logfile=True, combine=True, file_result="_roh_full.csv")
    
    ######################################################################################


    ################## Use the called ROH region to estimate contamination ###############
    contam, se, chunks, sumROH = hapsb_femaleROHcontam_preload(iid, f"{basepath}/hapRoh_iter/{iid}_roh_full.csv",
        "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/chr", 
        "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/meta_df_all.csv",
        hdf5_path=f"{basepath}/hdf5", e_rate=err, processes=p, prefix=args.prefix, logfile=False)

    # iterate the process if necessary
    if contam >= 0.05:
        print(f'estimated contamination rate {round(contam, 6)} greater than 0.05, start iteration.')
        diff = np.inf
        niter = 1
        maxIter = args.niter
        contam_prev = contam
        tol = args.tol
        while diff > tol and niter < maxIter:
            hapsb_ind(iid, chs=range(1,23), 
                path_targets_prefix = f"{basepath}/hdf5",
                h5_path1000g = "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/chr", 
                meta_path_ref = "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/meta_df_all.csv",
                folder_out=f"{basepath}/hapRoh_iter/", prefix_out="",
                e_model="readcount_contam", p_model="SardHDF5", post_model="Standard",
                processes=p, delete=True, output=True, save=True, save_fp=False, 
                n_ref=2504, diploid_ref=True, exclude_pops=[], readcounts=True, random_allele=False,
                c=contam_prev, roh_in=1, roh_out=20, roh_jump=300, e_rate=err, e_rate_ref=1e-3, 
                logfile=True, combine=True, file_result="_roh_full.csv")
            contam, se, chunks, sumROH = hapsb_femaleROHcontam_preload(iid, f"{basepath}/hapRoh_iter/{iid}_roh_full.csv",
                "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/chr", 
                "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/meta_df_all.csv",
                hdf5_path=f"{basepath}/hdf5", e_rate=err, processes=p, prefix=args.prefix, logfile=False)
            niter += 1
            diff = abs(contam_prev - contam)
            print(f'iteration {niter} done, prev contam: {round(contam_prev, 6)}, current contam: {round(contam, 6)}')
            contam_prev = contam

        converged = diff <= tol
        if converged:
            print(f'contamination rate converged after {niter} iterations.')
        else:
            print(f'contamination rate did not converge. Try increase the maxIter param.')
    else:
        converged = True


    if args.prefix:
        fileName = f'{iid}.{args.prefix}.hapCON_ROH.txt'
    else:
        fileName = f'{iid}.hapCON_ROH.txt'
    with open(f'{basepath}/{fileName}', 'w') as f:
        f.write(f'Method1: Fixing genotyping error rate at {round(err, 6)}\n')
        f.write(f'\tNumber of ROH blocks found: {len(chunks)}\n')
        f.write(f'\tTotal length of ROH after trimming: {round(100*sumROH,3)}cM\n')
        f.write(f'\tMLE for contamination using BFGS: {round(contam, 6)} ({round(contam-1.96*se, 6)} - {round(contam+1.96*se, 6)})\n')

    hapsb_ind(iid, chs=range(1,23), 
                path_targets_prefix = f"{basepath}/hdf5",
                h5_path1000g = "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/chr", 
                meta_path_ref = "/mnt/archgen/users/yilei/Data/1000G/1000g1240khdf5/all1240/meta_df_all.csv",
                folder_out=f"{basepath}/hapRoh_iter/", prefix_out="",
                e_model="readcount_contam", p_model="SardHDF5", post_model="Standard",
                processes=p, delete=False, output=True, save=True, save_fp=False, 
                n_ref=2504, diploid_ref=True, exclude_pops=[], readcounts=True, random_allele=False,
                c=contam_prev, roh_in=1, roh_out=20, roh_jump=300, e_rate=err, e_rate_ref=1e-3, 
                logfile=True, combine=True, file_result="_roh_full.csv")

    # clean up
    shutil.rmtree(f'{basepath}/hdf5') # this is a hack


    #####################################################################################
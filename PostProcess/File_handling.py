############### NOTE! ###############
# this file is untested.            #
# many of the functions here were   #
# written for older versions of the #
# pipeline and have not been fixed  #
# yet                               #
#####################################


import nibabel as nib
import pandas as pd
import scipy.io as spio


def read_atlas(path):
    raise NotImplementedError


def read_niftii(path):
    raise NotImplementedError


def make_hemi_stat_nifti(values, atlas):
    raise NotImplementedError


def convert_labels_to_names(labels, atlas):
    raise NotImplementedError


def transpose_dict(d):
    new_d = {}
    for k, v in d.items():
        for i in v:
            new_d[v] = k
    return new_d


def read_info(dataset, info_paths):
    sub_infos = []
    if dataset == 'HCP':
        for i in info_paths:
            sub_info_res = pd.read_csv(info_paths)
            sub_info = sub_info_res.set_index('Subject')
            sub_infos.append(sub_info)
    else:
        sub_info = pd.read_csv(info_paths[0])
        sub_info = sub_info.set_index('Column1')
        sub_info.index = [i.replace('subj', 'Subj') for i in sub_info.index]
        sub_infos.append(sub_info)
    return sub_infos

def get_all_cm(stats, dataset, base_path):
    """NOTE!
    This function is from an older version of the code and should be deprecated!"""

    all_cm = {'L': [], 'R': [], 'comis': []}
    for sub in stats.index:
        for hemi in ['L', 'R', 'comis']:
            cm = spio.loadmat(fr"{base_path}/{dataset}/{sub}/T1w/Diffusion/cm_{hemi}_thesis.mat")['cm']
            all_cm[hemi].append(cm)
            cm[cm < 0] = 0
            all_cm[hemi].append(cm)
    return all_cm


def get_tck_tracts(tracts, data):
    dif = nib.load(data)
    pixdim = dif.header['pixdim'][1]
    tck = nib.streamlines.load(tracts)
    tck = tck.tractogram
    tck_converted = tck.apply_affine(np.linalg.inv(dif.affine))
    st = np.array([i for i in tck_converted.streamlines])
    return st, pixdim
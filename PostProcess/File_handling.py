import pandas as pd


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


def read_info(dataset):
    sub_info_res = None
    if dataset == 'HCP':
        sub_info_res = pd.read_csv(
            "/state/partition1/home/ronniek/ronniek/HCP/RESTRICTED_ronniek_4_28_2019_8_15_50.csv")
        sub_info = pd.read_csv("/state/partition1/home/ronniek/ronniek/HCP/HCPsubList.csv")
        sub_info_res = sub_info_res.set_index('Subject')
        sub_info = sub_info.set_index('Subject')
    else:
        sub_info = pd.read_csv("/state/partition1/home/ronniek/ronniek/theBase/theBase_ques.csv")
        sub_info = sub_info.set_index('Column1')
        sub_info.index = [i.replace('subj', 'Subj') for i in sub_info.index]
    if sub_info_res:
        return sub_info, sub_info_res
    return sub_info

def get_all_cm(stats, dataset):
    all_cm = {'L': [], 'R': [], 'comis': []}
    for sub in stats.index:
        for hemi in ['L', 'R', 'comis']:
            cm = \
            spio.loadmat(fr"/state/partition1/home/ronniek/ronniek/{dataset}/{sub}/T1w/Diffusion/cm_{hemi}_thesis.mat")[
                'cm']
            all_cm[hemi].append(cm)
            cm[cm < 0] = 0
            all_cm[hemi].append(cm)
    return all_cm
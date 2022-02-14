import traceback
import nibabel as nb
import pandas as pd
import random
import numpy as np
import os
from collections import defaultdict
import scipy.io as spio
import networkx as nx
from glob import glob
from .PostProcess import File_handling, Network


def look_around(point, parc):
    get_min = lambda x: max(0, point[x] - 2)
    get_max = lambda x: min(np.shape(parc)[x], point[x] + 2)
    around = parc[get_min(0): get_max(0),
             get_min(1): get_max(1),
             get_min(2): get_max(2)]
    around = around.reshape(-1)
    around = around[around > 0]
    if len(around) == 0:
        return 0
    d = defaultdict(set)
    {d[np.sum(around == i)].add(i) for i in around}
    return random.choice(list(d[max(d.keys())]))


def make_hemis_sum(tracts, data, atlas, nodes=0, total=30000):
    tract_data, pixdim = File_handling.get_tck_tracts(tracts, data)
    parc = nb.load(atlas).get_data()
    # aal_stats = pd.read_csv('/state/partition1/home/ronniek/ronniek/AAL2_data/AAL150.txt', header=None,
    #                        names=['num', 'area', 'label', 'hemi'], delimiter=' ')
    aal_stats = pd.read_csv(f'/state/partition1/home/ronniek/ronniek/AAL2_data/kmeans{nodes}.txt', header=0,
                            delimiter=' ',
                            names=['num', 'area'])
    aal_stats = aal_stats.set_index('num')
    hemi = []
    for i in aal_stats.index:
        if 0 < int(i) / 1000 < 4:
            hemi.append("L")
        elif int(i) / 1000 > 4:
            hemi.append('R')
        else:
            hemi.append("")
    aal_stats['hemi'] = hemi
    # aal_stats['hemi'] = [i[-1] for i in aal_stats['area']]
    labels = {}
    cms = {}
    for hemi in ['L', 'R']:
        labels[hemi] = [x for x in np.unique(parc) if x > 0 and aal_stats['hemi'][x] == hemi]
        cms[hemi] = np.zeros((len(labels[hemi]), len(labels[hemi])))
    cms['comis'] = np.zeros((len(labels['L']), len(labels['R'])))

    random.shuffle(tract_data)
    tract_data = list(tract_data)
    ntracts = len(tract_data)
    while len(tract_data) > 0:
        tract = tract_data.pop()
        start = [int(round(tract[0][0])), int(round(tract[0][1])), int(round(tract[0][2]))]
        end = [int(round(tract[-1][0])), int(round(tract[-1][1])), int(round(tract[-1][2]))]
        if parc[start[0], start[1], start[2]] not in labels['L'] + labels['R']:
            start = look_around(start, parc)
        else:
            start = parc[start[0], start[1], start[2]]
        if not parc[end[0], end[1], end[2]] in labels['L'] + labels['R']:
            end = look_around(end, parc)
        else:
            end = parc[end[0], end[1], end[2]]
        if start != 0 and end != 0:
            if aal_stats['hemi'][start] == aal_stats['hemi'][end]:
                if start != end and total > 0:
                    total = total - 1
                    hemi = aal_stats['hemi'][start]
                    cms[hemi][labels[hemi].index(start), labels[hemi].index(end)] += 1
                    cms[hemi][labels[hemi].index(end), labels[hemi].index(start)] += 1
            else:
                if aal_stats['hemi'][start] == 'L':
                    l = labels['L'].index(start)
                    r = labels['R'].index(end)
                else:
                    r = labels['R'].index(start)
                    l = labels['L'].index(end)
                cms['comis'][l, r] += 1
    return cms, ntracts, labels






def get_odf_comis(path):
    corpus = rf'{path}/corpus_mask.nii.gz'
    brain = rf'{path}/brain_mask.nii.gz'
    brain = nb.load(brain)
    pixdim = brain.header['pixdim'][1]
    corpus_size = np.sum(nb.load(corpus).get_data())
    brain_size = np.sum(brain.get_data())
    brain_size_mm = pixdim * brain_size
    return ((corpus_size ** 0.5) / (brain_size ** (1 / 3))) * 100, brain_size_mm


def get_comis(path, ntracts):
    corpus_tracts = rf"{path}/corpus_tracts_super_cleaned_noatlas.tck"
    tracts = nb.streamlines.load(corpus_tracts)
    print(ntracts, len(tracts.tractogram))
    return (len(tracts.tractogram) / ntracts) * 100

if __name__ == '__main__':
    dataset = 'HCP'
    nodes = 150
    subjects = glob(fr'/state/partition1/home/ronniek/ronniek/{dataset}/*/T1w/Diffusion/')
    subjects = [i for i in subjects if os.path.isfile(fr"{i}kmeans_atlas{nodes}.nii.gz")]
    stats = defaultdict(list)
    count = 0
    for subject in subjects:
        subject_stats = {}
        try:
            # if 1 == 1:
            tracts = os.path.join(subject, 'tracts.tck')
            data = os.path.join(subject, 'brain.nii.gz')
            atlas = os.path.join(subject, f'kmeans_atlas{nodes}.nii.gz')
            tracts_noatlas = os.path.join(subject, 'tracts_noatlas_noCST.tck')
            cml = np.zeros((nodes, nodes))
            cmr = np.zeros((nodes, nodes))
            cmc = np.zeros((nodes, nodes))
            tract_noatlas_data, pixdim_noatlas = File_handling.get_tck_tracts(tracts_noatlas, data)
            msps = 0
            msps = []
            for _ in range(100):
                cms, ntracts, labels = make_hemis_sum(tracts, data, atlas, nodes=nodes)
                msps.append(Network.get_msp_both_hemis(cms))
                cml += cms['L']
                cmr += cms['R']
                cmc += cms['comis']
            subject_stats['msp'] = np.mean(msps)

            subject_stats['msp_std'] = np.std(msps)
            odf, brain_size = get_odf_comis(subject)
            subject_stats['brainsize'] = brain_size
            subject_stats['odf'] = odf
            ntracts_noatlas = len(tract_noatlas_data)
            subject_stats['comis'] = get_comis(subject, ntracts_noatlas)
            subject_stats['subname'] = subject.split('/')[7]
            subject_stats['ntracts'] = ntracts_noatlas
            for hemi, cm in zip(['L', 'R', 'comis'], [cml, cmr, cmc]):
                cms[hemi] = cm / 100

            for key in subject_stats.keys():
                stats[key].append(subject_stats[key])
            for hemi in ['L', 'R']:
                spio.savemat(os.path.join(subject, f'cm_{hemi}_{nodes}.mat'), {'cm': cms[hemi], 'labels': labels[hemi]})
            spio.savemat(os.path.join(subject, f'cm_comis_{nodes}.mat'), {'cm': cms['comis']})

            print('done', subject)
            count += 1
        except Exception as e:
            print(subject, e)
            traceback.print_exc()
    print(count)

    stats = pd.DataFrame(stats)
    stats.set_index('subname')
    stats.to_csv(
        fr'/state/partition1/home/ronniek/ronniek/ComisCortical/results/connectivity_new_{dataset}kmeans{nodes}.csv')

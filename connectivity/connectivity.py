import nibabel as nb
from dipy.io.streamline import load_tractogram
from dipy.tracking import utils
import numpy as np
import networkx as nx
import random
import collections
import os
from pathlib import Path
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob


def get_cm(sub_path, run_name, filter_labels=None):
    """
    :param sub_path: path to subject's directory
    :param run_name: name under which the run's files are saved
    :param filter_labels: iterable, labels that should not be included in the cm
    :return: matrix, dictionary with pairs of nodes and indexes for tracts connecting them, matrix labels
    """
    data = nb.load(
        fr'{sub_path}/brain/{run_name}.nii.gz')

    labels = nb.load(
        fr'{sub_path}/atlas/rBNA.nii').get_fdata()
    if filter_labels:
        labels[np.isin(labels, filter_labels)] = 0
    new_labels, lookup = utils.reduce_labels(labels)

    tracts = load_tractogram(
        fr'{sub_path}/tracts/{run_name}.tck', data)
    tracts = tracts.streamlines

    m, grouping = utils.connectivity_matrix(tracts, data.affine, new_labels, return_mapping=True,
                                            mapping_as_streamlines=True)
    m = m[1:, 1:]
    new_grouping = {(k[0] - 1, k[1] - 1): v for k, v in grouping.items() if 0 not in k}
    new_lookup = lookup[1:]
    return m, new_grouping, new_lookup


def get_efficiency(cm=None, g=None):
    """
    :param cm: matrix
    :param g: networkx graph
    enter either a graph or a matrix
    :return: metwork efficiency for that matrix/graph
    """
    if cm:
        cm = np.array(cm)
        cm = (cm/np.sum(cm))*100
        cm2 = 1 / cm
        cm2[cm == 0] = 0
        g = nx.from_numpy_matrix(cm2)
    short_paths = dict(nx.all_pairs_dijkstra_path_length(g))
    d = []
    for i in short_paths.keys():
        d.extend([short_paths[i][x] for x in short_paths[i].keys() if x != i])
    eff = 1/np.array(d)
    eff[np.array(d) == 0] = 0
    eff = np.mean(eff)
    return eff


def subsample_tracts(m, grouping, ntracts, label_group1, label_group2=()):
    labels = []
    for k, v in grouping.items():
        if (k[0] in label_group1 and k[1] in label_group1) or (k[0] in label_group2 and k[1] in label_group2):
            labels.append(k)
    sample = random.sample(labels, k=ntracts)
    sample_count = collections.Counter(sample)
    cm = np.zeros(m)
    for k, v in sample_count.items():
        cm[k] = v
    for i in label_group1:
        for j in label_group2:
            cm[i, j] = m[i, j]
            cm[j, i] = m[j, i]
    return cm + m


def sort_matrix_by_hemis(cm, lookup, grouping, atlas_stats):
    sorted_labels = sorted(atlas_stats.index[atlas_stats['hemi'] == 'L']) + sorted(
        atlas_stats.index[atlas_stats['hemi'] == 'R'])

    new_indices = [list(lookup).index(i) for i in sorted_labels]

    grouping_key = {j:i for i, j in enumerate(new_indices)}
    cm = cm[:, new_indices]
    cm = cm[new_indices, :]
    lookup = lookup[new_indices]
    new_grouping = {}
    for k, v in grouping.items():
        if k[0] in grouping_key.keys() and k[1] in grouping_key.keys():
            new_grouping[grouping_key[k[0]], grouping_key[k[1]]] = v
    return cm, lookup, new_grouping


def devide_cm_into_hemis(cm, lookup):
    hemi1 = cm[:len(lookup)//2, :len(lookup)//2]
    lookup1 = lookup[:len(lookup)//2]

    hemi2 = cm[len(lookup) // 2:, len(lookup) // 2:]
    lookup2 = lookup[len(lookup) // 2:]

    return hemi1, hemi2, lookup1, lookup2


def create_cms(sub_path, run_name, atlas_path, alternative_save=None):
    if alternative_save is None:
        alternative_save=run_name
    save_name = os.path.join(sub_path, 'cm', alternative_save)
    Path(os.path.join(sub_path, 'cm')).mkdir(exist_ok=True)
    m, grouping, lookup = get_cm(sub_path, run_name)
    atlas_stats = read_atlas(atlas_path)
    np.save(save_name + "_unsorted", m)
    np.save(save_name + '_lookup_unsorted', lookup)
    save_obj(grouping, save_name + '_grouping_unsorted')
    m, lookup, grouping = sort_matrix_by_hemis(m, lookup, grouping, atlas_stats)
    np.save(save_name, m)
    np.save(save_name + '_lookup', lookup)
    save_obj(grouping, save_name + '_grouping')
    return m, lookup, grouping


def save_obj(obj, path):
    with open(path + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(path):
    with open(path + '.pkl', 'rb') as f:
        return pickle.load(f)


def read_atlas(path):
    aal_stats = pd.read_csv(path, header=None,
                            names=['num', 'area', 'label', 'hemi'], delimiter=',')
    #aal_stats = pd.read_csv(path, header=None,
    #                        names=['num', 'area', 'hemi', 'size'], delimiter=' ')
    aal_stats['hemi'] = [i[-1] for i in aal_stats['area']]
    return aal_stats


def show_matrix(matrix, lookup, atlas_path):
    plt.figure(figsize=(15, 15))
    atlas_stats = read_atlas(atlas_path)
    area_names = atlas_stats['area'][lookup]
    plt.imshow(matrix)
    plt.colorbar()
    plt.yticks(ticks=range(len(area_names)), labels=list(area_names), size=7)
    plt.xticks(ticks=range(len(area_names)), labels=list(area_names), size=7, rotation=90)
    plt.show()

if __name__ == "__main__":
    subs = glob(r'/path/to/sub/folder')
    atlas_path = '/path/to/atlas'

    for sub in subs:
        if os.path.isfile(fr'{sub}/atlas/rBNA.nii'):
            try:
                m, lookup, grouping = create_cms(sub, 'HCP', atlas_path, alternative_save="rBNA")
                print(sub)
            except FileNotFoundError:
                print(sub + " has no files")
            except ValueError:
                print(sub + " value error")
            except nb.filebasedimages.ImageFileError:
                print(sub + " corrupt file")



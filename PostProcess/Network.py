from . import File_handling
import bct
import networkx as nx
import numpy as np
import scipy.io as spio
from scipy.stats import pearsonr
from tqdm import tqdm
import random


def get_all_graphs(stats, dataset, return_cm=True):
    all_cm = {'L': [], 'R': [], 'comis': []}
    graphs = []
    for sub in stats.index:
        g = {}
        for hemi in ['L', 'R']:
            cm = spio.loadmat(fr"/state/partition1/home/ronniek/ronniek/{dataset}/{sub}/T1w/Diffusion/cm_{hemi}.mat")[
                'cm']
            cm = cm / np.sum(cm) * 100
            cm2 = 1 / cm
            cm2[cm == 0] = 0
            g[hemi] = nx.from_numpy_matrix(cm2)
        graphs.append(g)
    if return_cm:
        return graphs, all_cm
    return graphs


def get_msp_both_hemis(cms):
    msps = []
    for hemi in ['L', 'R']:
        cm = np.array(cms[hemi])
        cm2 = 1 / cm
        cm2[cm == 0] = 0
        cm2 = 200 * cm2
        g = nx.from_numpy_matrix(cm2)
        msp = dict(nx.all_pairs_dijkstra_path_length(g))
        meanDs = []
        for i in msp:
            pairs = msp[i]
            d = 1 / np.array([x for x in pairs.values() if x > 0])
            if len(d) > 0:
                meanDs.append(np.mean(d))
        msps.append(1 / np.mean(np.array(meanDs)))
    return np.mean(msps)


def get_efficiency_both_hemis_from_cm(cm):
    raise NotImplementedError

def get_efficiency_both_hemis(graphs):
    g_eff = []
    for hemi in ['L', 'R']:
        g = graphs[hemi]
        g_eff.append(get_graph_efficiency(g))
    return np.mean(g_eff)


def get_graph_efficiency(g):
    short_paths = dict(nx.all_pairs_dijkstra_path_length(g))
    d = []
    for i in short_paths.keys():
        d.extend([short_paths[i][x] for x in short_paths[i].keys() if x != i])
    eff = 1 / np.array(d)
    eff[np.array(d) == 0] = 0
    eff = np.mean(eff)
    return eff


def leave_one_out(graphs, stats, labels, save=None):
    # graphs - list pf nx graphs
    # stats - pandas
    # labels - dict in the shape of {'L': [array_of_labels], 'R': [array_of_labels]}
    r_vals_per_node = {}
    for node_to_remove in tqdm(np.concatenate(labels['L'], labels['R'])):
        efficiency = []
        for g, sub in zip(graphs, stats.index):
            current_g = {}
            for hemi in ['L', 'R']:
                indices_to_remove = np.where(labels[hemi] == node_to_remove)[0]
                graph = g[hemi].copy()
                graph.remove_nodes_from(indices_to_remove)
                current_g[hemi] = graph
            efficiency.append(get_efficiency_both_hemis(current_g))
        comis = stats['comis']
        r = pearsonr(comis, efficiency)
        r_vals_per_node[node_to_remove] = r
        if save:
            np.save(save, r_vals_per_node)
        return r_vals_per_node


def remove_nodes_rvals(graphs, stats, labels, label_scores, n_perm = 70, rand_run=True, save=None):
    scores = np.unique(list(label_scores.keys()))
    rvals = []
    nodes_to_remove = []
    for i in tqdm(scores):
        nodes_to_remove.extend(label_scores[i])
        ncomis = []
        efficiency = []
        for g, sub in zip(graphs[:200], stats.index[:200]):
            ncomis.append(stats['comis'][sub])

            current_g = {}
            for hemi in ['L', 'R']:
                indices_to_remove = [j for i in nodes_to_remove for j in np.where(labels == i)[0] if i in labels]
                graph = g[hemi].copy()
                graph.remove_nodes_from(indices_to_remove)
                current_g[hemi] = graph
            efficiency.append(get_efficiency_both_hemis(current_g))
        rvals.append(pearsonr(np.array(ncomis)[~np.isnan(efficiency)], np.array(efficiency)[~np.isnan(efficiency)]))
        if save:
            np.save(save, rvals)

        if rand_run:
            rand_rvals = []
            for _ in range(n_perm):
                rand_rvals_perm = []
                nodes_to_remove = []

                for score in tqdm(scores):
                    no_of_nodes_to_remove = len(label_scores[score])
                    nodes_to_remove.extend(random.sample(list(labels), k=no_of_nodes_to_remove))
                    ncomis = []
                    efficiency = []
                    for g, sub in zip(graphs[:200], stats.index[:200]):
                        ncomis.append(stats['comis'][sub])

                        current_g = {}
                        for hemi in ['L', 'R']:
                            indices_to_remove = [j for i in nodes_to_remove for j in np.where(labels == i)[0] if
                                                 i in labels]
                            graph = g[hemi].copy()
                            graph.remove_nodes_from(indices_to_remove)
                            current_g[hemi] = graph

                        efficiency.append(get_efficiency_both_hemis(current_g))
                    rand_rvals_perm.append(
                        pearsonr(np.array(ncomis)[~np.isnan(efficiency)], np.array(efficiency)[~np.isnan(efficiency)]))

                rand_rvals.append(rand_rvals_perm)
                if save:
                    np.save(save, rand_rvals)
            return rvals, rand_rvals
    return rvals


def get_strongest_value_nodes(vals_per_node, sd_factor=1):
    dat = vals_per_node.values()
    ma = np.max(dat) - np.std(dat)
    mi = np.min(dat) + np.std(dat)

    strong_nodes = {}
    for k, v in vals_per_node.items():
        if (v > ma) or (v < mi):
            strong_nodes[k] = (v[0][0])
    return strong_nodes


def make_cm_from_parts(all_cm):
    cm = []
    for l, r, comis in zip(all_cm['L'], all_cm['R'], all_cm['comis']):
        cm.append(np.bmat([[l, comis], [comis.T, r]]))
    return cm


def get_scores_for_sub(stats, labels, all_cm=None, dataset=None):
    if (not all_cm) and dataset:
        all_cm = File_handling.get_all_cm(stats, dataset)
    scores = []
    for cm, sub in tqdm(zip(all_cm, stats.index)):
        cm = np.array(cm)
        s_coreness = np.zeros(len(cm))
        s_cores = np.sum(cm, 0)
        i = 1
        while np.any(s_cores > 0):
            score_mat, y = bct.score_wu(cm, i)
            s_cores = np.sum(score_mat, 0)
            s_coreness[np.array(s_cores).squeeze() > 0] = i
            i += 1
        all_scores = {l: score for l, score in zip(labels, s_coreness)}
        scores.append(all_scores)
    return scores


def rich_club(meanmat, n_iter=1000):
    rich_c = bct.core.rich_club_wu(meanmat)
    if n_iter > 0:
        rand_rich_club = []
        full_rich = None
        for _ in tqdm(range(n_iter)):
            cm = np.copy(meanmat)
            tril = np.ravel_multi_index(np.tril_indices(len(cm), k=1), np.shape(cm))
            indices = np.copy(tril)
            random.shuffle(indices)
            cm = cm.reshape(-1)
            cm[tril] = cm[indices]
            cm = cm.reshape(np.shape(meanmat))
            cm = np.tril(cm) + np.triu(cm.T, 1)
            rand_rich_club.append(bct.core.rich_club_wu(cm))
            pad = len(max(rand_rich_club, key=len))
            full_rich = np.empty((len(rand_rich_club), pad))
            full_rich[:] = np.NaN
            for i, j in enumerate(rand_rich_club):
                full_rich[i][0:len(j)] = j
            while np.all(np.isnan(full_rich[:, -1])):
                full_rich = np.delete(full_rich, -1, 1)
        return rich_c, full_rich
    return rich_c


def get_mean_mat(all_cm):
    count = np.count_nonzero(all_cm, 0)
    meanmat = np.mean(all_cm, 0)
    meanmat[count < 0.75 * np.shape(all_cm)[0]] = 0
    return meanmat


def get_pval_indices(dat, rand_dat):
    length = min(np.shape(rand_dat)[1], len(dat))
    pvals = np.sum(rand_dat[:, :length] > np.tile(dat[:length], (len(rand_dat), 1)), 0) / len(rand_dat)
    indices = np.where(pvals < 0.05)[0]
    areas = []
    a = indices[0]
    for i in range(1, len(indices) - 1):
        if indices[i] != indices[i - 1] + 1:
            areas.append((a, indices[i - 1]))
            a = indices[i]
    return areas, indices

def get_s_core(meanmat):
    s_coreness = np.zeros(len(meanmat))
    s_cores = np.sum(meanmat, 0)
    i = 1
    while np.any(s_cores > 0):
        score_mat, y = bct.score_wu(meanmat, i)
        s_cores = np.sum(score_mat, 0)
        s_coreness[s_cores > 0] = i
        i += 1
    return s_coreness
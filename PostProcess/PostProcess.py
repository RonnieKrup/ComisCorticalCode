from . import Network, File_handling, Graphics, Subject_info
from collections import defaultdict
import numpy as np



def leave_one_out(stats, dataset, labels, atlas):
    graphs = Network.get_all_graphs(stats, dataset)
    corrs_per_node = Network.leave_one_out(graphs, stats, labels)
    vals_per_node = {k: -0.5730816588001257-v[0] for k, v in corrs_per_node.items()}
    Graphics.make_histogram(list(vals_per_node.values()), 'Node Effect Histogram')
    strong_nodes = Network.get_strongest_value_nodes(vals_per_node)
    # TODO: print node names with values

    stats_nii_dict = File_handling.make_hemi_stat_nifti(vals_per_node, atlas)
    for key in stats_nii_dict.keys():
        Graphics.display_stats_on_surface(stats_nii_dict[key], hemi=key,
                                          title=f'Leave One Out Effect, {key} hemisphere', thresh=0.005, save=None)
    return vals_per_node, strong_nodes


def cross_coreness_leave_out(corness_vals, vals_per_node, atlas_meta):
    coreness_by_node = File_handling.transpose_dict(corness_vals)
    x = []
    y = []
    for k in coreness_by_node.keys():
        x.append(coreness_by_node[k])
        y.append(vals_per_node[k])
        Graphics.make_basic_graph(x, y, 'S-Coreness', '$delta$r-Value', "", 1000)
    result = {atlas_meta['name'][k]: {'label': k, 'rvals': v, 'coreness': coreness_by_node[k]}
              for k, v in vals_per_node}
    result = {k: v for k, v in sorted(result.items(), key=lambda item: 1 - item[1]['coreness'])}
    Graphics.display_scorness_rval(result)


def heritability(dataset, stats):
    sub_info = File_handling.read_info(dataset)
    if len(sub_info) == 1:
        sub_info = sub_info[0]
        sub_info_res = []
    else:
        sub_info_res = sub_info[1]
        sub_info = sub_info[0]
    bio = 'efficiencies'
    family_pairs = Subject_info.create_family_pairs(sub_info_res, stats, bio)
    tucky_results = Subject_info.family_comparison(family_pairs, bio)

    dat = []
    groups = ['MZ', 'DZ', 'NotTwin', 'NotRelated']
    for i in groups:
        dat.append(family_pairs[i])
    Graphics.barplot(family_pairs, groups, title=f'Difference in {bio} between pairs')
    falconers = Subject_info.falcon(Subject_info.create_family_pairs(sub_info_res, stats, bio, 'twinpair'))
    cross_twin = Subject_info.cross_twin(Subject_info.create_family_pairs(sub_info_res, stats, bio, 'comis'))


def rich_club(stats, dataset, labels):
    all_cms = File_handling.get_all_cm(stats, dataset)
    all_cms = Network.make_cm_from_parts(all_cms)
    meanmat = Network.get_mean_mat(all_cms)
    rich_c, rand_rich = Network.rich_club(meanmat)
    areas, indices = areas = Network.get_pval_indices(rich_club, rand_rich)
    Graphics.make_rich_club_graph(rich_c, rand_rich, areas=areas)
    rich_labels = labels[indices]


def s_coreness(stats, dataset, labels):
    graphs, all_cms = Network.get_all_graphs(stats, dataset, return_cm=True)
    all_cms = Network.make_cm_from_parts(all_cms)
    meanmat = Network.get_mean_mat(all_cms)
    s_core = Network.get_s_core(meanmat)
    label_scoreness = defaultdict(list)
    for s, label in zip(s_core, labels):
        label_scoreness[np.mean(s)].append(label)
    score_remove, score_remove_rand = Network.remove_nodes_rvals(graphs, stats, labels, label_scoreness)
    Graphics.make_rich_club_graph(score_remove, score_remove_rand, with_norm=False)
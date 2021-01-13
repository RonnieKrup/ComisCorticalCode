from collections import defaultdict
from statsmodels.stats.multicomp import MultiComparison
import numpy as np
import random
from scipy.stats import pearsonr

def create_family_pairs(sub_info_res, stats, bio, data_type='diff'):
    # data_type can be 'diff' for difference between pairs,
    # 'twinpair' for a tuple of both twins' bio
    # or a name of a trait from stats for cross twin cross cor
    family_pairs = defaultdict(list)
    ZygosityGT = sub_info_res.groupby('ZygosityGT')
    not_related = []
    for group in ZygosityGT:
        sibtype = group[0]
        families = group[1].groupby('Family_ID')
        for i in families:
            if len(i[1]) > 1:
                if data_type == 'diff':
                    try:
                        family_pairs[sibtype].append(np.abs(stats[bio][i[1].index[0]] -
                                                            stats[bio][i[1].index[1]]))
                        if len(i[1]) > 2:
                            not_related.append(stats[bio][i[1].index[2]])
                        else:
                            not_related.append(stats[bio][i[1].index[0]])
                    except KeyError:
                        pass
                elif data_type == 'twinpair':
                    try:
                        family_pairs[sibtype].append((stats[bio][i[1].index[0]],
                                                      stats[bio][i[1].index[1]]))
                    except KeyError:
                        pass
                else:
                    try:
                        family_pairs[sibtype].append(((stats[bio][i[1].index[0]],
                                                       stats[bio][i[1].index[1]]),
                                                      (stats[data_type][i[1].index[0]],
                                                       stats[data_type][i[1].index[1]])))
                    except KeyError:
                        pass
    for i in range(2):
        non_related_temp = not_related[:]
        random.shuffle(non_related_temp)
        while len(non_related_temp) > 1:
            family_pairs['NotRelated'].append(np.abs(non_related_temp.pop() - non_related_temp.pop()))
    family_pairs.pop('TwinUndefined')
    family_pairs.pop('undefined')
    return family_pairs


def family_comparison(family_pairs, bio):
    keys = []
    for i in family_pairs.items():
        for j in i[1]:
            keys.append((i[0], j))

    data = np.rec.array(keys, dtype=[('sib_type', '|U5'), (bio, float)])
    mc = MultiComparison(data[bio], data['sib_type'])
    return mc.tukeyhsd()


def falcon(family_pairs):
    rMZ = pearsonr(np.transpose(family_pairs['MZ'])[0], np.transpose(family_pairs['MZ'])[1])
    rDZ = pearsonr(np.transpose(family_pairs['DZ'])[0], np.transpose(family_pairs['DZ'])[1])
    return 2*(rMZ[0]-rDZ[0])


def cross_twin(family_pairs, n_iter = 5000):
    mz = []
    dz = []
    for _ in range(n_iter):
        xm = []
        ym = []
        for i in random.choices(family_pairs['MZ'], k=40):
            xm.append(i[0][0])
            ym.append(i[1][1])

        xd = []
        yd = []
        for i in random.choices(family_pairs['DZ'], k=40):
            xd.append(i[0][0])
            yd.append(i[1][1])

        mz.append(pearsonr(xm, ym))
        dz.append(pearsonr(xd, yd))

    print(np.mean(mz, 0))
    print(np.mean(dz, 0))
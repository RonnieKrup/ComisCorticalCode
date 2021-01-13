from . import Network
from matplotlib import colors, cm
from matplotlib import pyplot as plt
import numpy as np
from nilearn import surface, plotting
from scipy.stats import linregress


def round_pval():
    raise NotImplementedError


def make_basic_graph(x, y, xcaption, ycaption, title, ax_scale=1, scatter_kwargs=None):
    # in: x and y for scatter plot
    # displays scatter plot for x VS y, ax_scale is the scaling factor between the x and y axes
    # out: the slope and intersection of the linear regression line, and the figure for the graph
    # try:
    #    plt.close()
    # except:
    #    pass
    scatter_kwargs = scatter_kwargs or {}
    f, ax = plt.subplots(figsize=(5, 5), dpi=180)
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
    ax.ticklabel_format(style='sci', scilimits=(-3, 3), useMathText=True)

    plt.scatter(x, y, s=3, c='xkcd:azure', **scatter_kwargs)
    slope, inter, rval, pval, stder = linregress(x, y)
    plt.plot(x, np.array(x) * slope + inter, color='xkcd:darkblue', linewidth=1)

    plt.xlabel(xcaption, fontsize=12, fontname='Serif')
    plt.ylabel(ycaption, fontsize=12, fontname='Serif')
    plt.title(title)
    plt.gca().set_aspect(ax_scale, adjustable='box')
    xrange = max(x) - min(x)
    ymed = min(y) + (max(y) - min(y)) / 2
    plt.ylim(ymed - (xrange / (2 * ax_scale)), ymed + (xrange / (2 * ax_scale)))
    print(f"r^2 = {rval} \n p = {pval}")
    textstr = f"r = {np.round(rval,2)} \n {round_pval(pval)}"
    props = dict(boxstyle='round', facecolor='xkcd:light grey', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props, fontname='Serif')
    return slope, inter, f


def display_stats_on_surface(hemi_stat_data, hemi='Left', title='', thresh=0.1, save=None):
    pial = fr'/state/partition1/apps/freesurfer/subjects/cvs_avg35_inMNI152/surf/{hemi[0].lower()}h.pial'
    inflated = fr'/state/partition1/apps/freesurfer/subjects/cvs_avg35_inMNI152/surf/{hemi[0].lower()}h.inflated'
    sulc = fr"/state/partition1/apps/freesurfer/subjects/cvs_avg35_inMNI152/surf/{hemi[0].lower()}h.sulc"
    aal_surf = surface.vol_to_surf(hemi_stat_data, pial)

    f, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 5), dpi=180, subplot_kw={'projection': '3d'})
    for view, ax in zip(['lateral, medial'], [ax1, ax2]):
        plotting.plot_surf_stat_map(inflated, aal_surf, hemi=hemi.lower(), title=title, colorbar=True,
                                    threshold=thresh, figure=f, axes=ax, bg_map=sulc, view=view)
    if save:
        plt.savefig(save)


def make_histogram(dat, label, ylim=None, hist_kwargs=None):
    f, ax = plt.subplots(figsize=(7, 5), dpi=180)
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]

    hist_kwargs = hist_kwargs or {}
    hist_kwargs['bins'] = hist_kwargs.get('bins', 50)
    plt.hist(dat, color='xkcd:azure', edgecolor='xkcd:darkblue', histtype='stepfilled',
             **hist_kwargs)
    ax.ticklabel_format(style='sci', scilimits=(-3, 3), useMathText=True)
    plt.xlabel(label, fontsize=12, fontname='Serif')
    if ylim:
        ax.set_ylim(ylim)
    return f


def display_scorness_rval(result, save=None):
    r = [i['rvals'] for i in result.values()]
    norm = colors.Normalize(vmin=np.min(r), vmax=abs(np.min(r)))

    f, ax = plt.subplots(figsize=(10, 3), dpi=180)
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
    ax.bar(range(len(result.values())), [i['coreness'] for i in result.values()],
           color=[plt.get_cmap('seismic')(norm(i['rvals'])) for i in result.values()])
    plt.xticks(range(len(result.values())), [i for i in result.keys()], rotation='vertical', fontsize=5)
    sm = cm.ScalarMappable(norm=norm, cmap=plt.get_cmap('seismic'))
    sm.set_array([])
    plt.colorbar(sm)
    plt.ylabel("Node S-Coreness")
    if save:
        plt.savefig(save)


def barplot(data_dict, x_labels, title='', ylim=1, bracket_dict={}):
    err = [np.std(data_dict[i]) / np.sqrt(len(data_dict[i])) for i in x_labels]
    heights = [np.mean(data_dict[i]) for i in data_dict]
    bars = np.arange(len(heights))

    bar_kwargs = {'width': 0.8, 'color': 'xkcd:light blue', 'linewidth': 2, 'zorder': 5, 'edgecolor': 'xkcd:darkblue',
                  'alpha': 0.7}
    err_kwargs = {'zorder': 0, 'fmt': 'none', 'linewidth': 2, 'ecolor': 'xkcd:darkblue',
                  'capsize': 5}  # for matplotlib >= v1.4 use 'fmt':'none' instead

    fig = plt.figure(figsize=(7, 5), dpi=180)
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
    plt.bar(bars, heights,
            tick_label=list(x_labels), yerr=err, **bar_kwargs)
    plt.errs = plt.errorbar(bars, heights, yerr=err, **err_kwargs)
    plt.gca().set_ylim(0, ylim)

    for k, v in bracket_dict.items():
        barplot_annotate_brackets(k[0], k[1], v['value'], bars, heights, dh=v['height'])
    plt.title(title)


def make_rich_club_graph(rich_club, rand_rich, with_norm=True, areas=None):
    run_mean = [rich_club[1]]
    run_mean.extend(running_mean(np.array(rich_club[:-1]), 3))
    run_mean.append(rich_club[-2])
    single_rand_rich_club = np.nanmean(rand_rich, 0)
    f, ax = plt.subplots(figsize=(10, 5), dpi=180)
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
    ax.plot(rich_club, c='xkcd:darkblue', marker='o', linewidth=1, markeredgewidth=0.7, markersize=5)
    ax.plot(single_rand_rich_club, c='xkcd:azure', marker='o', linewidth=1, markeredgewidth=0.7, markersize=5)
    ax.plot(run_mean, c='xkcd:lightblue', linewidth=3, alpha=.7)


    if with_norm:
        ax2 = ax.twinx()
        ax2.plot(rich_club[:len(single_rand_rich_club)] / single_rand_rich_club, c='xkcd:coral', marker='o', linewidth=1,
                 markeredgewidth=0.7, markersize=5)
        ax2.set_ylabel("Normalized Rich Club - \u03A6$_{Norm}$")

    ax.set_ylabel("Rich Club - \u03A6")
    ax.set_xlabel("K")
    if areas:
        for i in areas[1:]:
            plt.axvspan(i[0], i[1], color='xkcd:grayblue', alpha=0.3)


def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0))
    return (cumsum[N:] - cumsum[:-N]) / float(N)




def barplot_annotate_brackets(num1, num2, data, center, height, yerr=None, dh=.05, barh=.05, fs=None, maxasterix=None):
    """
    Annotate barplot with p-values.

    :param num1: number of left bar to put bracket over
    :param num2: number of right bar to put bracket over
    :param data: string to write or number for generating asterixes
    :param center: centers of all bars (like plt.bar() input)
    :param height: heights of all bars (like plt.bar() input)
    :param yerr: yerrs of all bars (like plt.bar() input)
    :param dh: height offset over bar / bar + yerr in axes coordinates (0 to 1)
    :param barh: bar height in axes coordinates (0 to 1)
    :param fs: font size
    :param maxasterix: maximum number of asterixes to write (for very small p-values)
    """

    if type(data) is str:
        text = data
    else:
        # * is p < 0.05
        # ** is p < 0.005
        # *** is p < 0.0005
        # etc.
        text = ''
        p = .05

        while data < p:
            text += '*'
            p /= 10.

            if maxasterix and len(text) == maxasterix:
                break

        if len(text) == 0:
            text = 'n. s.'

    lx, ly = center[num1], height[num1]
    rx, ry = center[num2], height[num2]

    if yerr:
        ly += yerr[num1]
        ry += yerr[num2]

    ax_y0, ax_y1 = plt.gca().get_ylim()
    dh *= (ax_y1 - ax_y0)
    barh *= (ax_y1 - ax_y0)

    y = max(ly, ry) + dh

    barx = [lx, lx, rx, rx]
    bary = [y, y+barh, y+barh, y]
    mid = ((lx+rx)/2, y+barh)

    plt.plot(barx, bary, c='black')

    kwargs = dict(ha='center', va='bottom')
    if fs is not None:
        kwargs['fontsize'] = fs

    plt.text(*mid, text, **kwargs)
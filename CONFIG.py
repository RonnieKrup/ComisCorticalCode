import os
import pandas as pd
from ComisCorticalCode import toolbox

EXPNAME = '1'
DO_RESAMPLE = True
DO_SMOOTH = True
MINVOL = 259209    # for theBase. 577275 for HCP
TRACTOGRAPHY = {
                'PIXSCALE': 0.5,
                'MINSCALE': 15,
                'MAXSCALE': 250,
                'ANGLE': 45}
NO_OF_TRACTS = 5000000
NO_OF_SIFTED_TRACTS = 30500
DATASET = 'HCP'
ATLAS = "/state/partition1/home/ronniek/ronniek/AAL2_data/AAL150.nii"
ATLAS_META = "/state/partition1/home/ronniek/ronniek/AAL2_data/AAL150.txt"
ATLAS_TEMPLATE = "${FSLDIR}/data/standard/MNI152_T1_2mm"
ATLAS_FOR_CONNECTOME="../AAL2_data/AAL150_for_connectome.txt"
NTHREADS = 2
DATAIN = rf'/state/partition1/home/ronniek/ronniek/{DATASET}/datain.txt'
INDEX = rf'/state/partition1/home/ronniek/ronniek/{DATASET}/index.txt'
runs = pd.read_csv(fr'/state/partition1/home/ronniek/ronniek/{DATASET}/runs.csv')
prefix = toolbox.get_random_string(5)
DO = {}

def get_paths(base_dir, config):
    local_paths = {
        'raw_dat': 'raw_data',
        'temp': 'temp',
        'bvecs': 'raw_data/bvecs',
        'bvals': 'raw_data/bvals',
        'mprage': r'raw_data/mprage.nii.gz',
        "dif2mprage": r'affine/dif2t1',
        "mprage2diff": r'affine/t12dif',
        "5tt": '5tt'
    }

    if MINVOL in runs['MINVOL']:
        pref = runs.index[runs['MINVOL'] == MINVOL][0]
        DO['resample'] = False
    else:
        pref = prefix
        DO['resample'] = True
    local_paths.update({
        'data': rf'{pref}_data.nii.gz',
        'nodif': rf'{pref}_nodif.nii.gz',
        'brain': rf'{pref}_brain.nii.gz',
        'brain_mask': rf'{pref}_brain_mask.nii.gz'})

    if ATLAS in runs['ATLAS']:
        pref = runs.index[runs['ATLAS'] == ATLAS][0]
        DO['atlas'] = False
    else:
        pref = prefix
        DO['atlas'] = True

    local_paths['atlas'] = rf'{pref}_atlas.nii.gz'

    if DO['resample'] and DO['atlas']:
        pref = runs['MINVOL'][runs[ATLAS] == ATLAS][runs['MINVOL'] == 'MINVOL'].index[0]
        DO['make_fod'] = False
    else:
        pref = prefix
        DO['make_fod'] = True

    local_paths.update({"res": f'{pref}_wm_res.txt',
         "fod": f'{pref}_wm_fod.mif'})

    if MINVOL in runs['MINVOL'] and TRACTOGRAPHY in runs['TRACTOGRPAHY']:
        pref = runs['MINVOL'][runs[TRACTOGRAPHY] == TRACTOGRAPHY][runs['MINVOL'] == 'MINVOL'].index[0]
        DO['generate_tracts'] = True

    else:
        pref = prefix
        DO['generate_tracts'] = False
    local_paths.update({
        'tracts': f'{pref}_tracts_unsifted.tck',
        'sifted_tracts': f'{pref}_tracts.tck',
    })

    if DO['make_fod'] and TRACTOGRAPHY in runs['TRACTOGRPAHY']:
        prefs = runs['MINVOL'][runs[ATLAS] == ATLAS][runs['MINVOL'] == 'MINVOL'].index
        pref = runs['TRACTOGRAPHY'][prefs][runs['TRACTPGRAPHY'][prefs] == TRACTOGRAPHY].index[0]
        DO['SIFT'] = True

    else:
        pref = prefix
        DO['SIFT'] = False
    local_paths.update({
        'tracts': f'{pref}_atlas_tracts_unsifted.tck',
        'sifted_atlas_tracts': f'{pref}_atlas_tracts.tck',
    })



    return {
            name: os.path.join(base_dir, value)
            for name, value in local_paths.items()
            }

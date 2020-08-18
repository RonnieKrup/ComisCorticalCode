import os

EXPNAME = '1'
DO_RESAMPLE = True
DO_SMOOTH = True
MINVOL = 259209    # for theBase. 577275 for HCP
STEP_SIZE = 0.5
MIN_LENGTH = 15
MAX_LENGTH = 250
ANGEL = 45
NO_OF_TRACTS = 5000000
NO_OF_SIFTED_TRACTS = 30500
ATLAS = "/state/partition1/home/ronniek/ronniek/AAL2_data/AAL150.nii"
ATLAS_META = "/state/partition1/home/ronniek/ronniek/AAL2_data/AAL150.txt"
ATLAS_TEMPLATE = "${FSLDIR}/data/standard/MNI152_T1_2mm"
ATLAS_FOR_CONNECTOME="../AAL2_data/AAL150_for_connectome.txt"
NTHREADS = 2
NTRACTS=40500


def get_paths(base_dir, config):
    local_paths = {
        'raw_dat': ...,
        'nodif': ...,
        'datain': ...,
        'brain': ...,
        'brain_mask': ...,
        'index': ...,
        'temp': ...,
        'bv': ...,
        'data': ...,
        'mprage': ...,
        "dif2mprage": ...,
        "mprage2diff": ...,
        "atlas": ...,
        "5tt": ...,
        "res": ...,
        "fod": ...,
        "atlas_tracts": ...,
        'tracts': ...,
        'sifted_tracts': ...,
        "sifted_atlas_tracts": ...,

    }

    return {
        name: os.path.join(base_dir, value)
        for name, value in local_paths.items()
    }
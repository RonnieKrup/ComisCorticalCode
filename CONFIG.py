import os
import pandas as pd
from ComisCorticalCode import toolbox

EXPNAME = '1'
DO_RESAMPLE = True
SKIP_SMOOTH = True
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
RUNS = fr'/state/partition1/home/ronniek/ronniek/{DATASET}/runs.csv'
DO = {}



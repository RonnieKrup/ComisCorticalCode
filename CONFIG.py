import os
import pandas as pd
from ComisCorticalCode import toolbox

MINVOL = 259209    # for theBase. 577275 for HCP
SUBJECT_HOME = '/state/partition1/home/ronniek/ronniek/'
STEPSCALE = 0.5
LENSCALE = [15, 250]
ANGLE = 45
NTRACTS = 5000000
DATASET = 'HCP'
ATLAS = "/state/partition1/home/ronniek/ronniek/AAL2_data/AAL150.nii"
ATLAS_META = "/state/partition1/home/ronniek/ronniek/AAL2_data/AAL150.txt"
ATLAS_TEMPLATE = "${FSLDIR}/data/standard/MNI152_T1_2mm"
ATLAS_FOR_CONNECTOME="../AAL2_data/AAL150_for_connectome.txt"
NTHREADS = 2
DATAIN = rf'/state/partition1/home/ronniek/ronniek/{DATASET}/datain.txt'
INDEX = rf'/state/partition1/home/ronniek/ronniek/{DATASET}/index.txt'
RUNS = fr'/state/partition1/home/ronniek/ronniek/{DATASET}/runs.csv'
DO_EDDY = {}



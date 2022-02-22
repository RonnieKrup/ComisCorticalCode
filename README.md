# ComisCorticalCode
This is the preprocessing pipeline used in YA-lab for deterministic tractography using mrtrix. this pipeline includes:
- topup based eddy and movement correction
- rescaling of all images to similar number of brain voxels (optional)
- registration of both atlas and the t1 image to dwi space
- segmentation to 5 tissue types
- FOD estimation
- tractography
- tractography within atlas voxels (optional)

## Dependencies
- linux or linux vm
- FSL v6+ ([download here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation))
- Mrtrix3 ([download here](https://www.mrtrix.org/download/))
- python 3.6+

## The Steps:
Some steps are optional and will only happen if the required files and arguments are specified and exist.
1. *Eddy correction* based on FSL topup and eddy (optional). Will happen only if PA and AP. This step also includes mrtrix denoising of the data.
2. Resize brains to have a similar number of voxels (optional). Runs through mrtrix and will only run if minvol is specified.
3. registrations usinf fsl flirt and fnirt to create:
 I. T1w to diffusion affine matrix
 II. atlas template to T1w warp
 III. atlas registered to the diffusion space
4. Data segmentation, using mrtrix 5tt segmentation (fsl based). this segmentation is done for the t1w image and registered to the diffusion space.
5. creation of fiber orientation distribution with mrtrix. this pipeline assumes multi-shell data.
6. deterministic fiber tracking using mrtrix tracking and SIFT.
7. filter tracts to connectome (optional) - filter the unsifted tracts to tracts with ends inside or close to atlas voxels (2 voxel search radius), and then SIFTed. will only be used if `atlas_for_connectome` is specified.

## How to run
This pipeline uses input data that cen be specified either as a `config.json` file, or as commandline args:
### Required arguments
- `-data_path`: string. path to directory where the subjects' raw data is stored (see data organization below).
- `-atlas`: string. path to atlas.  
- `- atlas_template`: string. path to template image on which the atlas is based
- either:
 - `-run_name`: string. name for the files of this run. if not defined, `run_list` must be defined, and the name will be chosen based on the list.
 - `-run_list`: string. path to csv file listing past runs and their parameters.


### Additional Arguments
#### System Arguments
- `-config_path`: string. If you want to use a `config.json` file, enter the path here. Note that if the same argument apeares in both the config file and the command line, the command line argument is used.
- `-njobs`: int. number of jos to run at a time. default is one at a time.
- `-out`: string. path to directory in which to dump logs etc. default is an `out` directory in the current working directory.
- `-nthreads`: if running in multi-cpu computer, define the number of parallel threads to run in. default is 2
- `-additional_paths`: list. if specific paths should be added to the `${path}` enviromnent variable, add them here.
#### Arguments for Eddy Correction
- `-datain`: string. path to datain file for topup. if none, the pipeline will look for it in `{data_path}/datain.txt`
- `-index`: string. path to index file for topup. if none, the pipeline will look for it in `{data_path}/index.txt`
#### Arguments for Rescaling
- `-minvol`: int. if rescaling is needed, the number of voxels wanted for the brains after rescaling. The rescaling will be done such that the brain masks of each subject will be as close as possible to this number. If not used, the rescaling stepp will be skipped.
#### Arguments for Tractography
- `-stepscale`: float.  step size in tractography will be pixel_size * stepscale. default: 0.5
- `-lenscale`: min, max. two float/int values, seperated by commas. minimum and maximum tract length tractography will be pixel_size * lenscale. default: 15, 30.
- `-angle`: int. the minimum curvature angle for the tractography. default: 45.
- `-ntracts`: int. the number of tracts wanted by the end of the tractography. note that the pipline will innitialy create ntracts * 100 tracts. and then reduce the number to ntracts using mrtrix3 SIFT algorithm.
#### Arguments for Connectome Tractography
- `-atlas_meta`: string. path to atlas metadata (as csv/txt file file). if no path is given, default is the same path and file name as `atlas`, with the suffix .txt
- `-atlas_for_connectome`: string. if you want the tracts filtered to only include those ending in connectome nodes, add an atlas conversion csv for the connectome. This csv shpuld include labels, label names and the converted labels such that the node numbers are 1 to number of nodes. if none, this step is skipped



## Data organization
to run this, each subject should be in its own directory.
for each subject, a directory called raw_data directory with the following files must exist:
- mprage.nii.gz -> T1w image (including skull)
- bvals, bvecs -> files extracted from conversion to niftii
- either:
 - dif_AP.nii.gz and dif_PA.nii.gz -> for eddy correction
 - data.nii.gz -> if DWI data is already corrected

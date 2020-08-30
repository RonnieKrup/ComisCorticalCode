# ~~ IMPORTS~~ #
from ComisCorticalCode import CONFIG
from subprocess import call
import os
import nibabel as nb
import numpy as np
import shutil
# ~~~~~~~~~~~~ #


def get_command(program, args=(), **kwargs):
    result = []
    result.append(program)
    if args:
        for arg in args:
            result.append(arg)
    for arg_name, arg_value in kwargs.items():
        result.append(f'--{arg_name.lower()}={arg_value}')
    return ' '.join(result)


def to_log(cmd):
    with open(CONFIG.LOG, 'a') as log:
        log.write('\n')
        log.write('\n'.join(cmd))


def run_commands(cmd, environment=dict(os.environ)):
    for command in cmd:
        exit_code = call(command, shell=True, env=environment)
        if exit_code != 0:
            return False
        to_log(cmd)
    return True


def eddy(paths):
    # eddy current correction based on topup

    cmd = []
    cmd.append(get_command('fslroi', (f'{paths["raw_dat"]}/dif_AP.nii.gz', paths['nodif'], 0, 1)))
    cmd.append(get_command('fslroi', (f'{paths["raw_dat"]}/dif_PA.nii.gz', f'{paths["temp"]}/nodif_PA', 0, 1)))
    cmd.append(get_command('fslmerge', (paths["nodif"], f'{paths["raw_dat"]}/nodif_PA.nii.gz'),
                           t=f'{paths["temp"]}/AP_PA_b0.nii.gz'))
    cmd.append(get_command('topup', imain=f'{paths["temp"]}/AP_PA_b0.nii.gz', datain=CONFIG.DATAIN,
                           config='b02b0.cnf', out=f'{paths["temp"]}/topup_AP_PA_b0',
                           iout=f'{paths["temp"]}/topup_AP_PA_b0_iout', fout=f'{paths["temp"]}/topup_AP_PA_b0_fout'))
    cmd.append(get_command('fslmaths', (f'{paths["temp"]}/topup_AP_PA_b0_iout',), Tmean=paths["nodif"]))
    cmd.append(get_command('bet', (paths["nodif"], paths["brain"], '-m'), f=0.2))
    cmd.append(get_command("denoise", (f'{paths["raw_dat"]}/dif_AP.nii.gz', f'{paths["raw_dat"]}/dif_AP.nii.gz',
                                       'force'), mask=paths["brain_mask"]))
    cmd.append(get_command(f'eddy_openmp', ('data_is_shelled',), imain=f'{paths["raw_dat"]}/dif_AP.nii.gz',
                           mask=paths["brain_mask"], index=CONFIG.INDEX, acqp=CONFIG.DATAIN,
                           bvecs=paths["bvecs"], bvals=paths["bvals"][1], fwhm=0,
                           topup=f'{paths["temp"]}/topup_AP_PA_b0', flm='quadratic', out=paths["data"]))

    environment = dict(os.environ)  # Copy the existing environment variables
    environment['OMP_NUM_THREADS '] = CONFIG.NTHREADS
    if run_commands(cmd, environment):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("eddy failed. see log for details")
        return False


def resample(paths):
    # resizing data and creating a fitting brain mask

    mask = nb.load(paths["brain_mask"]).get_data()
    vol = np.sum(mask)
    cmd = []
    cmd.append(get_command('mrresize', (paths["data"], paths["data"].replace(".nii.gz", "_resampled.nii.gz"), "-force"),
               nthreads=CONFIG.NTHREADS, scale=(CONFIG.MINVOL/vol)**(1/3)))
    paths['data'] = paths["data"].replace(".nii.gz", "_resampled.nii.gz")
    cmd.append(get_command('fslroi', (paths["data"], paths["nodif"], 0, 1)))
    paths["brain"] = paths["brain"].replace(".nii.gz", "_resampled.nii.gz")
    paths["brain_mask"] = paths["brain"].replace("mask.nii.gz", "_resampled_mask.nii.gz")
    cmd.append(get_command('bet', (paths["nodif"], paths["brain"], '-m'), f=0.2, g=0.2))
    if run_commands(cmd):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("resampling failed. see log for details")
        return False


def register_t12diff(paths):
    cmd = []

    cmd.append(get_command('bet', (paths["mprage"], paths["mprage"].replace('.nii.gz', 'brain.nii.gz'), '-m'),
                           f=0.2, g=0.2))

    cmd.append(get_command('flirt', In=paths["brain"], ref=paths["anatomy"].replace('.nii.gz', 'brain.nii.gz'),
                           omat=paths["dif2mprage"], bins=256, cost="normmi", searchrx="-90 90", searchry="-90 90",
                           searchrz="-90 90", dof=12))

    cmd.append(get_command("convert_xfm", (paths["dif2mprage"], "-inverse"), omat=paths["mprage2diff"]))
    if run_commands(cmd):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("registration of anatomical data to diffusion failed. see log for details")
        return False


def register_template2t1(paths):
    cmd = []
    cmd.append(get_command("flirt", ref=CONFIG.ATLAS_TEMPLATE, In=paths["mprage"], omat=paths["mprage2template"]))
    cmd.append(get_command("fnirt", In=paths["mprage"], aff=paths["mprage2template"], ref=CONFIG.ATLAS_TEMPLATE,
                           cout=paths["mprage2template"], config="T1_2_MNI152_2mm"))
    cmd.append(get_command('invwarp', ref=paths["mprage"], out=paths["template2mprage"], warp=paths["mprage2template"]))
    if run_commands(cmd):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("registration of template to anatomical data failed. see log for details")
        return False


def register_atlas(paths):
    cmd = []
    cmd.append(get_command("applywarp", ref=paths["mprage"], In=CONFIG.ATLAS, out=paths["atlas"],
                           warp=paths["template2mprage"], interp="nn"))
    cmd.append(get_command("flirt", ("applyxfm",), ref=paths["brain"], In=paths["atlas"], init=paths["mprage2diff"],
                           interp="nearestneighbour", out=paths["atlas"]))
    cmd.append(get_command("labelconvert", (paths['atlas'], CONFIG.ATLAS_FOR_CONNECTOME,
                                            CONFIG.ATLAS_FOR_CONNECTOME.replace('.txt', '_converted.txt'),
                                            paths["atlas"].replace(".nii.gz", "_connectome.nii.gz"), "force"),
                           nthreads=CONFIG.NTHREADS))
    if run_commands(cmd):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("registration of atlas to data failed. see log for details")
        return False


def segment(paths):
    environment = dict(os.environ)  # Copy the existing environment variables
    environment['SGE_ROOT'] = ''
    program_path = '/state/partition1/home/ronniek/mrtrix3/bin/5ttgen'
    cmd = []
    cmd.append(get_command(program_path, ('fsl', paths["mprage"].replace('.nii.gz', 'brain.nii.gz'), paths["5tt"],
                                          '-premasked', '-nocrop', '-f')))
    cmd.append(get_command("transformconvert", ("-force", paths['mprage2diff'],
                                                paths["mprage"].replace('.nii.gz', 'brain.nii.gz'), paths['brain'],
                                                'flirt_import', paths['mprage2diff'].replace('.mat', '.txt'))))
    cmd.append(get_command("mrtransform", (paths["5tt"], paths["5tt"], "-force"), nthreads=2,
                           linear=paths['mprage2diff'].replace('.mat', '.txt')))

    if run_commands(cmd):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("segmentation failed. see log for details")
        return False


def make_fod(paths):
    cmd = []
    cmd.append(get_command("dwi2response", ("dhollander", paths["data"], paths['res'], fr"{paths['temp']}/gm_res.txt",
                                            fr"{paths['temp']}/csf_res.txt", '-force'),
                           mask=paths["brain_mask"], nthreads=CONFIG.NTHREADS,
                           fslgrad=f"{paths['bvecs']} {paths['bvals']}"))

    cmd.append(get_command("dwi2fod msmt_csd", (paths["data"], paths["res"], paths["fod"],
                                                fr"{paths['temp']}/gm_res.txt", fr"{paths['temp']}/gm_fod.mif"
                                                fr"{paths['temp']}/csf_res.txt", fr"{paths['temp']}/csf_fod.mif",
                                                "-force"),
                           fslgrad=f"{paths['bvecs']} {paths['bvals']}", nthreads=CONFIG.NTHREADS, mask=paths["brain_mask"]))
    if run_commands(cmd):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("FOD computation failed. see log for details")
        return False


def generate_tracts(paths):
    cmd = []
    diff = nb.load(paths['brain'])
    pixdim = diff.header['pixdim'][1]
    cmd.append(get_command("tckgen", (paths["fod"], paths["tracts"], "-force"), algorithm="Tensor_Det",
                           select=CONFIG.NTRACTS, step=pixdim * CONFIG.PIXSCALE, minlength=pixdim * CONFIG.MINSCALE,
                           maxlength=pixdim * CONFIG.MAXSCALE, angle=CONFIG.ANGLE, seed_image=paths["brain_mask"],
                           act=paths["5tt"], fslgrad=f"{paths['bvecs']} {paths['bvals']}"))
    cmd.append(get_command("tcksift", (paths["trats"], paths["fod"], paths["sifted_tracts"],
                                       "-force", "-fd_scale_gm"),
                           act=paths["5tt"], nthreads=CONFIG.NTHREADS, term_number=CONFIG.NTRACTS*0.1))
    if run_commands(cmd):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("tract generation failed. see log for details")
        return False


def sift_atlas(paths):
    cmd = []
    cmd.append(get_command("tck2connectome", (paths["atlas"].replace(".nii.gz", "_connectome.nii.gz"),
                                              rf"paths['temp']/connectome", "-force"),
                           nthreads=CONFIG.NTHREADS, assignment_radial_search=2, out_assignments=rf"paths['temp']/out"))
    cmd.append(get_command("connectome2tck", (paths["tracts"], rf"paths['temp']/out", paths["atlas_tracts"],
                                              "-exclusive", "-keep_self", "-force"),
                           nthreads=CONFIG.NTHREADS, nodes=",".join([str(i) for i in range(1, CONFIG.NODES+1)]),
                           files="single"))
    cmd.append(get_command("tcksift", (paths["atlas_tracts"], paths["fod"], paths["sifted_atlas_tracts"],
                                       "-force", "-fd_scale_gm"),
                           act=paths["5tt"], nthreads=CONFIG.NTHREADS, term_number=CONFIG.NTRACTS*0.1))

    if run_commands(cmd):
        print("eddy complete")
        shutil.rmtree(paths["temp"])
        return paths
    else:
        print("atlas tract sifting failed. see log for details")
        return False

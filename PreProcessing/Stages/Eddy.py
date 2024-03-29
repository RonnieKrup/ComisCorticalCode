from ComisCorticalCode.PreProcessing.toolbox import ExternalCommand
from ComisCorticalCode.PreProcessing import stage

import os


class Eddy(stage.BaseStage):
    def __init__(self, *, raw_dat, temp, bv, nthreads, index_datain):
        self.ap = os.path.join(raw_dat, 'dif_AP.nii.gz')
        self.pa = os.path.join(raw_dat, 'dif_PA.nii.gz')
        self.bvecs = bv[0]
        self.bvals = bv[1]
        self.ap_denoised = self.ap.replace('.nii.gz', '_denoised.nii.gz')
        self.hifi_nodif = os.path.join(f'{temp}', 'hifi_nodif.nii.gz')
        self.nodif = os.path.join(raw_dat, 'nodif.nii.gz')
        self.nodif_pa = os.path.join(f'{temp}', 'nodif_PA.nii.gz')
        self.merged_b0 = os.path.join(f'{temp}', 'AP_PA_b0.nii.gz')
        self.topup = os.path.join(f'{temp}', 'topup_AP_PA_b0_iout')
        self.brain = os.path.join(raw_dat, 'brain.nii.gz')
        self.mask = self.brain.replace('.nii.gz', '_mask.nii.gz')
        self.data = os.path.join(raw_dat, 'data.nii.gz')
        self.env = dict(os.environ)  # Copy the existing environment variables
        self.env['OMP_NUM_THREADS'] = str(nthreads)
        self.datain = index_datain
        self.index = os.path.join(f'{temp}', "index.txt")

    @staticmethod
    def create_from_dict(paths, config):
        raw_dat = paths["raw_dat"]
        temp = paths["temp"]
        bv = [f"{paths['raw_dat']}/bvecs", paths['bvals']]
        nthreads = config.nthreads
        index_datain = [config.index, config.datain]
        return Eddy(raw_dat=raw_dat,
                    temp=temp,
                    bv=bv,
                    nthreads=nthreads,
                    index_datain=index_datain)

    def run_stage(self, run_list):
        if os.path.isfile(self.data):
            return
        commands = []
        if (os.path.isfile(self.ap) and os.path.isfile(self.pa) and os.path.isfile(self.bvecs) and
                os.path.isfile(self.bvals)):
            if not os.path.isfile(self.topup):
                commands.extend(self.make_commands_topup())

            if not os.path.isfile(self.nodif) or not os.path.isfile(self.brain):
                commands.extend(self.make_commands_make_brain())

            if not os.path.isfile(self.ap_denoised):
                commands.extend(self.make_commands_denoise())
            commands.extend(self.make_commands_eddy())
        else:
            raise FileNotFoundError('Base Files Missing')

        for command in commands:
            command.run_command(self.env)
        print('Eddy correction done')

    def make_commands_topup(self):
        commands = [
                    ExternalCommand.get_command('fslroi', self.ap, self.nodif, 0, 1, input_files=(self.ap,),
                                                output_files=(self.nodif,)),
                    ExternalCommand.get_command('fslroi', self.pa, self.nodif_pa, 0, 1, input_files=(self.pa,),
                                                output_files=(self.nodif_pa,)),
                    ExternalCommand.get_command('fslmerge', '-t', self.merged_b0, self.nodif, self.nodif_pa,
                                                input_files=(self.nodif, self.nodif_pa),
                                                output_files=(self.merged_b0,)),
                    ExternalCommand.get_command('topup', imain=self.merged_b0, datain=self.datain[1],
                                                config='b02b0.cnf', out=f'{self.topup}out', iout=self.topup,
                                                fout=f'{self.topup}_fout', input_files=(self.merged_b0,),
                                                output_files=(f'{self.topup}.nii.gz', f'{self.topup}_fout.nii.gz'))
                   ]
        return commands

    def make_commands_make_brain(self):
        commands = [
                    ExternalCommand.get_command('fslmaths', self.topup, '-Tmean', self.hifi_nodif,
                                                input_files=(f'{self.topup}.nii.gz',), output_files=(self.nodif,)),
                    ExternalCommand.get_command('bet', self.nodif, self.brain, '-m', '-f 0.2',
                                                input_files=(self.nodif,),
                                                output_files=(self.brain,
                                                              self.brain.replace('.nii.gz', "_mask.nii.gz")))
                   ]
        return commands

    def make_commands_denoise(self):
        commands = [ExternalCommand.get_command("dwidenoise", self.ap, self.ap_denoised, '-force', f'-mask {self.mask}',
                                                input_files=(self.ap, self.mask), output_files=(self.ap_denoised,))]
        return commands

    def make_commands_eddy(self):
        with open(self.bvals, 'r') as f:
            lst = f.read().strip().split(" ")
        with open(self.index, 'w') as ind:
            for i in lst:
                ind.write("1\n")

        commands = [ExternalCommand.get_command(f'eddy_openmp', '--data_is_shelled', imain=self.ap,
                                                mask=self.mask, index=self.index, acqp=self.datain[1],
                                                bvecs=self.bvecs, bvals=self.bvals, fwhm=0, topup=f'{self.topup}out',
                                                flm='quadratic', out=self.data,
                                                input_files=(self.ap_denoised, self.mask, self.bvecs, self.bvecs,
                                                             f'{self.topup}.nii.gz'), output_files=(self.data,))]
        return commands

from ComisCorticalCode.toolbox import ExternalCommand
from ComisCorticalCode import stage

import os


class Eddy(stage.BaseStage):
    def __init__(self, *, raw_dat, temp, bv, nthreads, index_datain):
        self.ap = os.path.join(raw_dat, 'dif_AP.nii.gz')
        self.ap_denoised = self.ap.replace('.nii.gz', '_denpised.nii.gz')
        self.pa = os.path.join(raw_dat, 'dif_PA.nii.gz')
        self.nodif = os.path.join(raw_dat, 'nodif.nii.gz')
        self.nodif_pa = f'{raw_dat}/nodif_PA.nii.gz'
        self.merged_b0 = f'{temp}/AP_PA_b0.nii.gz'
        self.topup = f'{temp}/topup_AP_PA_b0_iout'
        self.brain = os.path.join(raw_dat, 'brain.nii.gz')
        self.mask = self.brain.replace('.nii.gz', '_maks.nii.gz')
        self.bvecs = bv[0]
        self.bvals = bv[1]
        self.data = os.path.join(raw_dat, 'data.nii.gz')
        self.env = dict(os.environ)  # Copy the existing environment variables
        self.env['OMP_NUM_THREADS '] = nthreads
        self.index_datain = index_datain

    @staticmethod
    def create_from_dict(paths, config):
        raw_dat = paths["raw_dat"]
        temp = paths["temp"]
        bv = [paths['bvecs'], paths['bvals']]
        nthreads = config.NTHREADS
        index_datain = [paths["index"], paths["datain"]]
        return Eddy(raw_dat=raw_dat,
                    temp=temp,
                    bv=bv,
                    nthreads=nthreads,
                    index_datain=index_datain)

    def run(self):
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
            self.make_commands_eddy()
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
                    ExternalCommand.get_command('fslmerge', self.nodif, self.nodif_pa, t=self.merged_b0,
                                                input_files=(self.nodif, self.nodif_pa),
                                                output_files=(self.merged_b0,)),
                    ExternalCommand.get_command('topup', imain=self.merged_b0, datain=self.index_datain[1],
                                                config='b02b0.cnf', out=f'{self.topup}out', iout=self.topup,
                                                fout=f'{self.topup}_fout', input_files=(self.merged_b0,),
                                                output_files=(f'{self.topup}out', self.topup, f'{self.topup}_fout'))
                   ]
        return commands

    def make_commands_make_brain(self):
        commands = [
                    ExternalCommand.get_command('fslmaths', self.topup, Tmean=self.nodif, input_files=(self.topup,),
                                                output_files=(self.nodif,)),
                    ExternalCommand.get_command('bet', self.nodif, self.brain, '-m', f=0.2, input_files=(self.nodif,),
                                                output_files=(self.brain,
                                                              self.brain.replace('.nii.gz', "_mask.nii.gz")))
                   ]
        return commands

    def make_commands_denoise(self):
        commands = [ExternalCommand.get_command("denoise", self.ap, self.ap_denoised, 'force', mask=self.mask,
                                                input_files=(self.ap, self.mask), output_files=(self.ap_denoised,))]
        return commands

    def make_commands_eddy(self):
        commands = [ExternalCommand.get_command(f'eddy_openmp', 'data_is_shelled', imain=self.ap_denoised,
                                                mask=self.mask, index=self.index_datain[0], acqp=self.index_datain[1],
                                                bvecs=self.bvecs, bvals=self.bvals, fwhm=0, topup=f'{self.topup}out',
                                                flm='quadratic', out=self.data,
                                                input_files=(self.ap_denoised, self.mask, self.bvecs, self.bvecs,
                                                             f'{self.topup}out'), output_files=(self.data,))]
        return commands

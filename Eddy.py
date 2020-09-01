from ComisCorticalCode import CONFIG,  toolbox
import os

class Eddy:
    def __init__(self, raw_dat, temp, bv, nthreads, skip_smooth, index_datain):
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
        self.commands = []
        self.env = dict(os.environ)  # Copy the existing environment variables
        self.env['OMP_NUM_THREADS '] = nthreads
        self.skip_smooth = skip_smooth
        self.index_datain = index_datain

    @staticmethod
    def create_from_dict(paths):
        raw_dat = paths["raw_dat"]
        temp = paths["temp"]
        bv = [paths['bvecs'], paths['bvals']]
        nthreads = CONFIG.NTHREADS
        skip_smooth = CONFIG.SKIP_SMOOTH
        index_datain = [paths["index"], paths["datain"]]
        return Eddy(raw_dat, temp, bv, nthreads, skip_smooth, index_datain)

    def run(self):
        if (os.path.isfile(self.ap) and os.path.isfile(self.pa) and os.path.isfile(self.bvecs) and
                os.path.isfile(self.bvals)) and not os.path.isfile(self.data):
            if not os.path.isfile(self.topup):
                self.make_topup()

            if not os.path.isfile(self.nodif) or not os.path.isfile(self.brain):
                self.make_brain()

            if not os.path.isfile(self.ap_denoised) and not self.skip_smooth:
                self.denoise()
            self.eddy()
        else:
            raise FileNotFoundError('Base Files Missing')

        toolbox.run_commands(self.commands, self.env)
        print('Eddy correction done')

    def make_topup(self):
        self.commands.append(toolbox.get_command('fslroi', (self.ap, self.nodif, 0, 1)))
        self.commands.append(toolbox.get_command('fslroi', (self.pa, self.nodif_pa, 0, 1)))
        self.commands.append(toolbox.get_command('fslmerge', (self.nodif, self.nodif_pa), t=self.merged_b0))
        self.commands.append(toolbox.get_command('topup', imain=self.merged_b0, datain=self.index_datain[1],
                                                 config='b02b0.cnf', out=f'{self.topup}out', iout=self.topup,
                                                 fout=f'{self.topup}_fout'))

    def make_brain(self):
        self.commands.append(toolbox.get_command('fslmaths', (self.topup,), Tmean=self.nodif))
        self.commands.append(toolbox.get_command('bet', (self.nodif, self.brain, '-m'), f=0.2))

    def denoise(self):
        self.commands.append(toolbox.get_command("denoise", (self.ap_denoised, 'force'), mask=self.mask))

    def eddy(self):
        self.commands.append(toolbox.get_command(f'eddy_openmp', ('data_is_shelled',), imain=self.ap_denoised,
                                                 mask=self.mask, index=self.index_datain[0], acqp=self.index_datain[1],
                                                 bvecs=self.bvecs, bvals=self.bvals, fwhm=0, topup=f'{self.topup}out',
                                                 flm='quadratic', out=self.data))

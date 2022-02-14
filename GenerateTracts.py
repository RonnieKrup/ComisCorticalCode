from ComisCorticalCode import toolbox, stage
import nibabel as nb
import os


class GenerateTracts(stage.Stage):
    def __init__(self, *, brain, fod, tracts, ntracts, lenscale_min, lenscale_max, stepscale, angle, mask, segmentation, bv,
                 sifted_tracts, nthreads, minvol):
        self.brain = brain
        self.fod = fod
        self.tracts = tracts
        self.ntracts = ntracts
        self.lenscale_min = lenscale_min
        self.lenscale_max = lenscale_max
        self.stepscale = stepscale
        self.angle = angle
        self.mask = mask
        self.segmentation = segmentation
        self.bv = bv
        self.sifted_tracts = sifted_tracts
        self.nthreads = nthreads
        self.minvol = minvol

    @staticmethod
    def create_from_dict(paths, config):
        brain = paths['brain']
        fod = paths["fod"]
        tracts = paths["tracts"]
        ntracts = config.ntracts
        lenscale_min = config.lenscale_min
        lenscale_max = config.lenscale_max
        stepscale = config.stepscale
        angle = config.angle
        mask = paths["mask"]
        segmentation = paths["5tt"]
        bv = [paths['bvecs'], paths['bvals']]
        sifted_tracts = paths["sifted_tracts"]
        nthreads = config.nthreads
        minvol = config.minvol
        return GenerateTracts(brain=brain,
                              fod=fod,
                              tracts=tracts,
                              ntracts=ntracts,
                              lenscale_min=lenscale_min,
                              lenscale_max=lenscale_max,
                              stepscale=stepscale,
                              angle=angle,
                              mask=mask,
                              segmentation=segmentation,
                              bv=bv,
                              sifted_tracts=sifted_tracts,
                              nthreads=nthreads,
                              minvol=minvol)

    # @property
    def needed_files(self):
        """The files that are required to exist for this stage to finish."""
        return self.tracts, self.sifted_tracts

    # @property
    def parameters_for_comparing_past_runs(self):
        """If these parameters are the same in a previous run, we can re-use the results."""
        return 'minvol', 'ntracts', 'lenscale_min','lenscale_max',  'stepscale', 'angle'

    def make_commands_for_stage(self):
        """If needed to generate the stage output, these commands need to run."""
        diff = nb.load(self.brain)
        pixdim = diff.header['pixdim'][1]
        commands = [
                    toolbox.ExternalCommand.get_command("tckgen", self.fod, self.tracts, "-force",
                                                        f'-algorithm SD_STREAM', f'-select {int(self.ntracts * 100)}',
                                                        f'-step {pixdim * self.stepscale}',
                                                        f'-minlength {pixdim * self.lenscale_min}',
                                                        f'-maxlength {pixdim * self.lenscale_max}',
                                                        f'-angle {self.angle}', f'-seed_image {self.mask}',
                                                        f'-act {self.segmentation}', f'-fslgrad {" ".join(self.bv)}',
                                                        f'-nthreads {self.nthreads}',
                                                        output_files=(self.tracts,),
                                                        input_files=(self.fod, self.mask, self.segmentation)),

                    toolbox.ExternalCommand.get_command("tcksift", self.tracts, self.fod, self.sifted_tracts, "-force",
                                                        "-fd_scale_gm", f'-act {self.segmentation}',
                                                        f'-nthreads {self.nthreads}', f'-term_number {self.ntracts}',
                                                        input_files=(self.tracts, self.fod, self.segmentation),
                                                        output_files=(self.sifted_tracts,))
                    ]
        return commands

from ComisCorticalCode import CSV, toolbox
import nibabel as nb
import os


class Generate_tracts:
    def __init__(self, *, brain, fod, tracts, ntracts, lenscale, stepscale, angle, mask, segmentation, bv, sifted_tracts,
                 nthreads):
        self.brain = brain
        self.fod = fod
        self.tracts = tracts
        self.ntracts = ntracts
        self.lenscale = lenscale
        self.stepscale = stepscale
        self.angle = angle
        self.mask = mask
        self.segmentation = segmentation
        self.bv = bv
        self.sifted_tracts = sifted_tracts
        self.nthreads = nthreads

    @staticmethod
    def create_from_dict(paths, config):
        brain = paths['brain']
        fod = paths["fod"]
        tracts = paths["tracts"]
        ntracts = config.NTRACTS
        lenscale = config.LENSCALE
        stepscale = config.STEPSCALE
        angle = config.ANGLE
        mask = paths["brain_mask"]
        segmentation = paths["5tt"]
        bv = [paths['bvecs'], paths['bvals']]
        sifted_tracts = paths["sifted_tracts"]
        nthreads = config.NTHREADS
        return Generate_tracts(brain=brain,
                               fod=fod,
                               tracts=tracts,
                               ntracts=ntracts,
                               lenscale=lenscale,
                               stepscale=stepscale,
                               angle=angle,
                               mask=mask,
                               segmentation=segmentation,
                               bv=bv,
                               sifted_tracts=sifted_tracts,
                               nthreads=nthreads)

    def run(self):
        commands = []
        if not os.path.isfile(self.fod):
            past_run = CSV.find_past_runs(['MINVOL', 'NTRACTS', 'LINSCALE', 'STEPSCALE', 'ANGLE'])
            if past_run:
                needed_files = (self.tracts, self.sifted_tracts)
                toolbox.make_link(past_run, needed_files)
            else:
                commands.extend(self.make_commands_generate_tracts())
        for command in commands:
            command.run_commands(commands)

    def make_commands_generate_tracts(self):
        commands = []
        diff = nb.load(self.brain)
        pixdim = diff.header['pixdim'][1]
        commands.append(toolbox.ExternalToolExecution.get_command("tckgen", (self.fod, self.tracts, "-force"),
                                                                  algorithm="SD_STREAM", select=self.ntracts,
                                                                  step=pixdim * self.stepscale,
                                                                  minlength=pixdim * self.lenscale[0],
                                                                  maxlength=pixdim * self.lenscale[0],
                                                                  angle=self.angle, seed_image=self.mask,
                                                                  act=self.segmentation, fslgrad=" ".join(self.bv)))

        commands.append(toolbox.ExternalToolExecution.get_command("tcksift", (self.tracts, self.fod, self.sifted_tracts,
                                                                              "-force", "-fd_scale_gm"),
                                                                  act=self.segmentation, nthreads=self.nthreads,
                                                                  term_number=self.ntracts*0.1))
        return commands


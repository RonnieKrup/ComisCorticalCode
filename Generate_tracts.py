from ComisCorticalCode import CONFIG, CSV, toolbox
import nibabel as nb
import os

class Generate_tracts:
    def __init__(self, brain, fod, tracts, ntracts, lenscale, stepscale, angle, mask, segmentation, bv, sifted_tracts,
                 nthreads):
        self.commands = []
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
    def Create_from_dict(paths):
        brain = paths['brain']
        fod = paths["fod"]
        tracts = paths["tracts"]
        ntracts = CONFIG.NTRACTS
        lenscale = CONFIG.LENSCALE
        stepscale = CONFIG.STEPSCALE
        angle = CONFIG.ANGLE
        mask = paths["brain_mask"]
        segmentation = paths["5tt"]
        bv = [paths['bvecs'], paths['bvals']]
        sifted_tracts = paths["sifted_tracts"]
        nthreads = CONFIG.NTHREADS
        return Generate_tracts(brain, fod, tracts, ntracts, lenscale, stepscale, angle, mask, segmentation, bv,
                               sifted_tracts, nthreads)

    def run(self):
        if not os.path.isfile(self.fod):
            past_run = CSV.find_past_runs(['MINVOL', 'NTRACTS', 'LINSCALE', 'STEPSCALE', 'ANGLE'])
            if past_run:
                needed_files = (self.tracts, self.sifted_tracts)
                toolbox.make_link(past_run, needed_files)
            else:
                self.generate_tracts()
        toolbox.run_commands(self.commands)

    def generate_tracts(self):
        diff = nb.load(self.brain)
        pixdim = diff.header['pixdim'][1]
        self.commands.append(toolbox.get_command("tckgen", (self.fod, self.tracts, "-force"), algorithm="SD_STREAM",
                             select=self.ntracts, step=pixdim * self.stepscale, minlength=pixdim * self.lenscale[0],
                             maxlength=pixdim * self.lenscale[0], angle=self.angle, seed_image=self.mask,
                             act=self.segmentation, fslgrad=" ".join(self.bv)))

        self.commands.append(toolbox.get_command("tcksift", (self.tracts, self.fod, self.sifted_tracts, "-force",
                                                             "-fd_scale_gm"), act=self.segmentation,
                                                 nthreads=self.nthreads, term_number=self.ntracts*0.1))

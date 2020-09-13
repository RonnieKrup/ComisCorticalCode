from ComisCorticalCode import CONFIG, CSV, toolbox
import os
import nibabel as nb
import numpy as np


class Siftt_to_atlas():
    def __init__(self, atlas, atlas_for_connectome, temp, nthreads, tracts, fod, sifted_atlas_tracts, segmentation,
                 ntracts):
        self.commands = []
        self.atlas = atlas
        self.atlas_for_connectome = atlas_for_connectome
        self.connectome_atlas = os.path.join(temp, 'conncetome_atlas.nii.gz')
        self.temp = temp
        self.nthreads = nthreads
        self.connectome_out = os.path.join(self.temp, 'out')
        self.tracts = tracts
        self.atlas_tracts = os.path.join(temp, 'atlas_tracts.tck')
        self.fod = fod
        self.sifted_atlas_tracts = sifted_atlas_tracts
        self.segmentation = segmentation
        self.ntracts = ntracts

    @staticmethod
    def create_from_dict(paths):
        atlas = paths['atlas']
        atlas_for_connectome = CONFIG.ATLAS_FOR_CONNECTOME
        temp = paths['temp']
        nthreads = CONFIG.NTHREADS
        tracts = paths["tracts"]
        fod = paths['fod']
        sifted_atlas_tracts = paths["sifted_atlas_tracts"]
        segmentation = paths["5tt"]
        ntracts = CONFIG.NTRACTS
        return Sift_to_atlas(atlas, atlas_for_connectome, temp, nthreads, tracts, fod, sifted_atlas_tracts,
                             segmentation, ntracts)

    def run(self):
        if not os.path.isfile(self.fod):
            past_run = CSV.find_past_runs(['MINVOL', 'NTRACTS', 'LINSCALE', 'STEPSCALE', 'ANGLE', 'ATLAS'])
            if past_run:
                needed_files = (self.atlas_tracts,)
                toolbox.make_link(past_run, needed_files)
            else:
                self.sift_atlas()
        toolbox.run_commands(self.commands)

    def sift_atlas(self):
        self.commands.append(toolbox.get_command("labelconvert", (self.atlas, self.atlas_for_connectome,
                                                                  self.atlas_for_connectome('.txt', '_converted.txt'),
                                                                  self.connectome_atlas, "force"),
                                                 nthreads=self.nthreads))
        self.commands.append(toolbox.get_command("tck2connectome", (self.connectome_atlas,
                                                                    os.path.join(self.temp, 'connectome'), "-force"),
                                                 nthreads=self.nthreads, assignment_radial_search=2,
                                                 out_assignments=self.connectome_out))
        self.commands.append(toolbox.get_command("connectome2tck", (self.tracts, self.connectome_out, self.atlas_tracts,
                                                  "-exclusive", "-keep_self", "-force"), nthreads=self.nthreads,
                                                 nodes=self.list_of_nodes(), files="single"))
        self.commands.append(toolbox.get_command("tcksift", (self.atlas_tracts, self.fod, self.sifted_atlas_tracts,
                                                             "-force", "-fd_scale_gm"), act=self.segmentation,
                                                 nthreads=self.nthreads, term_number=self.ntracts * 0.1))

    def list_of_nodes(self):
        parc = nb.load(self.atlas).get_data()
        return ",".join([str(i) for i in range(1, len(np.unique(parc)))])

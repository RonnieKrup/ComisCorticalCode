import os

from ComisCorticalCode import CSV
from ComisCorticalCode import toolbox


class BaseStage:
    def run(self):
        raise NotImplementedError()


class Stage(BaseStage):
    @property
    def needed_files(self):
        """The files that are required to exist for this stage to finish."""
        raise NotImplementedError()

    @property
    def parameters_for_comparing_past_runs(self):
        """If these parameters are the same in a previous run, we can re-use the results."""
        raise NotImplementedError()

    def make_commands_for_stage(self):
        """If needed to generate the stage output, these commands need to run."""
        raise NotImplementedError()

    def needs_to_run(self):
        for f in self.needed_files:
            if not os.path.isfile(f):
                return True
        return False

    def run(self):
        if not self.needs_to_run():
            return

        past_run = CSV.find_past_runs(self.parameters_for_comparing_past_runs)
        if past_run:
            toolbox.make_link(past_run, self.needed_files)
            return

        for command in self.make_commands_for_stage():
            command.run()

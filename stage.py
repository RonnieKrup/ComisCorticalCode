import os
import pandas as pd
from ComisCorticalCode import toolbox


class BaseStage:
    def run_stage(self, run_path):
        raise NotImplementedError()


class Stage(BaseStage):
    def needed_files(self):
        """The files that are required to exist for this stage to finish."""
        raise NotImplementedError()

    @property
    def parameters_for_comparing_past_runs(self):
        """If these parameters are the same in a previous run, we can re-use the results."""
        raise NotImplementedError()

    def make_commands_for_stage(self):
        """If needed to generate the stage output, these commands need to run."""
        raise NotImplementedError('Not yet implemented in %s' % type(self))

    def needs_to_run(self):
        for f in self.needed_files():
            if not os.path.isfile(f):
                return True
        return False

    def run_stage(self, run_path):
        if not self.needs_to_run():
            return
        if run_path:
            past_run = self.find_past_runs_(run_path)
            if past_run:
                toolbox.make_link(past_run, self.needed_files)
                return

        for command in self.make_commands_for_stage():
            command.run_command()

    def find_past_runs_(self, runs_path):
        runs = pd.read_csv(runs_path, index_col='Name')
        relevant_runs = runs
        for param in self.parameters_for_comparing_past_runs():
            relevant_runs = relevant_runs[relevant_runs[param] == getattr(self, param)]
        if len(relevant_runs):
            return relevant_runs.index[0]
        else:
            return None

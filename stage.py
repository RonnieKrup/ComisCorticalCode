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

    def run_commands(self):
        for command in self.make_commands_for_stage():
            command.run_command()

    def run_stage(self, run_path):
        if not self.needs_to_run():
            return
        if run_path:
            past_runs = self.find_past_runs_(run_path)
            missing_some_files = False
            for result_file in self.needed_files():
                for past_run in past_runs:
                    old_path = toolbox.get_file_from_past_run(result_file, past_run)
                    if os.path.isfile(old_path):
                        toolbox.make_link(past_run, result_file)
                        # We don't need to check other past runs FOR THIS FLIE
                        break
                # There was no break when going over the past runs
                else:
                    missing_some_files = True
            if not missing_some_files:
                # All good
                return
        self.run_commands()

    def find_past_runs_(self, runs_path):
        runs = pd.read_csv(runs_path, index_col='run_name')
        relevant_runs = runs
        for param in self.parameters_for_comparing_past_runs():
            relevant_runs = relevant_runs[relevant_runs[param] == getattr(self, param)]
        return relevant_runs.index

import os
import shutil

from unittest import TestCase
from unittest.mock import patch
from ComisCorticalCode.PreProcessing import stage, run_preprocessing, run_for_sub, Config
import tempfile


class LocalRunnerInProcess(run_preprocessing.Runner):
    def run_all_subjects(self, config, sub_dirs, out):
        for sub_dir in sub_dirs:
            run_for_sub.run_for_sub(sub_dir, config.run_name, out)


class TestStage(stage.Stage):
    num_runs = 0

    def __init__(self, paths_for_subject, config):
        self.stepscale = config.stepscale
        self.my_result_file = paths_for_subject['brain']

    @staticmethod
    def create_from_dict(paths_for_subject, config):
        return TestStage(paths_for_subject, config)

    def needed_files(self):
        return [self.my_result_file]

    def parameters_for_comparing_past_runs(self):
        return ["stepscale"]

    def run_commands(self):
        TestStage.num_runs += 1
        with open(self.my_result_file, 'w'):
            pass

def our_generate_stages(config):
    return [TestStage]


class TestRunPreprocessing(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.addCleanup(lambda: shutil.rmtree(self.tmp_dir))

        self.test_config = Config.Config()
        self.test_config.minvol = 42
        self.test_config.out = os.path.join(self.tmp_dir, 'out')
        self.test_config.atlas = os.path.join(self.tmp_dir, 'atlas.txt')
        self.test_config.run_list = os.path.join(self.tmp_dir, 'runs.csv')
        self.test_config.data_path = os.path.join(self.tmp_dir, 'hcp')

    @patch('ComisCorticalCode.run_for_sub.generate_stages_to_run', our_generate_stages)
    def test_make_sh_files(self):
        os.makedirs(os.path.join(self.test_config.data_path, 'sub1'))
        self.test_config.validate_config_values()

        run_preprocessing.run_with_config_and_runner(self.test_config, LocalRunnerInProcess())
        run_preprocessing.run_with_config_and_runner(self.test_config, LocalRunnerInProcess())

        self.assertEqual(TestStage.num_runs, 1, 'Expected one run of step')

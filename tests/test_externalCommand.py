from unittest import TestCase
from unittest.mock import patch
from ComisCorticalCode.PreProcessing import toolbox
import os
import tempfile
import unittest


def create_file(path):
    with open(path, 'w'):
        pass


class TestExternalCommand(TestCase):
    # See here
    # https://docs.python.org/3/library/unittest.mock.html#quick-guide
    @patch('subprocess.check_call')
    def test_fail_on_missing_input_file(self, check_call_mock):
        with tempfile.TemporaryDirectory() as my_dir:
            create_file(os.path.join(my_dir, '1.txt'))
            create_file(os.path.join(my_dir, '2.txt'))

            cmd = toolbox.ExternalCommand.get_command('bla', input_files=(
                os.path.join(my_dir, '1.txt'),
                os.path.join(my_dir, '2.txt'),
                os.path.join(my_dir, '3.txt'),
            ))

            try:
                cmd.run_command()
                # If we got here, we didn't throw an exception
                self.fail('Should have thrown an error on missing input file')
            except FileNotFoundError:
                pass

    @patch('subprocess.check_call')
    def test_fail_on_missing_output_file(self, check_call_mock):
        with tempfile.TemporaryDirectory() as my_dir:
            create_file(os.path.join(my_dir, '1.txt'))
            create_file(os.path.join(my_dir, '2.txt'))

            cmd = toolbox.ExternalCommand.get_command('bla', output_files=(
                os.path.join(my_dir, '1.txt'),
                os.path.join(my_dir, '2.txt'),
                os.path.join(my_dir, '3.txt'),
            ))

            try:
                cmd.run_command()
                # If we got here, we didn't throw an exception
                self.fail('Should have thrown an error on missing output file')
            except FileNotFoundError:
                pass

    @patch('subprocess.check_call')
    def test_actually_runs_command(self, check_call_mock):
        cmd = toolbox.ExternalCommand.get_command('bla', 'arg1', 'arg2', key1='hi', key2='bye')

        cmd.run_command()

        # See instructions here
        # https://docs.python.org/3/library/unittest.mock.html#quick-guide
        check_call_mock.assert_called_with('bla arg1 arg2 --key1=hi --key2=bye', shell=True, env=os.environ)

"""
class TestExternalCommand(TestCase):
    def test_get_command(self):
        base_path = r'E:\Ronniek\ComisCorticalCode\test_data'
        filenames = ['mprage', 'bvals', 'dif_AP.nii.gz']
        paths = [fr'{base_path}\{filename}' for filename in filenames]
        program = 'program'
        input_files = paths[:3]
        output_files = paths[3:]
        arg = ('foo', 'bar')
        kwarg = ('oof', 'rab')
        command = toolbox.ExternalCommand.get_command(program, arg[0], arg[1], input_files=input_files,
                                                      output_files=output_files, kwarg0=kwarg[0], kwarg1=kwarg[1])

        self.assertEqual(command.command, f'{program} {arg[0]} {arg[1]}, kwarg0={kwarg[0]} kwarg1={kwarg[1]}')
        self.assertEqual(command.input_files, input_files)
        self.assertEqual(command.output_files, output_files)

    def test_find_missing_files(self):
        base_path = r'E:\Ronniek\ComisCorticalCode\test_data'
        filenames = ['text.txt', 'mprage', 'foo', 'bvals', 'dif_AP.nii.gz']
        paths = [fr'{base_path}\{filename}' for filename in filenames]
        missing_files = toolbox.ExternalCommand.find_missing_files(paths)
        self.assertEqual(missing_files, paths[:3])


class TestToolbox(TestCase):
    def test_make_link(self):
        base_path = r'E:\Ronniek\ComisCorticalCode\test_data\raw_data'
        files_to_link = [os.path.join(base_path, 'foo', 'new_mprage.nii.gz'),
                         os.path.join(base_path, 'foo2', 'new_bvecs.nii.gz')]
        old_name = 'old'
        toolbox.make_link(old_name, files_to_link)
        # how do I check this in a dry run?
"""

if __name__ == '__main__':
    unittest.main()

#!/bin/bash
#$ -cwd
#$ -e OUT_PATH/qstOut/JOB_NAME.ERR
#$ -o OUT_PATH/qstOut/JOB_NAME.OUT


# Creating a file:
# touch /path/to/file

VENV_ACTIVATE
cd MY_DIR || { echo "couldn't activate venv"; exit 1; }
touch OUT_PATH/jobs/RUN_NAME/JOB_NAME.STARTED
python SCRIPT_TO_RUN SUBJECT_PATH RUN_NAME OUT_PATH
# TODO: change to "FAILED" if script fails
mv OUT_PATH/jobs/RUN_NAME/JOB_NAME.STARTED OUT_PATH/jobs/RUN_NAME/JOB_NAME.DONE
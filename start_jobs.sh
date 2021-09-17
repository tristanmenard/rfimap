#!/bin/bash
# Submits all job scripts for a project that were created by job_template.py.
# 1 require argument: the working directory path
# Example usage: ./start_jobs.sh /scratch/g/group/user/projectname

work_dir=$1
if [ -d $work_dir ]; then
    cd $work_dir

    #jobs=./node*/*_job.sh
    #echo $jobs

    jobs=$(find ./node*/*_job.sh)

    for JOB in $jobs
    do
        echo "Submitting $JOB"
        sbatch $JOB
        sleep 1
    done
else
    echo "$work_dir does not exist."
fi



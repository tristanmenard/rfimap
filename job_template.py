import datetime
import pathlib
from argparse import ArgumentParser

"""
Example usage: python job_template.py 240 Z:\Documents\ALBATROS\rfi_propagation_mapper testproject /project/s/sievers/tristanm
"""
parser = ArgumentParser(description='Template bash script for a job on a given node.')
# parser.add_argument('node_number', type=int, help='node number of the job')
parser.add_argument('total_txs', type=int, help='total number of transmitters')
parser.add_argument('--txs_per_node', type=int, default=80, help='amount of single transmitter power maps computed per node (recommended: 40-80)')
parser.add_argument('work_dir', type=str, help='directory used for Niagara jobs')
parser.add_argument('project_name', type=str, help='project name')
parser.add_argument('rasp_dir', type=str, help='path to local rasp directory (excluding rasp directory from path)')
parser.add_argument('--max_time', type=float, default=3, help='maximum time in hours allowed for the job to complete on a given node')
parser.add_argument('--python_env_bin', type=str, default='~/.virtualenvs/myenv/bin', help='bin directory for custom python environment')
args = parser.parse_args()

work_dir = pathlib.Path(args.work_dir)
rasp_dir = pathlib.Path(args.rasp_dir)
python_env_bin = pathlib.Path(args.python_env_bin)
python_env_activate = python_env_bin.joinpath('activate')

total_nodes = (args.total_txs-1) // args.txs_per_node + 1
max_time = str(datetime.timedelta(hours=args.max_time))

for node_num in range(total_nodes):
	bash_fname = work_dir.joinpath(f'node{node_num}/{args.project_name}_node{node_num}_job.sh')
	bash_fname.parent.mkdir(parents=True, exist_ok=True)

	txfirst = node_num*80
	txlast = (node_num+1)*80-1
	if node_num == total_nodes - 1:
		txlast = args.total_txs - 1

	template = f"""#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node={args.txs_per_node}
#SBATCH --time={max_time}
#SBATCH --job-name {args.project_name}_{node_num}
#SBATCH --mail-type=FAIL

# Go to job working directory
cd {work_dir}

# Turn off implicit threading in Python
export OMP_NUM_THREADS=1

# Load gnu-parallel
module load gnu-parallel

# Activate custom python 3 environment
source {python_env_activate}

# Add rasp to PYTHONPATH
export PYTHONPATH="$PYTHONPATH:{rasp_dir}"

parallel --joblog slurm-$SLURM_JOBID.log -j $SLURM_TASKS_PER_NODE "python singleTxmap.py {{}} {node_num}" ::: {{{txfirst}..{txlast}}}
"""

	with open(bash_fname, 'w') as f:
		f.write(template)

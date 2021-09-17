# rfimap
Scripts intended for serially computing RFI propagation maps using the computational power of the [Niagara supercomputer](https://docs.scinet.utoronto.ca/index.php/Niagara_Quickstart) with [GNU Parallel](https://www.gnu.org/software/parallel/). The scripts are based on [rasp](https://github.com/tristanmenard/rasp), a python implementation of the [Longley-Rice](https://www.its.bldrdoc.gov/research-topics/radio-propagation-software/itm/itm.aspx) signal propagation model.

## Setup
### Dependencies
`rasp`, `numba`, `numpy`, `pandas`, `pathlib`, `requests`, `tqdm`, `dbfread`, `zipfile`, `toml`, `pickle`, `datetime`

### Useful mapping tools
`matplotlib`, `folium`, `geojsoncontour`

### Setup instructions
1. Login to Niagara and create a custom python 3 environment with all required packages and versions.
  * [Niagara login instructions](https://docs.scinet.utoronto.ca/index.php/Niagara_Quickstart#Getting_started_on_Niagara)
  * [How to create a custom python 3 environment on Niagara](https://docs.scinet.utoronto.ca/index.php/Installing_your_own_Python_Modules#Using_Virtualenv_in_Regular_Python)
2. Clone rasp and rfimap to some directory of your choosing on the supercomputer (I will use the convention /project/group/user to signify that it should be a directory in your /project space on Niagara).
  ```
  cd /project/group/user
  git clone https://github.com/tristanmenard/rasp.git
  git clone https://github.com/tristanmenard/rfimap.git
  ```

3. Set the config.toml settings according to your project specifications.
  ```
  cd rasp
  nano config.toml
  ```
  Under `[general]`, set `threads = 1` to force rasp to only use 1 CPU thread and which helps speed up the computational process while using GNU Parallel. Under `[data]`, choose a location for your cache directories (likely in the /project filesystem on Niagara). Do not leave these fields empty when running rasp on Niagara.

## How to use rfimap
1. Upon logging in to Niagara, activate your custom python 3 environment. If needed, replace `~/.virtualenvs/myenv/bin` below with the path to your own custom python 3 environment.
```
source ~/.virtualenvs/myenv/bin/activate
```

2. Add rasp to your PYTHONPATH with the following line:
```
export PYTHONPATH=$PYTHONPATH:/project/group/user
```
where `/project/group/user` is the path to the directory that contains rasp (i.e. the parent directory for rasp).

2. Navigate to your rfimap directory and run the elevation data and transmitter data preparation scripts.
```
Example:
cd /project/group/user/rfimap
python prepare_terrain.py "-72.26 -65.07 49.13 53.63" "-70.10 -67.23 50.48 52.28" -w -s /scratch/directory/of/your/choice/filename.pickle
python prepare_txdb.py "-72.26 -65.07 49.13 53.63" -f1 20 -f2 200 -w -s /scratch/directory/of/your/choice/filename.csv
```
The outer bounds of the elevation data and transmitter database is `"-72.26 -65.07 49.13 53.63"` where the values represent the outermost west, east, south, and north latitude/longitude in degrees, respectively. The outer bounds should be the same in both `prepare_terrain.py` and `prepare_txdb.py`. The bounds of the region of interest (the region where RFI propagation is calculated) is `"-70.10 -67.23 50.48 52.28"` in the same west, east, south, north format as previously. The region of interest bounds should be completely within the outer bounds. `-f1` sets the lowest transmitter frequency to include in the RFI map and `-f2` sets the highest transmitter frequency. The `-w` options retrieves data from the web. Alternatively, the `-c` option can be used to retrieve cached data if it has already been retrieved from the web. The `-s` option allows the user to specify the location where the data object will be saved. Note that retrieving web data from Niagara can be slow, and it may be faster to download the data to your local machine and then transfer the data files to Niagara.

3. A message at the end of the `prepare_txdb.py` script will inform you about how many transmitters were found within your search criteria. Now, run `job_template.py`. This script will populate your working directory (`/scratch/group/user/projectname`) with a folder and job script for each node required for the project. By default, `rfimap` will run 80 transmitters per node but this can be changed with the `--txs_per_node` option for `job_template.py`.
```
Example:
python job_template.py 3303 /scratch/group/user/projectname /project/group/user --python_env_bin ~/.virtualenvs/myenv/bin
```
where 3303 is the number of transmitters, `/scratch/group/user/projectname` is the working directory where the jobs will happen, `/project/group/user` is the location of the rasp directory so it can be added to the PYTHONPATH on every core, and `--python_env_bin` gives the location of the custom python 3 environment that will need to be run on every core.

4. Start all the jobs.


## Resources
* [GNU Parallel basics](https://docs.computecanada.ca/wiki/GNU_Parallel)
* [Running serial jobs on Niagara](https://docs.scinet.utoronto.ca/index.php/Running_Serial_Jobs_on_Niagara)

## Future improvements
* Implement 1 job script to rule them all! (rather than 1 job script for every node) See [example](https://docs.scinet.utoronto.ca/index.php/Running_Serial_Jobs_on_Niagara#Version_for_more_than_1_node_at_once).

## Known Issues
* September 15 2021: TAFL transmitter data currently has a delimiter error in the CSV file. If you encounter `ValueError: could not convert string to float: '7K60F1W'`, you can edit the TAFL_LTAF.csv file (found in your cache directory) by replacing the first `"` after E369 on line 127551 with `'`. As of the newest version of rasp, this should be attempted automatically by rasp. If the error persists, you must investigate the CSV file manually.

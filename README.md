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
2. Clone rasp and rfimap to some directory of your choosing on the supercomputer (I will use the convention `/project/g/group/user` to signify that it should be a directory in your /project space on Niagara).
  ```
  cd /project/g/group/user
  git clone https://github.com/tristanmenard/rasp.git
  git clone https://github.com/tristanmenard/rfimap.git
  ```

3. Set the config.toml settings according to your project specifications.
  ```
  nano rasp/config.toml
  ```
  Under `[general]`, set `threads = 1`. This forces rasp to only use 1 CPU thread and helps speed up the computational process by reducing conflict with GNU Parallel. Under `[data]`, choose a location for your cache directories (likely in the /project filesystem on Niagara). Do not leave these fields empty when running rasp on Niagara.

## How to use rfimap
1. Upon logging in to Niagara, activate your custom python 3 environment. If needed, replace `~/.virtualenvs/myenv/bin` below with the path to your own custom python 3 environment.
```
source ~/.virtualenvs/myenv/bin/activate
```

2. Add rasp to your PYTHONPATH with the following line:
```
export PYTHONPATH=$PYTHONPATH:/project/g/group/user
```
where `/project/g/group/user` is the path to the directory that contains rasp (i.e. the parent directory for rasp).

3. Create the working directory for the jobs to run. I will use the convention `/scratch/g/group/user/projectname` to signify that it should be in your /scratch space on Niagara.
```
mkdir /scratch/g/group/user/projectname
```
Copy `singleTxmap.py` to your working directory.
```
cp /project/g/group/user/rfimap/singleTxmap.py /scratch/g/group/user/projectname/singleTxmap.py
```

(optional) I like to create another directory in the /project filesystem to keep some data, like the elevation and transmitter info, that can be useful for mapping later on.
```
mkdir /project/g/group/user/projectname
```

4. Navigate to your `rfimap` directory and run the elevation data and transmitter data preparation scripts.
```
cd /project/g/group/user/rfimap
python prepare_terrain.py "W E S N" "W E S N" -w -s /project/g/group/user/projectname/elevfname.pickle
```
  * The first argument gives the outer bounds of the elevation data as a space-delimited string with 4 values. The values represent the outermost west, east, south, and north latitudes/longitudes in degrees (in that order). Longitudes in the western hemisphere and latitudes in the southern hemisphere are represented by negative values.
  * The second argument gives the bounds for the region of interest (the region where RFI propagation is calculated) in the same format as above. The region of interest should be completely inside the outer bounds.
  * The `-w` option retrieves data from the web. Note that downloading from the web on Niagara can be slow. It may be faster to download the data to your local machine and then transfer the data files to Niagara.
  * The `-c` option can be used instead of `-w` to retrieve cached data that has already been downloaded from the web.
  * The `-s` option allows the user to specify the location where the data object will be saved.

```
python prepare_txdb.py "W E S N" -f1 20 -f2 250 -w -s /project/g/group/user/projectname/txdbfname.csv
```
  * The first argument gives the outer bounds of the transmitter database. These should almost always be the same as the outer bounds given in `prepare_terrain.py`.
  * `-f1` sets the lowest transmitter frequency to include from the database and `-f2` sets the highest transmitter frequency (both in MHz). They default to 20 MHz and 20 GHz, respectively.
  * The `-w`, `-c`, and `-s` options work the same way as they do in `prepare_terrain.py`
  * A message near the end of the `prepare_txdb.py` script will inform you about how many transmitters were found within your search criteria.

5. Now, run `job_template.py`. This script will populate your working directory with a folder and job script for each node required for the project. By default, `rfimap` will run 80 transmitters per node but this can be changed with the `--txs_per_node` option. Also, the `--max_time` option can be used to change the maximum time in hours allowed for the job to complete. The default value is 3 hours.
```
python job_template.py /scratch/g/group/user/projectname /project/g/group/user /project/g/group/user/projectname/elevfname.pickle /project/g/group/user/projectname/txdbfname.csv --python_env_bin ~/.virtualenvs/myenv/bin
```
  * The first argument is the working directory for the project.
  * The second argument is the parent directory for rasp.
  * The third argument gives the absolute path to the pickled elevation data file.
  * The fourth argument gives the absolute path to the CSV transmitter database for the project.
  * The `--python_env_bin` option gives the path to the custom python 3 environment.

6. Start all the jobs.

7. Check in log files that all jobs completed successfully.


## Resources
* [GNU Parallel basics](https://docs.computecanada.ca/wiki/GNU_Parallel)
* [Running serial jobs on Niagara](https://docs.scinet.utoronto.ca/index.php/Running_Serial_Jobs_on_Niagara)

## Future improvements
* 1 job script to rule them all! (rather than 1 job script for every node) See [example](https://docs.scinet.utoronto.ca/index.php/Running_Serial_Jobs_on_Niagara#Version_for_more_than_1_node_at_once).

## Known Issues
* September 15 2021: TAFL transmitter data currently has a delimiter error in the CSV file. If you encounter `ValueError: could not convert string to float: '7K60F1W'`, you can edit the TAFL_LTAF.csv file (found in your cache directory) by replacing the first `"` after E369 on line 127551 with `'`. As of the newest version of rasp, this should be attempted automatically by rasp. If the error persists, you must investigate the CSV file manually.

# rfimap
Scripts intended for serially computing RFI propagation maps using the computational power of the [https://docs.scinet.utoronto.ca/index.php/Niagara_Quickstart](Niagara supercomputer) with [https://www.gnu.org/software/parallel/](GNU Parallel). The scripts are based on [https://github.com/tristanmenard/rasp](rasp), a python implementation of the [https://www.its.bldrdoc.gov/research-topics/radio-propagation-software/itm/itm.aspx](Longey-Rice signal propagation model).

## Setup
### Dependencies
rasp, numba, pathlib, ...

### Setup instructions
1. Login to Niagara and create a custom python 3 environment with all required packages and versions.
  * [https://docs.scinet.utoronto.ca/index.php/Niagara_Quickstart#Getting_started_on_Niagara](Niagara login instructions)
  * [https://docs.scinet.utoronto.ca/index.php/Installing_your_own_Python_Modules#Using_Virtualenv_in_Regular_Python](How to create a custom python 3 environment on Niagara)
2. Clone rasp and rfimap to some directory of your choosing on the supercomputer (likely in the /project filesystem on Niagara).
  `cd /project/directory/of/your/choice`
  `clone https://github.com/tristanmenard/rasp.git`
  `clone https://github.com/tristanmenard/rfimap.git`
3. Set the config.toml settings according to your project specifications.
  `cd rasp`
  `nano config.toml`
  Under [general], set `threads = 1` to force rasp to only use 1 CPU thread and which helps speed up the computational process while using GNU Parallel. Under [data], choose a location for your cache directories (likely in the /project filesystem on Niagara). Do not leave these fields empty when running rasp on Niagara.

## How to use rfimap

## Resources
* [https://docs.computecanada.ca/wiki/GNU_Parallel](GNU Parallel basics)
* [https://docs.scinet.utoronto.ca/index.php/Running_Serial_Jobs_on_Niagara](Running serial jobs on Niagara)

## Future improvements
* Implement 1 job script to rule them all! (rather than 1 job script for every node) See [https://docs.scinet.utoronto.ca/index.php/Running_Serial_Jobs_on_Niagara#Version_for_more_than_1_node_at_once](example).

## Known Issues
* September 15 2021: TAFL transmitter data currently has a delimiter error in the CSV file. If you encounter `ValueError: could not convert string to float: '7K60F1W'`, you can edit the TAFL_LTAF.csv file (found in your cache directory) by replacing the first `"` after E369 on line 127551 with `'`. As of the newest version of rasp, this should be attempted automatically by rasp. If the error persists, you must investigate the CSV file manually.

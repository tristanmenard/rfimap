
timeit = False
if timeit:
	import time
	start = time.time()
import pandas as pd
import numpy as np
import rasp
import pathlib
from argparse import ArgumentParser

# TO DO: REMEMBER TO SET MAX_NUM_THREADS in rasp to 1 !!!

"""
Example usage: python singleTxmap.py 0 0 elevation_dict.pickle txdb.csv /scratch/s/username/dir
"""
parser = ArgumentParser(description='Signal propagation mapping of a transmitter using rasp')
parser.add_argument('job_number', type=int, help='gnu-parallel job number')
parser.add_argument('node_number', type=int, help='node number for job')
parser.add_argument('elevation_fname', type=str, help='path to elevation data file (.pickle)')
parser.add_argument('txdb_fname', type=str, help='path to transmitter database file (.csv)')
parser.add_argument('save_dir', type=str, help='directory where computed RFI power data is saved')

args = parser.parse_args()

job_number = args.job_number # actually the row index in transmitter database
node_num = args.node_number

save_dir = pathlib.Path(args.save_dir)
savemap_fname = save_dir.joinpath(f'node{node_num}/powermap_{job_number}.npy') # numpy binary array of power map
savetx_fname = save_dir.joinpath(f'node{node_num}/info_{job_number}.txt')


# hardcoded parameters
# values
rxheight = 3 # receiving antenna height above ground
txheight = 10 # default height for transmitting antenna above ground (if not data is not found in the database)
Ns = 301 # surface refractivity (N-units)
horizontal = True # horizontal polarization, set to False for vertical (can be done on a tx-by-tx basis as well)

# Load elevation data
elevation = rasp.data.file.load_elevation(args.elevation_fname) # region of interest is already set, if not uncomment the line below and choose desired bounds for the region of interest
# elevation.set_region_of_interest()

# Load local transmitter information (from pre-prepared csv file that only includes the following fields)
# Required fields: call_sign, frequency, latitude, longitude, erp
# Optional fields: height, ground_elevation
# Other fields: service, subservice
localtxdb = pd.read_csv(args.txdb_fname)
tx = localtxdb.iloc[job_number,:].copy()
# pandas dataframe is good enough format for our purposes. no need to convert to rasp TxDB object

# Calculate ITM signal propagation for the transmitter with rasp
if ~np.isnan(tx.ground_elevation):
	g_diff = tx.ground_elevation - elevation.get_elevation(tx.latitude, tx.longitude) # ground elevation difference between transmitter database and the SRTM3 elevation at the transmitter's location
	if ~np.isnan(tx.height):
		tx_height = tx.height + g_diff
		if tx_height <= 0: # if transmitter is "underground" according to this calculation, revert to original height
			tx_height = tx.height
	elif ~np.isnan(tx.haat):
		if tx.haat != 0:
			tx_height = tx.haat + g_diff
			if tx_height <= 0:
				if tx.haat < 0:
					tx_height = txheight
				elif tx.haat > 0:
					tx_height = tx.haat
		elif tx.haat == 0:
			tx_height = txheight + g_diff
			if tx_height <= 0:
				tx_height = txheight
	else:
		raise ValueError(f'Missing transmitter height information... (job number: {job_number:03})')
else:
	if ~np.isnan(tx.height):
		tx_height = tx.height
	elif ~np.isnan(tx.haat):
		if tx.haat > 0:
			tx_height = tx.haat
		elif tx.haat <= 0: # if haat is negative (or zero), revert to script's default transmitter height
			tx_height = txheight
	else:
		raise ValueError(f'Missing transmitter height information... (job number: {job_number:03})')

txattenuation_dB = elevation.attenuation_map(tx.latitude, tx.longitude, tx_height, rx_height=rxheight, frequency=tx.frequency, Ns=Ns, horizontal=horizontal)

# Calculate power from attenuation
txpower = rasp.utils.misc.dBW_to_watts(-txattenuation_dB + tx.erp + 2.15) # in watts

# Convert 1d array of powers to 2d map
# For a rectangular region of interest, can simply reshape the 1d array
powermap = txpower.reshape((len(np.unique(elevation.roi['inds'][0])), len(np.unique(elevation.roi['inds'][1]))))

# Save power map as binary array
np.save(savemap_fname, powermap)

# Save additional transmitter info in txt
service = rasp.data.taflcodes.service_code(tx.service)
subservice = rasp.data.taflcodes.subservice_code(tx.subservice)

if timeit:
	finish = time.time()

with open(savetx_fname, 'w') as f:
	f.write('call_sign\tfrequency\tservice\tsubservice\tlatitude\tlongitude\terp\theight\tground_elevation\thaat\ttx_height\n')
	f.write(f'{tx.call_sign}\t{tx.frequency}\t{service}\t{subservice}\t{np.degrees(tx.latitude)}\t{np.degrees(tx.longitude)}\t{tx.erp}\t{tx.height}\t{tx.ground_elevation}\t{tx.haat}\t{tx_height}\n')
	if timeit:
		f.write(f'run time: {round(finish-start,2)} s\n')

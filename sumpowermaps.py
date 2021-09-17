import numpy as np
import pathlib
from pandas import read_csv
from rasp import data.file.load_elevation
from argparse import ArgumentParser
from tqdm.auto import tqdm

"""
Example usage: python sumpowermaps.py /scratch/g/group/user/projectname /project/g/group/user/projectname/elevfname.pickle /project/g/group/user/projectname/txdb.csv
"""
parser = ArgumentParser(description='Sum RFI power maps together for a region of interest.')
parser.add_argument('project_dir', type=str, help='absolute path to working directory used for project')
parser.add_argument('elevfname', type=str, help='path to pickled elevation data file used for project')
parser.add_argument('txdbfname', type=str, help='path to transmitter database CSV file used for project')
parser.add_argument('--txs_per_node', type=float, default=80)
parser.add_argument('-p', '--plot', action='store_true')
args = parser.parse_args()

project_dir = pathlib.Path(args.project_dir)

elevation = load_elevation(args.elevation_fname)
# Latitude and longitude coordinates inside the region of interest given by inner_bounds
latitude_roi = np.unique(elevation.latitude_deg[elevation.roi['inds'][0]])
nlat = len(latitude_roi)
longitude_roi = np.unique(elevation.longitude_deg[elevation.roi['inds'][1]])
nlon = len(longitude_roi)

txdb = read_csv(args.txdbfname)
Ntxs = len(txdb)

totalpowermap = np.zeros((nlat, nlon))
with tqdm(total=Ntxs, unit='Tx') as pbar:
    for i, tx in enumerate(txdb):
        node_num = i // args.txs_per_node
        powermap = np.load(project_dir.joinpath(f'node{node_num}/powermap_{i}.npy'))
        totalpowermap = np.nansum([totalpowermap, powermap], axis=0)
        pbar.update()

if args.plot:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10,10))
    ax = plt.gca()
    im = ax.pcolormesh(longitude_roi, latitude_roi, 10*np.log10(totalpowermap))
    plt.grid(linestyle='--', alpha=0.8)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='2%', pad=0.05)
    plt.colorbar(im, cax=cax)
    # plt.savefig()
    plt.show()

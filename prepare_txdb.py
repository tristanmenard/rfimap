import numpy as np
import pandas as pd
import pathlib
import rasp
from extra_utils import save_txdb
from argparse import ArgumentParser

URL = 'http://www.ic.gc.ca/engineering/SMS_TAFL_Files/TAFL_LTAF.zip'
CSV = rasp.CACHE_DIR.joinpath('TAFL_LTAF.csv')

def import_TAFL(fname, radians=False, allow_duplicates=False, allow_nonoperational=False, allow_unauthorized=False):
    columns = [0,1,10,14,15,16,23,24,25,26,27,28,29,30,31,33,37,39,40,41,42,43,48,49,51,52,54,56,58,59]
    fieldnames = ['station_function','frequency','bandwidth','erp','power','loss','gain','pattern',
                  'half_power_beamwidth','fb_ratio','polarization','haat','azimuth','elevation_angle','location',
                  'call_sign','identical_stations','province','latitude','longitude','ground_elevation','height',
                  'service','subservice','authorization_status','in-service_date','licensee','operational_status',
                  'horizontal_power','vertical_power']
    dtypes = {'frequency': float,'bandwidth': float,'erp': float,'power': float,'loss': float,'gain': float,
              'pattern': str,'half_power_beamwidth': float,'fb_ratio': float,'haat': float,'azimuth': float,
              'elevation_angle': float,'latitude': float,'longitude': float,'ground_elevation': float,'height': float,
              'service': int,'subservice': int,'authorization_status': str,'licensee': str, 'operational_status': str,
              'horizontal_power': float,'vertical_power': float}
    fulldatabase = pd.read_csv(fname, usecols=columns, names=fieldnames, dtype=dtypes, header=None, na_values=['-'])
    txs = fulldatabase.loc[fulldatabase.station_function == 'TX'].copy()

    if not radians:
        # Change latitude and longitude from degrees to radians
        txs.loc[:,'latitude'] = np.radians(txs.loc[:,'latitude'])
        txs.loc[:,'longitude'] = np.radians(txs.loc[:,'longitude'])
    if not allow_duplicates:
        # Remove any duplicated entries
        n1 = len(txs)
        txs.drop_duplicates(keep='first', inplace=True)
        n2 = len(txs)
        print(f'{n1-n2} duplicated transmitters were found and removed')
    if not allow_nonoperational:
        # Remove non-operational transmitters (including auxiliary transmitters and those under consideration)
        n1 = len(txs)
        bad_operational_status = ('AX','AXO','AXP','UX','PUC','UC')
        txs = txs[~txs.operational_status.isin(bad_operational_status)]
        n2 = len(txs)
        print(f'{n1-n2} non-operational transmitters were removed (including auxiliary transmitters and those under consideration)')
    if not allow_unauthorized:
        # Remove transmitters with cancelled or "not granted" authorization status
        n1 = len(txs)
        bad_authorization_status = ('-4','-2','NG')
        txs = txs[~txs.authorization_status.isin(bad_authorization_status)]
        n2 = len(txs)
        print(f'{n1-n2} unauthorized transmitters were removed')

    return txs

if __name__ == '__main__':
    """
    Example usage:  python prepare_txdb.py -b "-72.26 -65.07 49.13 53.63" -f1 20 -f2 200 -w
    """
    parser = ArgumentParser(description='Prepare transmitter database from Government of Canada\'s Spectrum Management System. Downloads the database from http://www.ic.gc.ca/engineering/SMS_TAFL_Files/TAFL_LTAF.zip. Saves the database as csv.')
    parser.add_argument('-b', '--bounds', type=str, nargs=1, default=["-180 180 -90 90"], help='Set latitude, longitude of outer bounds for inclusion of transmitters (space-delimited: "W E S N")')
    parser.add_argument('-f1', '--frequency_low', type=float, default=0, help='Set lower frequency bound (MHz) for transmitter inclusion in database.')
    parser.add_argument('-f2', '--frequency_high', type=float, default=20e3, help='Set upper frequency bound (MHz) for transmitter inclusion in database.')
    parser.add_argument('-s', '--savename', type=str, default='txdb.csv', help='Filename to save transmitter database. Must be .csv (default: txdb.csv)')
    data_src = parser.add_mutually_exclusive_group()
    data_src.add_argument('-w', '--web', action='store_true', help='Download transmitter database from web')
    data_src.add_argument('-c', '--cache', action='store_true', help='Use cached transmitter database')
    args = parser.parse_args()

    # Parse and check values of bounds
    bounds = args.bounds[0].split(" ")
    W = float(bounds[0])
    E = float(bounds[1])
    S = float(bounds[2])
    N = float(bounds[3])
    if E <= W:
        raise ValueError('bounds: East bound should be greater than West bound')
    if N <= S:
        raise ValueError('bounds: North bound should be greater than South bound')
    txdb_bounds_rad = np.radians(((S, W), (N, E)))

    # Download transmitter database to cache
    if args.web:
        print('Getting transmitter database from the web...')
        dest = rasp.fetch.download(URL, rasp.CACHE_DIR)
        contents = rasp.fetch.unzip(dest)[0]
        # Import and munge transmitter database
        print('Munging transmitter database...')
        txs = import_TAFL(contents)
    else:
        # Retrieve transmitter database from cache
        print('Getting transmitter database from cache...')
        if CSV.exists():
            print('Munging transmitter database...')
            txs = import_TAFL(CSV)
        else:
            raise FileNotFoundError(f'{CSV} does not exist!')

    # Only keep transmitters within latitude, longitude bounds and within given frequency band
    print(f'Looking for transmitters between {args.frequency_low}-{args.frequency_high} MHz and inside latitude / longitude: {S}-{N}° / {W}-{E}°')
    txdb = rasp.TxDB(txs).in_bounds(txdb_bounds_rad).in_band(args.frequency_low, args.frequency_high)
    print(f'Found {len(txdb)} transmitters!')
    print(f'Saving transmitter database as {args.savename}')
    extra_utils.save_txdb(txdb, args.savename)
    print('Transmitter database saved')

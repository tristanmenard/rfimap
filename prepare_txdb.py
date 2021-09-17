import numpy as np
import pandas as pd
import rasp
from argparse import ArgumentParser

if __name__ == '__main__':
    """
    Example usage:  python prepare_txdb.py "-72.26 -65.07 49.13 53.63" -f1 20 -f2 200 -w
    """
    parser = ArgumentParser(description='Prepare transmitter database from ISED\'s Spectrum Management System. Downloads the database from http://www.ic.gc.ca/engineering/SMS_TAFL_Files/TAFL_LTAF.zip. Saves the database as csv.')
    parser.add_argument('bounds', type=str, nargs=1, help='Set latitude, longitude of outer bounds for inclusion of transmitters (space-delimited: "W E S N")')
    parser.add_argument('-f1', '--frequency_low', type=float, default=0, help='Set lower frequency bound (MHz) for transmitter inclusion in database.')
    parser.add_argument('-f2', '--frequency_high', type=float, default=20e3, help='Set upper frequency bound (MHz) for transmitter inclusion in database.')
    parser.add_argument('-s', '--savename', type=str, default='txdb.csv', help='Filename to save transmitter database. Must be .csv (default: txdb.csv)')
    data_src = parser.add_mutually_exclusive_group()
    data_src.add_argument('-w', '--web', action='store_true', help='Download transmitter database from web')
    data_src.add_argument('-c', '--cache', action='store_true', help='Use cached transmitter database')
    args = parser.parse_args()

    # Parse bound values
    bounds = args.bounds[0].split(" ")
    W = float(bounds[0])
    E = float(bounds[1])
    S = float(bounds[2])
    N = float(bounds[3])
    bounds_rad = np.radians(((S, W), (N, E)))

    # Download transmitter database to cache
    if args.web:
        print('Getting transmitter database from the web...')
        txdb = rasp.TxDB.from_web()
    else:
        # Retrieve transmitter database from cache
        print('Getting transmitter database from cache...')
        txdb = rasp.TxDB.from_cache()

    # Only keep transmitters within latitude, longitude bounds and within given frequency band
    print(f'Looking for transmitters between {args.frequency_low}-{args.frequency_high} MHz and inside latitude / longitude: {S}-{N} deg / {W}-{E} deg')
    txs = txdb.in_bounds(bounds_rad).in_band(args.frequency_low, args.frequency_high)
    print(f'Found {len(txdb)} transmitters!')
    print(f'Saving transmitter database as {args.savename}')
    rasp.data.file.save_txdb(txdb, args.savename)
    print('Transmitter database saved')

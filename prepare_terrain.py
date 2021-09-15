import numpy as np
import matplotlib.pyplot as plt
import rasp
from argparse import ArgumentParser

if __name__ == "__main__":
    """
    Example usage:  python prepare_terrain.py "-72.26 -65.07 49.13 53.63" "-70.10 -67.23 50.48 52.28" -w
    """
    parser = ArgumentParser(description='Prepare terrain elevation data for propagation mapping. Saves the elevation data object as .pickle')
    parser.add_argument('bounds', type=str, nargs=1, help='Set latitude, longitude of outer bounds for terrain elevation data (space-delimited: "W E S N")')
    parser.add_argument('roi_bounds', type=str, nargs=1, help='Set latitude, longitude of region of interest for signal propagation map (space-delimited: "W E S N")')
    parser.add_argument('-s', '--savename', type=str, default='elevation_dict.pickle', help='Filename to save elevation data object. Must be .pickle (default: elevation_dict.pickle)')
    parser.add_argument('-p', '--plot', action='store_true', help='Plot elevation data on map')
    data_src = parser.add_mutually_exclusive_group()
    data_src.add_argument('-w', '--web', action='store_true', help='Download SRTM elevation data from the web')
    data_src.add_argument('-c', '--cache', action='store_true', help='Use cached SRTM elevation data')
    args = parser.parse_args()

    # Parse and check values of bounds
    bounds = args.bounds[0].split(" ")
    W = float(bounds[0])
    E = float(bounds[1])
    S = float(bounds[2])
    N = float(bounds[3])
    bounds_rad = np.radians(((S, W), (N, E)))

    roi_bounds = args.roi_bounds[0].split(" ")
    W_roi = float(roi_bounds[0])
    E_roi = float(roi_bounds[1])
    S_roi = float(roi_bounds[2])
    N_roi = float(roi_bounds[3])
    roi_bounds_rad = np.radians(((S_roi, W_roi), (N_roi, E_roi)))

    # Load SRTM3 terrain elevation data from web or cache
    if args.web:
        print('Getting terrain elevation data from web...')
        elevation = rasp.Elevation.from_web(bounds=bounds_rad)
        elevation.set_region_of_interest(bounds=roi_bounds_rad)
    else:
        print('Getting terrain elevation data from cache...')
        elevation = rasp.Elevation.from_cache(bounds=bounds_rad)
        elevation.set_region_of_interest(bounds=roi_bounds_rad)

    # Save terrain elevation data as .pickle
    print(f'Saving terrain elevation data to {args.savename} ...')
    rasp.data.file.save_elevation(elevation, args.savename)
    print('Terrain elevation data saved')

    # Plot elevation map
    if args.plot:
        plt.figure(figsize=(10,8))
        plt.imshow(elevation.dem, origin='lower', extent=[W, E, S, N], aspect=elevation.dem.shape[1]/elevation.dem.shape[0], cmap='gist_ncar')
        plt.grid(color='k', linestyle='--', alpha=0.8)
        plt.colorbar()
        plt.show()

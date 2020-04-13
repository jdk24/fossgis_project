#!/usr/bin/env python

from __future__ import print_function

from os import path

import os
import grass.script as g_script


def init():
    # setup folder names
    os.chdir("../.")
    global base_directory, data_folder, remove_outlier
    base_directory = os.getcwd()
    data_folder = base_directory + '/data/'

    # whether to remove stations with always high average values see img folder 0h, 6h, 12h and 18h
    remove_outlier = True


def import_data():
    files_to_import = {
        data_folder: ['stuttgart_districts', 'stuttgart'],
        data_folder + 'pm10/': ['lubw', 'luftdaten'],
        data_folder + 'pm25/': ['avg_{0:0=2d}_hrs'.format(x) for x in range(0, 24)]
    }

    layer_list = g_script.read_command(
        'g.list',
        type='vector,raster'
    ).split()

    print("Importing data. Please make sure the following files exist in these folders:")
    for path_name, names in files_to_import.items():
        print(
            "{}: {}".format(
                path_name,
                ','.join(['{}.geojson'.format(x) for x in names])
            )
        )
    print("")

    # switch to PERMANENT mapset
    g_script.run_command('g.mapset', mapset='PERMANENT')

    # import all files
    for path_name, names in files_to_import.items():
        for name in names:
            # import only if not imported
            if name not in layer_list:
                g_script.run_command(
                    'v.import',
                    input=path_name + name + '.geojson',
                    output=name,
                    overwrite=True
                )

                if remove_outlier and name.startswith('avg'):
                    g_script.run_command(
                        'v.edit',
                        map=name,
                        type='point',
                        tool='delete',
                        where="station_id IN(1106,3993,23955,6608)"
                    )

    # set extent by districts
    print("\nSetting region and extent to Stuttgart with resolution of 10x10 m\n")
    g_script.run_command(
        'g.region',
        vector='stuttgart_districts@PERMANENT',
        res=10,
        flags='s'
    )

    # check region
    g_script.run_command('g.region', flags='p')

    # list layers
    print('\nAvailable Layers:')
    g_script.run_command('g.list', type='vector')


def write_config_files():
    """
    Writes the config files according to the EAQI according to https://airindex.eea.europa.eu/#
    to the folder data/config if they do not exist.
    All of these represent hourly value limits.
    """
    if not path.isdir(data_folder + "config"):
        print("\nCreating config directory and files ...\n")
        config_folder = data_folder + 'config/'
        os.mkdir(config_folder)
        os.chdir(config_folder)

        # pm_25 categories
        os.popen('echo "0 thru 10 = 1   Good\n'
                 '10 thru 20 = 2   Fair\n'
                 '20 thru 25 = 3   Moderate\n'
                 '25 thru 50 = 4   Poor\n'
                 '50 thru 75 = 5   Very poor\n'
                 '75 thru 800 = 6   Extremely poor\n'
                 '* = 7   None" > pm25.txt')

        # pm_10 categories
        os.popen('echo "0 thru 20 = 1   Good\n'
                 '20 thru 40 = 2   Fair\n'
                 '40 thru 50 = 3   Moderate\n'
                 '50 thru 100 = 4   Poor\n'
                 '100 thru 150 = 5   Very poor\n'
                 '150 thru 1200 = 6   Extremely poor\n'
                 '* = 7   None" > pm10.txt')

        # NO2 categories
        os.popen('echo "0 thru 40 = 1   Good\n'
                 '40 thru 90 = 2   Fair\n'
                 '90 thru 120 = 3   Moderate\n'
                 '120 thru 230 = 4   Poor\n'
                 '230 thru 340 = 5   Very poor\n'
                 '340 thru 1000 = 6   Extremely poor\n'
                 '* = 7   None" > NO2.txt')

        # O3 categories
        os.popen('echo "0 thru 50 = 1   Good\n'
                 '50 thru 100 = 2   Fair\n'
                 '100 thru 130 = 3   Moderate\n'
                 '130 thru 240 = 4   Poor\n'
                 '240 thru 380 = 5   Very poor\n'
                 '380 thru 800 = 6   Extremely poor\n'
                 '* = 7   None" > O3.txt')

        # SO2 categories
        os.popen('echo "0 thru 100 = 1   Good\n'
                 '100 thru 200 = 2   Fair\n'
                 '200 thru 350 = 3   Moderate\n'
                 '350 thru 500 = 4   Poor\n'
                 '500 thru 750 = 5   Very poor\n'
                 '750 thru 1250 = 6   Extremely poor\n'
                 '* = 7   None" > SO2.txt')

        os.popen('echo "1 0:244:224\n'
                 '2 0:200:151\n'
                 '3 236:229:0\n'
                 '4 255:27:55\n'
                 '5 144:0:36\n'
                 '6 113:0:112\n'
                 '7 255:255:255" > eaqi_colors.txt')

        print("created:\n"
              "data/\n"
              "  config/\n"
              "    eaqi_colors.txt\n"
              "    NO2.txt\n"
              "    O3.txt\n"
              "    pm10.txt\n"
              "    pm25.txt\n"
              "    SO2.txt\n"
              )

        # return to project folder
        os.chdir('../..')
    else:
        print("\nConfig files already existing.")


if __name__ == '__main__':
    init()
    import_data()
    write_config_files()
    print('\nFinished setup.')

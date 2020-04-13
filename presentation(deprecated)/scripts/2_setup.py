#!/usr/bin/env python

from os import path

import os
import grass.script as g_script


def init():
    # setup folder names
    os.chdir("../.")
    global base_directory, data_folder
    base_directory = os.getcwd()
    data_folder = base_directory + '/data/'


def import_data():
    file_names = [
        # "stuttgart",
        "stuttgart_districts",
        "lubw",
        "luftdaten"
    ]

    layer_list = g_script.read_command(
        'g.list',
        type='vector,raster'
    ).split()

    print("Importing data. Please make sure the following files exist in the data folder:")
    for name in file_names:
        print("{}.geojson".format(name))
    print("")

    # switch to PERMANENT mapset
    g_script.run_command('g.mapset', mapset='PERMANENT')

    # import all files
    for name in file_names:
        # import only if not imported
        if name not in layer_list:
            g_script.run_command(
                'v.import',
                input=data_folder + name + '.geojson',
                output=name,
                overwrite=True
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
    Writes the config files according to the CAQI according to http://www.airqualitynow.eu/about_indices_definition.php
    to the folder data/config if they do not exist.
    """
    if not path.isdir(data_folder + "config"):
        print("Creating config directory and files ...")
        config_folder = data_folder + 'config/'
        os.mkdir(config_folder)
        os.chdir(config_folder)

        # TODO do we need null/error values in the categories ?

        # MANDATORY CATEGORIES

        # generate pm_10 hourly categories
        os.popen('echo "0 thru 25 = 1   Very Low\n'
                 '25 thru 50 = 2   Low\n'
                 '50 thru 90 = 3   Medium\n'
                 '90 thru 180 = 4   High\n'
                 '* = 5   Very High" > pm_10_hourly.txt')

        # generate pm_10 daily categories
        os.popen('echo "0 thru 15 = 1   Very Low\n'
                 '15 thru 30 = 2   Low\n'
                 '30 thru 50 = 3   Medium\n'
                 '50 thru 100 = 4   High\n'
                 '* = 5   Very High" > pm_10_daily.txt')

        # generate NO2 categories
        os.popen('echo "0 thru 50 = 1   Very Low\n'
                 '50 thru 100 = 2   Low\n'
                 '100 thru 200 = 3   Medium\n'
                 '200 thru 400 = 4   High\n'
                 '* = 5   Very High" > NO2.txt')

        # generate O3 categories
        os.popen('echo "0 thru 60 = 1   Very Low\n'
                 '60 thru 120 = 2   Low\n'
                 '120 thru 180 = 3   Medium\n'
                 '180 thru 240 = 4   High\n'
                 '* = 5   Very High" > O3.txt')

        # AUXILIARY CATEGORIES

        # generate pm_2_5 hourly categories
        os.popen('echo "0 thru 15 = 1   Very Low\n'
                 '15 thru 30 = 2   Low\n'
                 '30 thru 55 = 3   Medium\n'
                 '55 thru 110 = 4   High\n'
                 '* = 5   Very High" > pm_2_5_hourly.txt')

        # generate pm_2_5 daily categories
        os.popen('echo "0 thru 10 = 1   Very Low\n'
                 '10 thru 20 = 2   Low\n'
                 '20 thru 30 = 3   Medium\n'
                 '30 thru 60 = 4   High\n'
                 '* = 5   Very High" > pm_2_5_daily.txt')

        # generate CO daily categories
        os.popen('echo "0 thru 5000 = 1   Very Low\n'
                 '5000 thru 7500 = 2   Low\n'
                 '7500 thru 10000 = 3   Medium\n'
                 '10000 thru 20000 = 4   High\n'
                 '* = 5   Very High" > CO.txt')

        # generate SO2 daily categories
        os.popen('echo "0 thru 50 = 1   Very Low\n'
                 '50 thru 100 = 2   Low\n'
                 '100 thru 350 = 3   Medium\n'
                 '350 thru 500 = 4   High\n'
                 '* = 5   Very High" > SO2.txt')

        os.popen('echo "1 100:171:84\m'
                 '2 173:200:60'
                 '3 232:183:15'
                 '4 236:128:11'
                 '5 130:0:19" > caqi_colors.txt')

        print("created:\n"
              "data/\n"
              "  config/\n"
              "    caqi_colors.txt\n"
              "    CO.txt\n"
              "    NO2.txt\n"
              "    O3.txt\n"
              "    pm_10_daily.txt\n"
              "    pm_10_hourly.txt\n"
              "    pm_2_5_daily.txt\n"
              "    pm_2_5_hourly.txt\n"
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

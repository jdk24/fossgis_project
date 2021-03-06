#!/usr/bin/env python

import os
import grass.script as g_script


def init():
    # setup folder names
    os.chdir("../.")
    global base_directory, data_folder, config_folder
    base_directory = os.getcwd()
    data_folder = base_directory + '/data/'
    config_folder = data_folder + 'config/'


def switch_mapset():

    global user
    # set user from current mapset
    user = g_script.read_command(
        'g.mapset',
        flags='p'
    ).rstrip()

    # list mapsets
    user_list = g_script.read_command(
        'g.mapset',
        flags='l'
    ).split()
    user_list = [x for x in user_list if x != u'PERMANENT']

    if not user_list:
        answer = raw_input('You currently have no user mapset. If you don\'t create a user mapset the PERMANENT '
                           'mapset will be used. Do you want to create a user mapset?(Y/n)')
        if answer != 'n':
            user = raw_input('Name the mapset:').rstrip()
            g_script.run_command(
                'g.mapset',
                mapset=user,
                flags='c',
            )
            g_script.run_command(
                'g.region',
                flags='d'
            )
        else:
            user = 'PERMANENT'
    else:
        while unicode(user) not in user_list:
            user = raw_input('Choose a user to switch to: {}'.format(user_list)).rstrip()
    # switch mapset
    g_script.run_command(
        'g.mapset',
        mapset=user
    )
    print('Switched to {}'.format(user))


def interpolate(skip):
    global user

    if not skip:
        # idw interpolation pm10
        g_script.run_command(
            'v.surf.idw',
            input='luftdaten@PERMANENT',
            column='p10',
            output='idw_p10',
            overwrite=True
        )

        # bspline interpolation
        g_script.run_command(
            'v.surf.bspline',
            input='luftdaten@PERMANENT',
            column='p10',
            raster_output='bspline_p10',
            ns_step=50,
            ew_step=50,
            overwrite=True
        )

        # rst interpolation
        g_script.run_command(
            'v.surf.rst',
            input='luftdaten@PERMANENT',
            zcolumn='p10',
            elevation='rst_p10',
            segmax=10,
            npmin=50,
            overwrite=True
        )

        # reclassify to CAQI categories
        for name in [
            'idw',
            'bspline',
            'rst'
        ]:

            g_script.run_command(
                'r.reclass',
                input='{}_p10'.format(name),
                output='{}_p10_caqi_hourly'.format(name),
                rules=config_folder + 'pm_10_hourly.txt',
                overwrite=True
            )

            # convert raster to vector
            g_script.run_command(
                'r.to.vect',
                input='{}_p10_caqi_hourly'.format(name),
                output='{}_p10_caqi_hourly_vec'.format(name),
                type='area',
                overwrite=True
            )

            # generalize polygons
            g_script.run_command(
                'v.generalize',
                input='{}_p10_caqi_hourly_vec'.format(name),
                output='{}_p10_caqi_hourly_vec_simple'.format(name),
                method='douglas',
                threshold=20,
                type='area',
                overwrite=True
            )

            # save to geojson
            g_script.run_command(
                'v.out.ogr',
                input='{}_p10_caqi_hourly_vec_simple'.format(name),
                output='{}{}_p10.geojson'.format(data_folder, name),
                format='GeoJSON',
                output_type='boundary',
                overwrite=True
            )

            # reproject geojson
            os.popen('ogr2ogr -overwrite {0}{1}_p10_4326.geojson -s_srs "EPSG:25832" '
                     '-t_srs "EPSG:4326" {0}{1}_p10.geojson'.format(data_folder, name))


if __name__ == '__main__':
    init()
    # To hardcode the mapset uncomment this command and comment switch_mapset()
    #
    #     g_script.run_command(
    #         'g.mapset',
    #         mapset=username
    #     )
    switch_mapset()
    skip_processing = False
    interpolate(skip_processing)

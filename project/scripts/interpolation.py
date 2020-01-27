#!/usr/bin/env python

import os
import grass.script as g_script


def init():
    # setup folder names
    os.chdir("../.")
    global base_directory, config_folder
    base_directory = os.getcwd()
    config_folder = base_directory + '/data/config/'


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
        answer = raw_input('You currently have no user mapset. If you don\'t create a user mapset the PERMANENT mapset will'
                       'be used. Do you want to create a user mapset?(Y/n)')
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

        # idw interpolation pm2.5
        # if not skip:
        #     g_script.run_command(
        #         'v.surf.',
        #         input='luftdaten@PERMANENT',
        #         column='p25',
        #         output='idw_p25',
        #         overwrite=True
        #     )

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

#         TODO
#         used commands to get vector from interpolated raster
#         r.to.vect

#         v.out.ogr
# /Applications/QGIS3.8.app/Contents/MacOS/bin/ogr2ogr rst_poly_reprojected.geojson -s_srs "EPSG:25832" -t_srs "EPSG:4326" rst_polys.geojson

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

#!/usr/bin/env python

import os
import grass.script as g_script


def init():
    # setup folder names
    os.chdir("../.")
    global base_directory, data_folder, config_folder, keep_intermediates, run_quiet
    base_directory = os.getcwd()
    data_folder = base_directory + '/data/'
    config_folder = data_folder + 'config/'
    keep_intermediates = False
    run_quiet = False


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


def interpolate(layer, i_method, column_name, pollutant_config):
    """
    Interpolates an existing vector point layer using either inverse distance weighting,
    bi-linear splines or regularized splines with tension. The column name of the values that should be interpolated
    needs to be passed as well as the category config for the pollutant that is interpolated e.g. 'pm25'.
    The config files can be found in the data/config folder.
    :param layer: str - existing vector point layer with values to interpolate
    :param i_method: str - interpolation method: idw, bspline or rst
    :param column_name: str - name of the value column in the input layer
    :param pollutant_config: str - name of the config in data/config folder to use for reclassification
    """
    if i_method not in ['idw', 'bspline', 'rst']:
        print('Invalid interpolation method. Choose one of "idw", "bspline" and "rst".')
    else:
        temp_name = '{}_{}_{}'.format(layer, pollutant_config, i_method)
        # idw interpolation
        if i_method == 'idw':
            g_script.run_command(
                'v.surf.idw',
                input='{}@PERMANENT'.format(layer),
                column=column_name,
                output=temp_name,
                overwrite=True,
                quiet=True if run_quiet else False
            )

        # bspline interpolation
        elif i_method == 'bspline':
            g_script.run_command(
                'v.surf.bspline',
                input='{}@PERMANENT'.format(layer),
                column=column_name,
                raster_output=temp_name,
                ns_step=50,
                ew_step=50,
                overwrite=True,
                quiet=True if run_quiet else False
            )

        # rst interpolation
        elif i_method == 'rst':
            g_script.run_command(
                'v.surf.rst',
                input='{}@PERMANENT'.format(layer),
                zcolumn=column_name,
                elevation=temp_name,
                segmax=10,
                npmin=50,
                smooth=0.1,
                tension=100,
                overwrite=True,
                quiet=True if run_quiet else False
            )

        # reclassify to EAQI categories
        g_script.run_command(
            'r.reclass',
            input=temp_name,
            output='{}_eaqi'.format(temp_name),
            rules=config_folder + '{}.txt'.format(pollutant_config),
            overwrite=True,
            quiet=True if run_quiet else False
        )

        # convert raster to vector
        g_script.run_command(
            'r.to.vect',
            input='{}_eaqi'.format(temp_name),
            output='{}_eaqi_vec'.format(temp_name),
            type='area',
            overwrite=True,
            quiet=True if run_quiet else False
        )

        # generalize polygons
        g_script.run_command(
            'v.generalize',
            input='{}_eaqi_vec'.format(temp_name),
            output='{}'.format(temp_name),
            method='douglas',
            threshold=20,
            type='area',
            overwrite=True,
            quiet=True if run_quiet else False
        )

        # remove Good and None category values to reduce geojson size
        g_script.run_command(
            'v.edit',
            map='{}'.format(temp_name),
            tool='delete',
            where="value IN(1,7)",
            overwrite=True,
            quiet=True if run_quiet else False
        )

        # save to geojson
        g_script.run_command(
            'v.out.ogr',
            input='{}'.format(temp_name),
            output='{}{}_temp.geojson'.format(data_folder, temp_name),
            format='GeoJSON',
            output_type='boundary',
            overwrite=True,
            quiet=True if run_quiet else False
        )

        # remove existing geojson as ogr2ogr can't overwrite file names directly ???
        if os.path.exists('{}{}.geojson'.format(data_folder, temp_name)):
            os.popen('rm {}{}.geojson'.format(data_folder, temp_name))

        # reproject geojson
        os.popen('ogr2ogr {0}{1}.geojson -s_srs "EPSG:25832" '
                 '-t_srs "EPSG:4326" {0}{1}_temp.geojson'.format(data_folder, temp_name))
        if not keep_intermediates:
            os.popen('rm {}{}_temp.geojson'.format(data_folder, temp_name))
            os.popen('g.remove type=vector name={}_eaqi_vec -f'.format(temp_name))


if __name__ == '__main__':
    init()

    # To hard-code the mapset uncomment this command and comment switch_mapset()
    #
    #     g_script.run_command(
    #         'g.mapset',
    #         mapset=username
    #     )
    switch_mapset()

    # interpolate average values for each hour of the day using rst
    for name in ['avg_{0:0=2d}_hrs'.format(x) for x in range(0, 24)]:
        interpolate(name, 'rst', 'avg_pm25', 'pm25')

    # interpolate 12:00 with idw and bsplines as well
    interpolate('avg_12_hrs', 'idw', 'avg_pm25', 'pm25')
    interpolate('avg_12_hrs', 'bspline', 'avg_pm25', 'pm25')

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


def interpolate(layer, step, lambda_i, out_folder):
    """
    Interpolates an existing vector point layer using either inverse distance weighting,
    bi-linear splines or regularized splines with tension. The column name of the values that should be interpolated
    needs to be passed as well as the category config for the pollutant that is interpolated e.g. 'pm25'.
    The config files can be found in the data/config folder.
    :param layer: str - existing vector point layer with values to interpolate
    :param value1: str - value to test interpolation methods with
    :param column_name: str - name of the value column in the input layer
    :param pollutant_config: str - name of the config in data/config folder to use for reclassification
    """
    temp_name = '{}_{}_{}'.format(layer, step, lambda_i)
    out_folder += '/'

    g_script.run_command(
        'v.surf.bspline',
        input='{}@PERMANENT'.format(layer),
        column='avg_pm25',
        raster_output=temp_name,
        ns_step=step,
        ew_step=step,
        solver='cholesky',
        method='bilinear',
        lambda_i= lambda_i
        overwrite=True,
        quiet=True if run_quiet else False
    )

    if not os.path.isdir(data_folder + out_folder):
        os.mkdir(data_folder + out_folder)

    g_script.run_command(
        'r.out.gdal',
        input=temp_name,
        output='{}{}/{}.png'.format(data_folder, out_folder, temp_name),
        format='PNG',
        type='Float64',
        overwrite=True
    )
    # bspline interpolation
    # elif i_method == 'bspline':

    #
    # # rst interpolation
    # elif i_method == 'rst':
    #     g_script.run_command(
    #         'v.surf.rst',
    #         input='{}@PERMANENT'.format(layer),
    #         zcolumn=column_name,
    #         elevation=temp_name,
    #         segmax=10,
    #         npmin=50,
    #         overwrite=True,
    #         quiet=True if run_quiet else False
    #     )

    # reclassify to EAQI categories
    g_script.run_command(
        'r.reclass',
        input=temp_name,
        output='{}_eaqi'.format(temp_name),
        rules=config_folder + '{}.txt'.format('pm25'),
        overwrite=True,
        quiet=True if run_quiet else False
    )

    if not os.path.isdir(data_folder + 'cat_' + out_folder):
        os.mkdir(data_folder + 'cat_' + out_folder)

    g_script.run_command(
        'r.out.gdal',
        input='{}_eaqi'.format(temp_name),
        output='{}cat_{}/{}.png'.format(data_folder, out_folder, temp_name),
        format='PNG',
        type='Float64',
        overwrite=True
    )


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
    for lambda_i in [0, 0.3, 1, 2, 4, 10, 30]:
        interpolate('avg_11_hrs', lambda_i, 12, 'power')

    # for step in [0, 3, 8, 12, 20, 60]:
    #     interpolate('avg_11_hrs', 2, npoints, 'npoints')

    # interpolate 12:00 with idw and bsplines as well
    # interpolate('avg_12_hrs', 'idw', 'avg_pm25', 'pm25')
    # interpolate('avg_12_hrs', 'bspline', 'avg_pm25', 'pm25')

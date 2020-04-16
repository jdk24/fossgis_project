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


def interpolate(layer, power, npoints, out_folder):
    """
    Interpolates an existing vector point layer using inverse distance weighting.
    :param layer: str - existing vector point layer with values to interpolate
    :param power: str - value for the power parameter
    :param npoints: str - value for the npoints parameter
    :param out_folder: str - sub folder in data to save the output to
    """
    temp_name = 'idw_{}_{}'.format(npoints, power)
    out_folder += '/'
    # idw interpolation
    g_script.run_command(
        'v.surf.idw',
        flags='n',
        input='{}@PERMANENT'.format(layer),
        column='avg_pm25',
        output=temp_name,
        power=power,
        overwrite=True,
        quiet=True if run_quiet else False
    )

    if keep_intermediates:
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
    switch_mapset()

    default_power = 2
    power_values = [0.3, 1, 2, 4, 10, 30]
    default_npoints = 12
    npoint_values = [0, 3, 8, 12, 20]

    # interpolate with different parameters
    for value in power_values:
        if not os.path.isfile(data_folder + 'cat_power/idw_{}_{}.png'.format(default_npoints, value)):
            interpolate('avg_11_hrs', value, default_npoints, 'power')

    for value in npoint_values:
        if not os.path.isfile(data_folder + 'cat_npoints/idw_{}_{}.png'.format(value, default_power)):
            interpolate('avg_11_hrs', default_power, value, 'npoints')

    # compare difference after categorization
    g_script.run_command(
        'r.mapcalc',
        expression='idw_power_diff = abs( idw_{0}_{1}_eaqi - idw_{0}_{2}_eaqi )'
            .format(default_npoints, power_values[0], power_values[-1]),
        overwrite=True
    )

    g_script.run_command(
        'r.report',
        map='idw_power_diff',
        units='p'
    )

    g_script.run_command(
        'r.mapcalc',
        expression='idw_npoints_diff = abs( idw_{1}_{0}_eaqi - idw_{2}_{0}_eaqi )'
            .format(default_power, npoint_values[0], npoint_values[-1]),
        overwrite=True
    )

    g_script.run_command(
        'r.report',
        map='idw_npoints_diff',
        units='p'
    )

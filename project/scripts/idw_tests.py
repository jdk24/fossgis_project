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
    temp_name = '{}_{}_{}'.format(layer, npoints, power)
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

    # To hard-code the mapset uncomment this command and comment switch_mapset()
    #
    #     g_script.run_command(
    #         'g.mapset',
    #         mapset=username
    #     )
    switch_mapset()

    # test different powers
    for power in [0, 0.3, 1, 2, 4, 10, 30]:
        interpolate('avg_11_hrs', power, 12, 'power')

    # test different npoints
    for npoints in [0, 3, 8, 12, 20, 60]:
        interpolate('avg_11_hrs', 2, npoints, 'npoints')



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


def interpolate(layer, tension, smoothing, out_folder):
    """
    Interpolates an existing vector point layer using regularized splines with tension.
    :param layer: str - existing vector point layer with values to interpolate
    :param tension: str - value to test interpolation methods with
    :param smoothing: str - name of the value column in the input layer
    :param out_folder: str - name of the config in data/config folder to use for reclassification
    """
    temp_name = 'rst_{}_{}'.format(tension, smoothing)
    out_folder += '/'
    # idw interpolation
    g_script.run_command(
        'v.surf.rst',
        input='{}@PERMANENT'.format(layer),
        zcolumn='avg_pm25',
        elevation=temp_name,
        segmax=10,
        npmin=50,
        tension=tension,
        smooth=smoothing,
        overwrite=True,
        quiet=True if run_quiet else False
    )

    if keep_intermediates:
        if not os.path.isdir(data_folder + out_folder):
            os.mkdir(data_folder + out_folder)

        g_script.run_command(
            'r.out.gdal',
            input=temp_name,
            output='{}{}{}.png'.format(data_folder, out_folder, temp_name),
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
        output='{}cat_{}{}.png'.format(data_folder, out_folder, temp_name),
        format='PNG',
        type='Float64',
        overwrite=True
    )


if __name__ == '__main__':
    init()
    switch_mapset()

    default_tension = 100
    t_values = [10, 20, 40, 100]
    default_smoothing = 0.5
    s_values = [0.05, 0.1, 0.5, 0.75, 1, 3, 10]

    # interpolate with different parameters
    for value in t_values:
        if not os.path.isfile(data_folder + 'cat_tension/rst_{}_{}.png'.format(value, default_smoothing)):
            interpolate('avg_11_hrs', value, default_smoothing, 'tension')

    for value in s_values:
        if not os.path.isfile(data_folder + 'cat_smoothing/rst_{}_{}.png'.format(default_tension, value)):
            interpolate('avg_11_hrs', default_tension, value, 'smoothing')

    # compare difference after categorization
    g_script.run_command(
        'r.mapcalc',
        expression='rst_tension_diff = abs( rst_{1}_{0}_eaqi - rst_{2}_{0}_eaqi )'
            .format(default_smoothing, t_values[0], t_values[-1]),
        overwrite=True
    )

    g_script.run_command(
        'r.report',
        map='rst_tension_diff',
        units='p'
    )

    g_script.run_command(
        'r.mapcalc',
        expression='rst_smoothing_diff = abs( rst_{0}_{1}_eaqi - rst_{0}_{2}_eaqi )'
            .format(default_tension, s_values[0], s_values[-1]),
        overwrite=True
    )

    g_script.run_command(
        'r.report',
        map='rst_smoothing_diff',
        units='p'
    )

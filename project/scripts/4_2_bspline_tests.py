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
    Interpolates an existing vector point layer using bi-linear splines.
    The step and lambda_i values can be adjusted. The step refers to both the north-south and the east-west step,
    creating square sub regions.
    :param layer: str - existing vector point layer with values to interpolate
    :param step: str - value for the ew_step and ns_step parameters
    :param lambda_i: str - value for the lambda_i paramter
    :param out_folder: str - name of the output folder
    """
    temp_name = 'bspline_{}_{}'.format(step, lambda_i)
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
        lambda_i=lambda_i,
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

    # set default values
    default_lambda = 0.01
    l_values = [0.001, 0.006, 0.01, 0.06, 0.1]
    default_step = 50  # adjust to your point density
    step_values = [50, 75, 100, 150, 200]  # values below 50 result in too many areas with no data

    # interpolate with different parameters
    for value in l_values:
        if not os.path.isfile(data_folder + 'cat_lambda_i/bspline_{}_{}.png'.format(default_step, value)):
            interpolate('avg_11_hrs', default_step, value, 'lambda_i')

    for value in step_values:
        if not os.path.isfile(data_folder + 'cat_step/bspline_{}_{}.png'.format(value, default_lambda)):
            interpolate('avg_11_hrs', value, default_lambda, 'step')

    # compare difference after categorization
    g_script.run_command(
        'r.mapcalc',
        expression='bspline_lambda_diff = abs( bspline_{0}_{1}_eaqi - bspline_{0}_{2}_eaqi )'
            .format(default_step, l_values[0], l_values[-1]),
        overwrite=True
    )

    g_script.run_command(
        'r.report',
        map='bspline_lambda_diff',
        units='p'
    )

    g_script.run_command(
        'r.mapcalc',
        expression='bspline_step_diff = abs( bspline_{1}_{0}_eaqi - bspline_{2}_{0}_eaqi )'
            .format(default_lambda, step_values[0], step_values[-1]),
        overwrite=True
    )

    g_script.run_command(
        'r.report',
        map='bspline_step_diff',
        units='p'
    )

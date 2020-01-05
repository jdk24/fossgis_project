#!/usr/bin/env python

import os
import grass.script as g_script


def import_data():
    # switch to PERMANENT mapset
    g_script.run_command('g.mapset', mapset='PERMANENT')
    # check region
    g_script.run_command('g.region', flags='p')

    # setup folder names
    os.chdir("../.")
    base_directory = os.getcwd()
    print(base_directory)
    data_folder = base_directory + '/data/'

    # import land cover, reprojected internally
    # g_script.run_command(
    #     'r.import',
    #     input=data_folder + '/corine_landcover_2018/CLC2018_tarragona.tif',
    #     output='corine_landcover.tif',
    #     overwrite=True
    # )

    # dem_folder = data_folder + '/dem'
    # for dem_file in os.listdir(dem_folder):
    #     if dem_file.endswith('.zip'):
    #         with zipfile.ZipFile("{}/{}".format(dem_folder, dem_file), 'r') as zip_ref:
    #             zip_ref.extractall(dem_folder)

    # mosaic and reproject the srtm data
    # os.popen('gdalwarp -overwrite -t_srs "EPSG:32631" {0}/*.hgt {0}/srtm_mosaik.tif'.format(dem_folder))

    # import it
    # g_script.run_command('r.in.gdal', input=dem_folder+'/srtm_mosaik.tif', output='srtm_mosaik')

    # import Stuttgart
    # g_script.run_command(
    #     'v.import',
    #     input=data_folder + 'stuttgart.geojson',
    #     output='stuttgart',
    #     overwrite=True
    # )

    # import districts
    g_script.run_command(
        'v.import',
        input=data_folder + 'stuttgart_districts.geojson',
        output='stuttgart_districts',
        overwrite=True
    )

    # import lubw
    g_script.run_command(
        'v.import',
        input=data_folder + 'lubw.geojson',
        output='lubw',
        overwrite=True
    )

    # import luftdaten
    g_script.run_command(
        'v.import',
        input=data_folder + 'luftdaten.geojson',
        output='luftdaten',
        overwrite=True
    )

    # set extent
    g_script.run_command(
        'g.region',
        vector='stuttgart_districts@PERMANENT'
    )

    # idw interpolation
    g_script.run_command(
        'v.surf.idw',
        input='luftdaten@PERMANENT',
        column='p10',
        outpu='idw_p10'
    )

    # import buildings and fire_stations (tarragona_region already imported in step 1)
    # for file_name in ['buildings', 'fire_stations']:
    #     g_script.run_command(
    #         'v.import',
    #         input=data_folder + '/osm/{}.geojson'.format(file_name),
    #         output=file_name,
    #         overwrite=True
    #     )

    # list layers
    print('\nAvailable Layers:')
    g_script.run_command('g.list', type='vector,raster')


if __name__ == '__main__':
    import_data()

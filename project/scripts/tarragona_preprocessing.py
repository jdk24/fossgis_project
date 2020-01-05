#!/usr/bin/env python
import zipfile

import os

import grass.script as g_script

from grass.pygrass.modules.shortcuts import general as g, vector as v, raster as r

g_proj = g.proj
g_proj.flags.p = True
g_proj.run()



print(r_import.params_list)

def import_data():
    # switch to PERMANENT mapset
    g_script.run_command('g.mapset', mapset='PERMANENT')
    # check region just in case
    g_script.run_command('g.region', flags='p')

    # setup folder names
    base_directory = os.getcwd()
    data_folder = base_directory + '/assignment4_data'

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

    # import fire incidents
    # g_script.run_command(
    #     'v.import',
    #     input=data_folder + '/fire_incidents/fire_archive_V1_89293.shp',
    #     output='fire_incidents',
    #     overwrite=True
    # )

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

    # switch to tarragona mapset
    g_script.run_command('g.mapset', mapset='tarragona')
    g_script.run_command('g.region', vector='tarragona_region@PERMANENT', res=1000)

    # g_script.run_command(
    #     'r.slope.aspect',
    #     elevation='srtm_mosaik@PERMANENT',
    #     slope='slope',
    #     overwrite=True
    # )
    # generate slope class file
    # os.popen('echo "0 thru 5 = 1 hazard level 1\n'
    #          '6 thru 10 = 2 hazard level 2\n'
    #          '11 thru 15 = 3 hazard level 3\n'
    #          '16 thru 90 = 4 hazard level 4" > slope_classes.txt')

    # reclassify slope
    # g_script.run_command(
    #     'r.reclass',
    #     input='slope',
    #     output='temp_slope_class',
    #     rules='slope_classes.txt',
    #     overwrite=True
    # )

    # save reclassed file
    # g_script.run_command(
    #     'r.resample',
    #     input='temp_slope_class',
    #     output='slope_classed',
    #     overwrite=True
    # )

    # generate corine class file
    # os.popen('echo "212 213 221 222 241 331 = 2 hazard level 2\n'
    #          '211 223 231 242 244 = 3 hazard level 3\n'
    #          '243 311 312 313 321 322 323 324 332 333 334 = 4 hazard level 4\n'
    #          '* = 1 hazard level 1" > land_cover_classes.txt')

    # reclassify land_cover
    # g_script.run_command(
    #     'r.reclass',
    #     input='corine_landcover.tif',
    #     output='temp_land_cover_class',
    #     rules='land_cover_classes.txt',
    #     verbose=True,
    #     overwrite=True
    # )

    # save reclassed file
    # g_script.run_command(
    #     'r.resample',
    #     input='temp_land_cover_class',
    #     output='land_cover_classed',
    #     overwrite=True
    # )

    # create 1km grid
    # g_script.run_command(
    #     'v.mkgrid',
    #     map='fire_probability',
    #     box='1000,1000',
    #     overwrite=True
    # )

    # count fire incidents
    # g_script.run_command(
    #     'v.vect.stats',
    #     points='fire_incidents',
    #     areas='fire_probability',
    #     count_column='fire_count',
    #     overwrite=True
    # )

    # transform the vector grid to raster
    # g_script.run_command(
    #     'v.to.rast',
    #     input='fire_probability',
    #     output='fire_prob_rast',
    #     use='attr',
    #     attribute_column='fire_count',
    #     overwrite=True
    # )

    # calculate fire ignition probability
    # g_script.run_command(
    #     'r.mapcalc',
    #     expression='ignition = if( fire_prob_rast@tarragona > 15, 15, fire_prob_rast@tarragona ) * 100 / 15',
    #     overwrite=True
    # )

    # reclass 0 to 1 but keep others
    # os.popen('echo "0 = 1\n'
    #          '* = *" > reclass_zero.txt')

    # reclass with file
    # g_script.run_command(
    #     'r.reclass',
    #     input='ignition',
    #     output='ignition_reclass',
    #     rules='reclass_zero.txt',
    #     overwrite=True
    # )

    # generate ignition prob classes
    # os.popen('echo "0 thru 25 = 1\n'
    #          '25 thru 50 = 2\n'
    #          '50 thru 75 = 3\n'
    #          '75 thru 100 = 4" > ignition_classes.txt')

    # reclass ignition prob percentage to hazard value
    # g_script.run_command(
    #     'r.reclass',
    #     input='ignition_reclass',
    #     output='ignition_prob',
    #     rules='ignition_classes.txt',
    #     overwrite=True
    # )

    # create 1km grid
    # g_script.run_command(
    #     'v.mkgrid',
    #     map='building_density',
    #     box='1000,1000',
    #     overwrite=True
    # )

    # create building centroids
    # g_script.run_command(
    #     'v.extract',
    #     input='buildings@PERMANENT',
    #     output='centroids',
    #     type='centroid',
    #     overwrite=True
    # )

    # create add column for building count
    # g_script.run_command(
    #     'v.db.addcolumn',
    #     map='centroids',
    #     columns='count'
    # )

    # fill count column with 1
    # g_script.run_command(
    #     'v.db.update',
    #     map='centroids',
    #     column='count',
    #     value=1
    # )

    # count buildings
    # g_script.run_command(
    #     'v.vect.stats',
    #     points='centroids',
    #     areas='building_density',
    #     count_column='count',
    #     type='centroid',
    #     overwrite=True
    # )

    # transform the vector grid to raster
    # g_script.run_command(
    #     'v.to.rast',
    #     input='building_density',
    #     output='build_dens_rast',
    #     use='attr',
    #     attribute_column='count',
    #     overwrite=True
    # )

    # generate density categories
    # os.popen('echo "0 thru 10 = 1\n'
    #          '10 thru 50 = 2\n'
    #          '50 thru 250 = 3\n'
    #          '* = 4" > building_classes.txt')

    # reclass building density to exposure value
    # g_script.run_command(
    #     'r.reclass',
    #     input='build_dens_rast',
    #     output='exposure',
    #     rules='building_classes.txt',
    #     overwrite=True
    # )

    # create 1km grid
    # g_script.run_command(
    #     'v.mkgrid',
    #     map='vulnerability_grid',
    #     box='1000,1000',
    #     overwrite=True
    # )

    # create building centroids
    # g_script.run_command(
    #     'v.extract',
    #     input='fire_stations@PERMANENT',
    #     output='station_centroids',
    #     type='centroid',
    #     overwrite=True
    # )

    # create add column for building count
    # g_script.run_command(
    #     'v.db.addcolumn',
    #     map='station_centroids',
    #     columns='count'
    # )

    # fill count column with 1
    # g_script.run_command(
    #     'v.db.update',
    #     map='station_centroids',
    #     column='count',
    #     value=1
    # )

    # count buildings
    # g_script.run_command(
    #     'v.vect.stats',
    #     points='station_centroids',
    #     areas='vulnerability_grid',
    #     count_column='count',
    #     type='centroid',
    #     overwrite=True
    # )

    # transform the vector grid to raster
    # g_script.run_command(
    #     'v.to.rast',
    #     input='vulnerability_grid',
    #     output='vulnerability_rast',
    #     use='attr',
    #     attribute_column='count',
    #     overwrite=True
    # )

    # prepare for r.grow.distance
    os.popen('echo "1 thru 1000 = NULL\n'
             '* = 1" > station_classes.txt')

    # reclass vulnerability raster to NULL values for stations
    g_script.run_command(
        'r.reclass',
        input='vulnerability_rast',
        output='vulnerability_reclassed',
        rules='station_classes.txt',
        overwrite=True
    )
    # Calc Proximity
    g_script.run_command(
        'r.grow.distance',
        input='vulnerability_reclassed',
        distance='distance',
        flags='n',
        overwrite=True
    )

    # vulnerability classes
    os.popen('echo "0 thru 3000 = 1 \n'
             '3000 thru 8000 = 2\n'
             '8000 thru 15000 = 3\n'
             '* = 4" > station_classes.txt')

    # reclass building density to exposure value
    g_script.run_command(
        'r.reclass',
        input='distance',
        output='vulnerability',
        rules='station_classes.txt',
        overwrite=True
    )


if __name__ == '__main__':
    import_data()

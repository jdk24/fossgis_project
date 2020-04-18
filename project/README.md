# Project

The project is structured into the following folders and contents:
- data: input and output files for the analysis
- scripts: scripts to automate the analysis
- webapp: healthy routing webapp
- GrassLocation (after setup): the GrassLocation for Stuttgart]

After installing all dependencies listed in [prerequisites](#prerequesites) the different workflows
 should be executable.

Once _Getting started_ commands are finished you should be able to run every workflow independently.

In a future endeavor the interpolation workflow could be coupled with the database and the web application connected
directly to the database views providing near real-time data.
 
 ## Prerequesites
- [NodeJS](https://nodejs.org/en/) (used: 12.11.1, or use [NVM](https://github.com/nvm-sh/nvm))
- [Python 3](https://www.python.org/downloads/) (used: 3.6.8)
- [GRASS GIS](https://grass.osgeo.org/download/) (used: 7.7.svn, Python: 2.7.15, wxPython: 4.0.4)
- [PostgreSQL](https://www.postgresql.org/download/) (used: used 11.5)
- ([GeoServer](http://geoserver.org/download/) (not used due to technical issues))


## Getting started

1. Clone the repository and enter it
    ```bash
    git clone https://github.com/jdk24/fossgis_project.git
    cd fossgis_project
    ```
1. Create python 3 environment for later use
    ```bash
    python3 -m venv env
    
    source env/bin/activate
    # Windows: .\env\Scripts\activate
    
    # Check if you are using correct python
    which python
    -> .../env/bin/python
    
    # Windows:
    # where python
    # -> .../env/bin/python.exe
    
    # install dependecy
    pip install requests
    
    # exit environment
    deactivate
    ```
1. Install osmtogeojson conversion command line tool
    ```bash
    npm -i -g osmtogeojson
    ```

## PostgreSQL database workflow
Dependencies: PostgreSQL, GeoServer/GRASS GIS?

1. Change to scripts folder (if you are not already there)
    ```bash
    project/scripts
    ```
1. Run database setup script
    ```bash
    psql 0_db_setup.sql
    ```
1. Start cron jobs to download lubw & luftdaten data
    ```bash
    # Julian more info pls :D
    sh 1_1_dl_lubw.sh
    sh 1_2_dl_luftdaten.sh
    ```
1. (Fill database with values from january if needed
    ```bash
    psql luftdaten_backup.sql
    ```
    )

## Interpolation workflow
Dependencies: Python 3, GRASS GIS

1. Activate Python 3 environment
    ```bash
    source env/bin/activate
    ```
1. Switch to scripts folder
    ```bash
    cd project/scripts
    ```
1. Run OSM download script
    ```bash
    # if you are having trouble with this step try the manual download at the bottom of this README
    python download_osm_data.py
    ```
1. Deactivate the environment
    ```bash
    deactivate
    ```
1. Open GRASS GIS or run from your custom shell (keeps plugins & autocomplete)
    ```bash
    # might need adjustment: open grass from OS once and copy the opening command of grass
    /usr/bin/env -i HOME=/Users/*yourUser* PATH=/usr/bin:/bin:/usr/sbin:/etc:/usr/lib /Applications/GRASS-7.7.app/Contents/MacOS/Grass.sh
    ```
1. Choose project folder as database directory
1. Create new Location called `GrassLocation` with name `Stuttgart` and select CRS `UTM 32N WGS84`

You can now either
- run the following commands from the GRASS terminal
- Start PyCharm or your favorite Python IDE from the Grass Terminal for full command support and create run configurations
    for the python scripts
- (you could possibly also use the simple python editor the GRASS gui has to offer, but with my mac installation i couldn't
    even import a file, there is no command completion and it sucks in other ways too, so think twice...)
    
Afterwards:
1. Change to scripts folder (if you are not already there)
    ```bash
    project/scripts
    ```
1. Run interpolation setup script
    ```bash
    python 3_interpolation_setup.py
    ```
1. Run the algorithm tests to create some categorized raster layers and `.png` files in `data/img` for different configurations.
    This step is optional. Adjust `keep_intermadiates` value to keep intermediate raster.
    ```bash
    python 4_1_idw_tests.py
    python 4_2_bspline_tests.py
    python 4_3_rst_tests.py
    ```
1. Run interpolation process script to generate hourly layers and `.geojson` files from the ones in `data/pm25` (loaded in interpolation setup)
    ```bash
    python 5_interpolation_process.py
    ```

The interpolation process script can easily switch between the 3 algorithms by passing a different `i_method` value to
    the `analyse()` function.

## Routing application workflow
Dependencies: NodeJS

1. change to webapp folder
    ```bash
    project/webapp
    ```
1. install webapp dependencies
    ```bash
    npm install
    ```
1. serve webapp locally
    ```bash
    npm run serve
    ```
1. open the application in you favorite browser on https://localhost:8080 (check output of previous command)


## Overpass Queries

If you are having trouble to downloading the osm data run the following query on overpass-turbo.eu
and export it as geojson:

stuttgart_districts.geojson:
```
(
relation
  ["boundary"="administrative"]
  ["admin_level"=9]
  ["name"~"Stuttgart-Süd|Stuttgart-Ost|Stuttgart-West|Stuttgart-Nord|Stuttgart-Mitte|Feuerbach|Botnang|Bad Cannstatt|Hedelfingen|Wangen|Münster"]
  (48.750077, 9.111614,48.823706, 9.268856);
);
(._;>;);
out;
```
__The geojson contains both 'fixme' and 'FIXME' properties. 'fixme' was replaced by 'FIXME'__
__to avoid duplicate table names which crashes the import into the Grass DB__.

stuttgart.geojson:
```
(
relation
  ["boundary"="administrative"]
  ["admin_level"=6]
  ["name"="Stuttgart"]
  (48.750077, 9.111614,48.823706, 9.268856);
);
(._;>;);
out;
```

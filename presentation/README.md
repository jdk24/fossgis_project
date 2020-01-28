# Project Files

Contains the following:
- data: lubw and luftdaten station information for one day
- GrassLocation: well the GrassLocation for Stuttgart
- scripts: there are scripts inside

## Getting started

1. Start a Grass session using the GrassLocation folder as Location.
(Alternatively Create a new Location called GrassLocation with name Stuttgart as UTM 32N WGS84)
2. Copy lubw.csv lubw.geojson luftdaten.csv luftdaten.geojson to the data folder
(2.1 Start PyCharm or your favorite Python IDE from the Grass Terminal for full command support)
3. Run `scripts/2_setup.py` to initialize the project.

## Overpass Queries

If you cannot initiate and establish a database connection, the OSM data can be downloaded via the 
following Overpass API queries:

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
__to avoid duplicate table names which crashes the import__.

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

## Create interpolated raster

The actual interpolation script is found in `scripts/3_interpolation.py`
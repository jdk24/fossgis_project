# coding=utf-8
# tested on Python 3.7
# Use a Python 3 env with following installed packages:
# - requests
# - osmtogeojson
from __future__ import print_function

import requests
import os
import json
import sys


def out(input_string):
    """
    Writes input string to sys.stdout
    :param input_string: String to write
    """
    sys.stdout.write(input_string + '\n')
    sys.stdout.flush()


if __name__ == '__main__':
    out('Downloading stuttgart administrative area from overpass API. Please wait ...')
    # set up parameters
    bbox = "48.750077,9.111614,48.823706,9.268856"
    url = "https://overpass-api.de/api/interpreter"
    data = {
        'data': '[out:json][timeout:25];'
                'nwr({0});'
                '(relation'
                '["boundary"="administrative"]'
                '["admin_level"=6]'
                '["name"~"Stuttgart"]'  # one of districts
                '({0}););'
                '(._;>;);out;'.format(bbox)
    }

    overpass_output_json = '../data/overpass_output.json'
    try:
        r = requests.post(url, data)
        with open(overpass_output_json, 'w') as f:
            f.write(r.text)
        r.close()
        out('Download successful')
    except Exception as e:
        out(e.message)
        out('Download failed.')
        os.remove(overpass_output_json)
        sys.exit()

    # convert overpass output to geojson
    out('Converting to GeoJSON')
    try:
        os.system('osmtogeojson ../data/overpass_output.json > ../data/stuttgart.geojson')
    except Exception as e:
        out(e.message)
        out('Conversion failed. Make sure you have nodejs installed and try to install osmtogeojson'
            ' globally using"npm -i -g osmtogeojson"')
        os.remove(overpass_output_json)
        sys.exit()

    # remove temporary file
    os.remove(overpass_output_json)

    # minify geojson
    with open('../data/stuttgart.geojson', 'r') as fp:
        temp = json.load(fp)
    with open('../data/stuttgart.geojson', 'w') as fp:
        fp.write(json.dumps(temp).replace('fixme', 'FIXME'))

    out('File stuttgart.geojson created in data folder.')

    out('Downloading stuttgart districts from overpass API. Please wait ...')
    # set up parameters
    bbox = "48.750077,9.111614,48.823706,9.268856"
    url = "https://overpass-api.de/api/interpreter"
    districts = ["Stuttgart-Süd",
                 "Stuttgart-Ost",
                 "Stuttgart-West",
                 "Stuttgart-Nord",
                 "Stuttgart-Mitte",
                 "Feuerbach",
                 "Botnang",
                 "Bad Cannstatt",
                 "Hedelfingen",
                 "Wangen",
                 "Münster"]
    data = {
        'data': '[out:json][timeout:25];'
                'nwr({0});'
                '(relation'
                '["boundary"="administrative"]'
                '["admin_level"=9]'
                '["name"~"{1}"]'  # one of districts
                '({0}););'
                '(._;>;);out;'.format(bbox, "|".join(districts))
    }

    overpass_output_json = '../data/overpass_output.json'
    try:
        r = requests.post(url, data)
        with open(overpass_output_json, 'w') as f:
            f.write(r.text)
        r.close()
        out('Download successful')
    except Exception as e:
        out(e.message)
        out('Download failed.')
        os.remove(overpass_output_json)
        sys.exit()

    # convert overpass output to geojson
    out('Converting to GeoJSON')
    try:
        os.system('osmtogeojson ../data/overpass_output.json > ../data/stuttgart_districts.geojson')
    except Exception as e:
        out(e.message)
        out('Conversion failed. Make sure you have nodejs installed and try to install osmtogeojson'
            ' globally using"npm -i -g osmtogeojson"')
        os.remove(overpass_output_json)
        sys.exit()

    # remove temporary file
    os.remove(overpass_output_json)

    # minify geojson
    with open('../data/stuttgart_districts.geojson', 'r') as fp:
        temp = json.load(fp)
    with open('../data/stuttgart_districts.geojson', 'w') as fp:
        fp.write(json.dumps(temp).replace('fixme', 'FIXME'))

    out('File stuttgart_districts.geojson created in data folder.')

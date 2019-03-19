import datetime
# import logging
import pprint

import ee
import pytest

import image as sims_et
import collection as sims_et_coll
import utils
import pandas as pd

def get_region_df(info):
    """Convert the output of getRegions to a pandas dataframe"""
    col_dict = {}
    info_dict = {}
    for i, k in enumerate(info[0][4:]):
        col_dict[k] = i + 4
        info_dict[k] = {}

    for row in info[1:]:
        date = datetime.datetime.utcfromtimestamp(row[3] / 1000.0).strftime('%Y-%m-%d')
        for k, v in col_dict.items():
            info_dict[k][date] = row[col_dict[k]]

    return pd.DataFrame.from_dict(info_dict)

ee.Initialize()

collections = ['LANDSAT/LC08/C01/T1_SR','LANDSAT/LE07/C01/T1_SR']

etr_source = 'IDAHO_EPSCOR/GRIDMET'
etr_band = 'etr'

# Date range you want to aggregate ET over
# End date is inclusive (like filterDate() calls)
start_date = '2015-01-01'
end_date = '2016-01-01'

# Only keep images with an average cloud cover less than
# Cloud cover filter parameter is not being passed in (yet)
cloud_cover = 90

# Number of extra days (at start and end) to include in interpolation
interp_days = 32
# Interpolation method - currently only LINEAR is supported
interp_method = 'LINEAR'

test_point = ee.Geometry.Point(-121.5265, 38.7399)
study_area = ee.Geometry.Polygon(
        [[[-121.06181640624999, 37.74947086129773],
          [-120.88603515624999, 36.09841849699811],
          [-119.30400390624999, 36.027370248727394],
          [-119.52373046874999, 37.992302272998934]]])

# Hard code the study area and CRS
study_region = study_area.bounds(1, 'EPSG:2163').coordinates().getInfo()
study_crs = 'EPSG:2163'

sims_et_obj = sims_et_coll.Collection(
    collections=collections,
    start_date=start_date,
    end_date=end_date,
    geometry=test_point,
    etr_source=etr_source,
    etr_band=etr_band
)
#pprint.pprint(sims_et_obj.get_image_ids())

overpass_coll = sims_et_obj.overpass(variables=['ndvi','et'])
overpass_df = get_region_df(overpass_coll.getRegion(test_point, scale=30).getInfo())
pprint.pprint(overpass_df)



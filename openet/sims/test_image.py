# Short script to test image collection

import datetime
# import logging
import pprint

import ee
import pytest

import image as sims_et
import utils


COLL_ID = 'LANDSAT/LC08/C01/T1_SR/'
SCENE_ID = 'LC08_044033_20170716'
SCENE_DT = datetime.datetime.strptime(SCENE_ID[-8:], '%Y%m%d')
SCENE_DATE = SCENE_DT.strftime('%Y-%m-%d')
SCENE_DOY = int(SCENE_DT.strftime('%j'))
SCENE_TIME = utils.millis(SCENE_DT)

#First get the sample image from ee
ee.Initialize()
landsat_img = ee.Image(COLL_ID+SCENE_ID)

simsObj = sims_et.Image.from_landsat_c1_sr(sr_image=landsat_img,etr_source='IDAHO_EPSCOR/GRIDMET',
                                           etr_band='etr',landcover_source='USDA/NASS/CDL')
print(simsObj.etr_source)
print(simsObj.landcover_source)

simsNDVI = simsObj.ndvi

simsETcb = simsObj.calculate(['et'])
print(simsETcb.getInfo())

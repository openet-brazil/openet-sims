import datetime
# import logging
import pprint

import ee
import pytest

# Different imports than NDVI model since tests are in same folder as model
from . import utils
from . import collection as model
# import openet.sims as model
# import openet.sims.utils as utils
# TODO: import utils from openet.core
# import openet.core.utils as utils


COLL_ID = 'LANDSAT/LC08/C01/T1_SR/'
SCENE_ID = 'LC08_044033_20170716'
SCENE_DT = datetime.datetime.strptime(SCENE_ID[-8:], '%Y%m%d')
SCENE_DATE = SCENE_DT.strftime('%Y-%m-%d')
SCENE_DOY = int(SCENE_DT.strftime('%j'))
SCENE_TIME = utils.millis(SCENE_DT)
# SCENE_TIME = utils.getinfo(ee.Date(SCENE_DATE).millis())


# Should these be test fixtures instead?
# I'm not sure how to make them fixtures and allow input parameters
def input_image(red=0.1, nir=0.9):
    """Construct a fake input image with renamed bands"""
    return ee.Image.constant([red, nir]).rename(['red', 'nir'])\
        .set({'system:time_start': ee.Date(SCENE_DATE).millis()})


def default_image(ndvi=0.8):
    return ee.Image.constant([ndvi]).rename(['ndvi'])\
        .set({
            'system:index': SCENE_ID,
            'system:time_start': ee.Date(SCENE_DATE).millis(),
            'system:id': COLL_ID + SCENE_ID,
        })


# Setting etr_source and etr_band on the default image to simplify testing
#   but these do not have defaults in the Image class init
def default_image_args(ndvi=0.8, etr_source='IDAHO_EPSCOR/GRIDMET',
                       etr_band='etr', etr_factor=0.85,
                       landcover_source='USDA/NASS/CDL',
                       landcover_band='cropland'):
    return {
        'image': default_image(ndvi=ndvi),
        'etr_source': etr_source,
        'etr_band': etr_band,
        'etr_factor': etr_factor,
        'landcover_source': landcover_source,
        'landcover_band': landcover_band,
    }


def default_image_obj(ndvi=0.8, etr_source='IDAHO_EPSCOR/GRIDMET',
                      etr_band='etr', etr_factor=0.85,
                      landcover_source='USDA/NASS/CDL',
                      landcover_band='cropland'):
    return model.Image(**default_image_args(
        ndvi=ndvi,
        etr_source=etr_source, etr_band=etr_band, etr_factor=etr_factor,
        landcover_source=landcover_source, landcover_band=landcover_band))


def test_ee_init():
    """Check that Earth Engine was initialized"""
    assert ee.Number(1).getInfo() == 1


def test_Image_init_default_parameters():
    m = model.Image(image=default_image())
    assert m.etr_source == None
    assert m.etr_band == None
    assert m.etr_factor == 1.0
    assert m.landcover_source == 'USDA/NASS/CDL'
    assert m.landcover_band == 'cropland'


def test_Image_init_calculated_properties():
    m = default_image_obj()
    assert utils.getinfo(m._time_start) == SCENE_TIME
    assert utils.getinfo(m._index) == SCENE_ID


def test_Image_init_date_properties():
    m = default_image_obj()
    assert utils.getinfo(m._date)['value'] == SCENE_TIME
    assert utils.getinfo(m._year) == int(SCENE_DATE.split('-')[0])
    assert utils.getinfo(m._start_date)['value'] == SCENE_TIME
    assert utils.getinfo(m._end_date)['value'] == utils.millis(
        SCENE_DT + datetime.timedelta(days=1))


@pytest.mark.parametrize(
    'red, nir, expected',
    [
        [0.2, 9.0 / 55, -0.1],
        [0.2, 0.2,  0.0],
        [0.1, 11.0 / 90,  0.1],
        [0.2, 0.3, 0.2],
        [0.1, 13.0 / 70, 0.3],
        [0.3, 0.7, 0.4],
        [0.2, 0.6, 0.5],
        [0.2, 0.8, 0.6],
        [0.1, 17.0 / 30, 0.7],
        [0.1, 0.9, 0.8],
    ]
)
def test_Image_static_ndvi_calculation(red, nir, expected, tol=0.000001):
    output = utils.constant_image_value(
        model.Image._ndvi(input_image(red=red, nir=nir)))
    assert abs(output['ndvi'] - expected) <= tol


def test_Image_static_ndvi_band_name():
    output = utils.getinfo(model.Image._ndvi(input_image()))
    assert output['bands'][0]['id'] == 'ndvi'


def test_Image_ndvi_properties():
    """Test if properties are set on the ndvi image"""
    output = utils.getinfo(default_image_obj().ndvi)
    assert output['bands'][0]['id'] == 'ndvi'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


def test_Image_ndvi_constant_value(ndvi=0.8, expected=0.8, tol=0.0001):
    output = utils.constant_image_value(default_image_obj(ndvi=ndvi).ndvi)
    assert abs(output['ndvi'] - expected) <= tol


def test_Image_fc_properties():
    """Test if properties are set on the fc image"""
    output = utils.getinfo(default_image_obj().fc)
    assert output['bands'][0]['id'] == 'fc'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


@pytest.mark.parametrize(
    'ndvi, expected',
    [
        [0.8, 0.828],
        [0.7, 0.702],
        [0.2, 0.072],
        # Check if low NDVI Fc values are clamped
        [0.1, 0.0],
        [0.0, 0.0],
        [-0.1, 0.0],
        # Check if high NDVI Fc values are clamped
        [0.95, 1.0],
    ]
)
def test_Image_fc_constant_value(ndvi, expected, tol=0.0001):
    args = default_image_args(ndvi=ndvi)
    output_img = model.Image(**args).fc
    output = utils.constant_image_value(output_img)
    assert abs(output['fc'] - expected) <= tol


# CGM - I'm not sure what the value of this test is
# def test_Image_fc_default_value(ndvi=0.8, expected=0.828, tol=0.0001):
#     output = utils.constant_image_value(default_image_obj(ndvi=ndvi).fc)
#     assert abs(output['fc'] - expected) <= tol


def test_Image_landcover_properties():
    """Test if properties are set on the landcover image"""
    output = utils.getinfo(default_image_obj().landcover)
    assert output['bands'][0]['id'] == 'cropland'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


@pytest.mark.parametrize(
    'landcover_value, expected',
    [
        [1, 1],
        [69, 2],
        [66, 3],
    ]
)
def test_Image_landcover_constant_value(landcover_value, expected):
    output = utils.constant_image_value(default_image_obj(
        landcover_source=landcover_value).landcover)
    assert output['cropland'] == expected


@pytest.mark.parametrize(
    'xy, expected',
    [
        # Test spots around the Five Points CIMIS station
        [[-120.113, 36.336], 1],
        [[-120.1073, 36.3309], 2],
        [[-120.108, 36.3459], 3],
    ]
)
def test_Image_landcover_point_value(xy, expected):
    output = utils.point_image_value(default_image_obj(
        landcover_source='USDA/NASS/CDL').landcover, xy)
    assert output['cropland'] == expected


def test_Image_landcover_source_exception():
    with pytest.raises(ValueError):
        utils.getinfo(default_image_obj(landcover_source='DEADBEEF').landcover)


def test_Image_kc_properties():
    """Test if properties are set on the kc image"""
    output = utils.getinfo(default_image_obj().kc)
    assert output['bands'][0]['id'] == 'kc'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


@pytest.mark.parametrize(
    'ndvi, landcover, expected',
    [
        # 1.26 * 0.8 - 0.18 = 0.828
        # ((0.828 ** 2) * -0.4771) + (1.4047 * 0.828) + 0.15 = 0.9859994736
        [0.8, 1, 0.9859994736],
        [0.7, 69, 0.702 * 1.7],
        [0.8, 66, 0.828 * 1.48 + 0.007],
        [0.2, 1, 0.2486651136],
        # Test if low NDVI Kc values are clamped
        # Fc for NDVI of 0.1 should be clamped to 0.0
        [0.1, 1, 0.15],
        [0.1, 69, 0.0],
        [0.1, 66, 0.007],
        # Test if high NDVI Kc values are clamped
        # Kc for class 1 can never get to clamp limit since NDVI <= 1
        [1.0, 1, 1.0776],
        [0.90, 69, 1.25],
        [0.90, 66, 1.25],
    ]
)
def test_Image_kc_constant_value(ndvi, landcover, expected, tol=0.0001):
    output = utils.constant_image_value(default_image_obj(
        ndvi=ndvi, landcover_source=landcover).kc)
    assert abs(output['kc'] - expected) <= tol


def test_Image_kc_constant_nodata():
    output = utils.constant_image_value(default_image_obj(landcover_source=0).kc)
    assert output['kc'] is None


# CGM - This doesn't work because landcover defaults to CDL
# def test_Image_kc_default_value(ndvi=0.8, expected=1.0, tol=0.0001):
#     output = utils.constant_image_value(default_image_obj(ndvi=ndvi).kc)
#     assert abs(output['kc'] - expected) <= tol


def test_Image_etf_properties():
    """Test if properties are set on the ETf image"""
    output = utils.getinfo(default_image_obj().etf)
    assert output['bands'][0]['id'] == 'etf'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


def test_Image_etf_constant_value():
    # ETf method returns Kc
    output = utils.constant_image_value(default_image_obj(
        ndvi=0.8, landcover_source=1).etf)
    assert abs(output['etf'] - 0.9859994736) <= 0.0001


def test_Image_etr_constant_value(etr=10.0, tol=0.0001):
    output = utils.constant_image_value(default_image_obj(
        etr_source=etr, etr_factor=0.85).etr)
    assert abs(output['etr'] - etr * 0.85) <= tol


def test_Image_etr_properties():
    """Test if properties are set on the ETr image"""
    output = utils.getinfo(default_image_obj().etr)
    assert output['bands'][0]['id'] == 'etr'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


def test_Image_etr_source_exception():
    """Test that an Exception is raise for an invalid image ID"""
    with pytest.raises(Exception):
        utils.getinfo(default_image_obj(etr_source=None).etr)


# CGM - I'm not sure why this is commented out
# def test_Image_etr_band_exception():
#     """Test that an Exception is raise for an invalid etr band name"""
#     with pytest.raises(Exception):
#         utils.getinfo(default_image_obj(etr_band=None).etr)


def test_Image_et_properties():
    """Test if properties are set on the ET image"""
    output = utils.getinfo(default_image_obj().et)
    assert output['bands'][0]['id'] == 'et'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


def test_Image_et_constant_value():
    output = utils.constant_image_value(default_image_obj(
        etr_source=10, etr_factor=1.0, landcover_source=1).et)
    assert abs(output['et'] - 10 * 0.986) <= 0.0001


def test_Image_mask_properties():
    """Test if properties are set on the time image"""
    output = utils.getinfo(default_image_obj().mask)
    assert output['bands'][0]['id'] == 'mask'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


def test_Image_mask_constant_value():
    output = utils.constant_image_value(default_image_obj(
        landcover_source=1).mask)
    assert output['mask'] == 1


def test_Image_time_properties():
    """Test if properties are set on the time image"""
    output = utils.getinfo(default_image_obj().time)
    assert output['bands'][0]['id'] == 'time'
    assert output['properties']['system:index'] == SCENE_ID
    assert output['properties']['system:time_start'] == SCENE_TIME
    assert output['properties']['image_id'] == COLL_ID + SCENE_ID


def test_Image_time_constant_value():
    output = utils.constant_image_value(default_image_obj(
        landcover_source=1).time)
    assert output['time'] == SCENE_TIME


def test_Image_calculate_variables_default():
    output = utils.getinfo(default_image_obj().calculate())
    assert set([x['id'] for x in output['bands']]) == set(['et'])


def test_Image_calculate_variables_custom():
    variables = ['ndvi']
    output = utils.getinfo(default_image_obj().calculate(variables))
    assert set([x['id'] for x in output['bands']]) == set(variables)


def test_Image_calculate_variables_all():
    variables = ['et', 'etf', 'etr', 'fc', 'kc', 'mask', 'ndvi', 'time']
    # variables = ['et', 'etr', 'fc', 'kc', 'landcover', 'mask', 'ndvi', 'time']
    output = utils.getinfo(default_image_obj().calculate(variables=variables))
    assert set([x['id'] for x in output['bands']]) == set(variables)


def test_Image_from_landsat_c1_sr_default_image():
    """Test that the classmethod is returning a class object"""
    output = model.Image.from_landsat_c1_sr(input_image())
    assert type(output) == type(default_image_obj())


@pytest.mark.parametrize(
    'image_id',
    [
        'LANDSAT/LC08/C01/T1_SR/LC08_044033_20170716',
        'LANDSAT/LE07/C01/T1_SR/LE07_044033_20170708',
        'LANDSAT/LT05/C01/T1_SR/LT05_044033_20110716',
        'LANDSAT/LT04/C01/T1_SR/LT04_044033_19830812',
    ]
)
def test_Image_from_landsat_c1_sr_image_id(image_id):
    """Test instantiating the class from a Landsat image ID"""
    output = utils.getinfo(model.Image.from_landsat_c1_sr(image_id).ndvi)
    assert output['properties']['system:index'] == image_id.split('/')[-1]


def test_Image_from_landsat_c1_sr_image():
    """Test instantiating the class from a Landsat ee.Image"""
    image_id = 'LANDSAT/LC08/C01/T1_SR/LC08_044033_20170716'
    output = utils.getinfo(model.Image.from_landsat_c1_sr(
        ee.Image(image_id)).ndvi)
    assert output['properties']['system:index'] == image_id.split('/')[-1]


def test_Image_from_landsat_c1_sr_kc():
    """Test if ETf can be built from a Landsat images"""
    image_id = 'LANDSAT/LC08/C01/T1_SR/LC08_044033_20170716'
    output = utils.getinfo(model.Image.from_landsat_c1_sr(image_id).kc)
    assert output['properties']['system:index'] == image_id.split('/')[-1]


def test_Image_from_landsat_c1_sr_et():
    """Test if ET can be built from a Landsat images"""
    image_id = 'LANDSAT/LC08/C01/T1_SR/LC08_044033_20170716'
    output = utils.getinfo(model.Image.from_landsat_c1_sr(
        image_id, etr_source='IDAHO_EPSCOR/GRIDMET', etr_band='etr').et)
    assert output['properties']['system:index'] == image_id.split('/')[-1]


def test_Image_from_landsat_c1_sr_exception():
    """Test that an Exception is raise for an invalid image ID"""
    with pytest.raises(Exception):
        utils.getinfo(model.Image.from_landsat_c1_sr(ee.Image('FOO')).ndvi)


@pytest.mark.parametrize(
    'image_id',
    [
        'LANDSAT/LC08/C01/T1_SR/LC08_044033_20170716',
    ]
)
def test_Image_from_image_id(image_id):
    """Test instantiating the class using the from_image_id method"""
    output = utils.getinfo(model.Image.from_image_id(image_id).ndvi)
    assert output['properties']['system:index'] == image_id.split('/')[-1]
    assert output['properties']['image_id'] == image_id


def test_Image_from_method_kwargs():
    """Test that the init parameters can be passed through the helper methods"""
    assert model.Image.from_landsat_c1_sr(
        'LANDSAT/LC08/C01/T1_SR/LC08_042035_20150713',
        etr_band='FOO').etr_band == 'FOO'

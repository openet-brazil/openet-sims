
import ee
import pytest

from . import model
from . import utils


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
def test_Image_fc(ndvi, expected, tol=0.0001):
    output = utils.constant_image_value(model.fc(ndvi=ee.Image.constant(ndvi)))
    assert abs(output['fc'] - expected) <= tol


@pytest.mark.parametrize(
    'ndvi, fc_min, fc_max, expected',
    [
        [0.8, 0, 0.8, 0.8],
        [0.2, 0.5, 0.8, 0.5],
    ]
)
def test_Image_fc_min_max(ndvi, fc_min, fc_max, expected, tol=0.0001):
    output = utils.constant_image_value(model.fc(
        ndvi=ee.Image.constant(ndvi), fc_min=fc_min, fc_max=fc_max))
    assert abs(output['fc'] - expected) <= tol


def test_Image_crop_type_source_exception():
    with pytest.raises(ValueError):
        utils.getinfo(model.crop_type(crop_type_source='DEADBEEF'))


def test_Image_crop_type_constant_value():
    output = utils.constant_image_value(model.crop_type(crop_type_source=10))
    assert output['crop_type'] == 10


@pytest.mark.parametrize(
    'year, expected',
    [
        [2007, 2008],
        [2008, 2008],
        [2019, 2018],
    ]
)
def test_Image_crop_type_source_cdl_collection(year, expected):
    """Test that CDL image collection is limited to 2008-2018"""
    output = utils.getinfo(model.crop_type(
        crop_type_source='USDA/NASS/CDL', year=ee.Number(year)))
    assert output['properties']['id'] == 'USDA/NASS/CDL/{}'.format(expected)


def test_Image_crop_type_source_cdl_image():
    output = utils.getinfo(model.crop_type(
        crop_type_source='USDA/NASS/CDL/2008'))
    assert output['properties']['id'] == 'USDA/NASS/CDL/2008'


def test_Image_crop_type_source_cdl_image_exception():
    """Requesting a CDL image that doesn't exist should raise an EE exception"""
    with pytest.raises(Exception):
        utils.getinfo(model.crop_type(crop_type_source='USDA/NASS/CDL/2099'))


def test_Image_crop_type_source_openet_crop_type():
    output = utils.getinfo(model.crop_type(
        crop_type_source='projects/openet/crop_type'))
    assert output['bands'][0]['id'] == 'crop_type'


def test_Image_crop_class_remap_exception():
    with pytest.raises(ValueError):
        utils.getinfo(model.crop_class(
            crop_type=ee.Image.constant(10), crop_type_remap='DEADBEEF'))


@pytest.mark.parametrize(
    'crop_type_value, expected',
    [
        [1, 1],
        [3, 1],  # Rice
        [69, 2],
        [66, 3],
    ]
)
def test_Image_crop_class_constant_value(crop_type_value, expected):
    output = utils.constant_image_value(model.crop_class(
        crop_type=ee.Image.constant(crop_type_value).rename(['crop_type']),
        crop_type_remap='CDL'))
    assert output['crop_class'] == expected
    # assert output['remapped'] == expected




def test_kcb_full():
    assert False


def test_fr():
    assert False







@pytest.mark.parametrize(
    'fc, crop_class, expected',
    [
        # 1.26 * 0.8 - 0.18 = 0.828
        # ((0.828 ** 2) * -0.4771) + (1.4047 * 0.828) + 0.15 = 0.9859994736
        [0.828, 1, 0.9859994736],
        # [0.7, 2, 0.702 * 1.7],
        # [0.8, 3, 0.828 * 1.48 + 0.007],
        # [0.2, 1, 0.2486651136],
        # # Test if low NDVI Kc values are clamped
        # # Fc for NDVI of 0.1 should be clamped to 0.0
        # [0.1, 1, 0.15],
        # [0.1, 2, 0.0],
        # [0.1, 3, 0.007],
        # # Test if high NDVI Kc values are clamped
        # # Kc for class 1 can never get to clamp limit since NDVI <= 1
        # [1.0, 1, 1.0776],
        # [0.90, 2, 1.25],
        # [0.90, 3, 1.25],
    ]
)
def test_Image_kc_constant_value(fc, crop_class, expected, tol=0.0001):
    output = utils.constant_image_value(model.kc(
        fc=ee.Image.constant(fc).rename(['fc']),
        crop_class=ee.Image.constant(crop_class)))
    print(output)
    assert abs(output['kc'] - expected) <= tol


# def test_Image_kc_constant_nodata():
#     output = utils.constant_image_value(model.kc(
#         crop_type_source=ee.Image.constant(0)))
#     assert output['kc'] is None


# CGM - This doesn't work because crop_type defaults to CDL
# def test_Image_kc_default_value(ndvi=0.8, expected=1.0, tol=0.0001):
#     output = utils.constant_image_value(default_image_obj(ndvi=ndvi).kc)
#     assert abs(output['kc'] - expected) <= tol





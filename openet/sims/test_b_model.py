
import ee
import pytest

from . import data
from . import model
from . import utils

# DATE = '2017-07-16'
YEAR = 2017
DOY = 197


# CGM - Should these be test fixtures instead?
#   I'm not sure how to make them fixtures and allow input parameters
# CGM - Setting default crop_type_source to 2017 image to simplify testing
#   but the default in the Model class init is the full collection
def default_model_args(year=YEAR, doy=DOY,
                       crop_type_source='USDA/NASS/CDL/{}'.format(YEAR),
                       crop_type_remap='CDL'):
    return {
        'year': year, 'doy': doy,
        'crop_type_source': crop_type_source,
        'crop_type_remap': crop_type_remap,
    }


def default_model_obj(year=YEAR, doy=DOY,
                      crop_type_source='USDA/NASS/CDL/{}'.format(YEAR),
                      crop_type_remap='CDL'):
    return model.Model(**default_model_args(
        year=year, doy=doy,
        crop_type_source=crop_type_source, crop_type_remap=crop_type_remap))


def test_ee_init():
    """Check that Earth Engine was initialized"""
    assert ee.Number(1).getInfo() == 1


def test_crop_data_image():
    output = utils.constant_image_value(model.crop_data_image(
        param_name='crop_class',
        crop_type=ee.Image.constant(9).rename(['crop_class']),
        crop_data={9: {'crop_class': 10}}))
    assert output['crop_class'] == 10


def test_crop_data_image_int_scalar():
    # Test that floating point values are scaled to int before remapping
    output = utils.constant_image_value(model.crop_data_image(
        param_name='m_l', crop_type=ee.Image.constant(9).rename(['m_l']),
        crop_data={9: {'m_l': 0.01}}))
    assert output['m_l'] == 0.01


def test_Model_init_default_parameters():
    m = default_model_obj()
    assert m.crop_type_source == 'USDA/NASS/CDL/{}'.format(YEAR)
    assert m.crop_type_remap == 'CDL'


@pytest.mark.parametrize('parameter', ['m_l', 'h_max'])
def test_Model_init_crop_data_images(parameter):
    output = utils.getinfo(getattr(default_model_obj(), parameter))
    assert output['bands'][0]['id'] == parameter


@pytest.mark.parametrize(
    'year, expected',
    [
        [2007, 2008],
        [2008, 2008],
        [2019, 2018],
    ]
)
def test_Model_crop_type_source_cdl_collection(year, expected):
    """Test that the CDL collection is filtered to a single year and is limited
    to years with data (2008-2018 as of 7/15/2019)
    """
    output = utils.getinfo(default_model_obj(
        crop_type_source='USDA/NASS/CDL', year=ee.Number(year)).crop_type)
    assert output['properties']['id'] == 'USDA/NASS/CDL/{}'.format(expected)


def test_Model_crop_type_source_cdl_image():
    output = utils.getinfo(default_model_obj(
        crop_type_source='USDA/NASS/CDL/2008').crop_type)
    assert output['properties']['id'] == 'USDA/NASS/CDL/2008'


def test_Model_crop_type_source_cdl_image_exception():
    """Requesting a CDL image that doesn't exist should raise an EE exception"""
    with pytest.raises(Exception):
        utils.getinfo(default_model_obj(crop_type_source='USDA/NASS/CDL/2099'))
        # CGM - The exception is raised in the _crop_type() method which is
        #   in the init.  If crop_type is a lazy property then it is necessary
        #   to request the property in order to raise the exception.
        # utils.getinfo(default_model_obj(
        #     crop_type_source='USDA/NASS/CDL/2099').crop_type)


def test_Model_crop_type_source_openet_crop_type():
    output = utils.getinfo(default_model_obj(
        crop_type_source='projects/openet/crop_type').crop_type)
    assert output['bands'][0]['id'] == 'crop_type'


def test_Model_crop_type_source_exception():
    with pytest.raises(ValueError):
        utils.getinfo(default_model_obj(crop_type_source='FOO'))
        # utils.getinfo(default_model_obj(crop_type_source='FOO').crop_type)


def test_Model_crop_type_constant_value():
    output = utils.constant_image_value(default_model_obj(
        crop_type_source=10).crop_type)
    assert output['crop_type'] == 10


def test_Model_crop_data():
    assert default_model_obj(crop_type_remap='CDL').crop_data


def test_Model_crop_data_remap_exception():
    with pytest.raises(ValueError):
        utils.getinfo(default_model_obj(crop_type_remap='FOO'))
        # utils.getinfo(default_model_obj(crop_type_remap='FOO').crop_data)


@pytest.mark.parametrize(
    'crop_type, expected',
    [
        [1, data.cdl[1]['h_max']],
        # [69, data.cdl[69]['h_max']],
        # [66, data.cdl[66]['h_max']],
        # [1, 1],
        # [69, 2],
        # [66, 3],
    ]
)
def test_Model_h_max(crop_type, expected):
    output = utils.constant_image_value(default_model_obj(
        crop_type_source=crop_type).h_max)
    assert output['h_max'] == expected


@pytest.mark.parametrize(
    'crop_type, expected',
    [
        [1, data.cdl[1]['m_l']],
        # [69, data.cdl[69]['m_l']],
        # [66, data.cdl[66]['m_l']],
        # [1, 2],
        # 69, 1.5],
        # [66, 2],
    ]
)
def test_Model_m_l(crop_type, expected):
    output = utils.constant_image_value(default_model_obj(
        crop_type_source=crop_type).m_l)
    assert output['m_l'] == expected


@pytest.mark.parametrize(
    'crop_type, expected',
    [
        [1, 1],
        [69, 2],
        [66, 3],
        [3, 1],  # Rice may be switched to class 5 instead of 1
    ]
)
def test_Model_crop_class_constant_value(crop_type, expected):
    output = utils.constant_image_value(default_model_obj(
        crop_type_source=crop_type,
        crop_type_remap='CDL').crop_class)
    assert output['crop_class'] == expected


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
def test_Model_fc(ndvi, expected, tol=0.0001):
    output = utils.constant_image_value(default_model_obj().fc(
        ndvi=ee.Image.constant(ndvi)))
    assert abs(output['fc'] - expected) <= tol


@pytest.mark.parametrize(
    'ndvi, fc_min, fc_max, expected',
    [
        [0.8, 0, 0.8, 0.8],
        [0.2, 0.5, 0.8, 0.5],
    ]
)
def test_Model_fc_min_max(ndvi, fc_min, fc_max, expected, tol=0.0001):
    output = utils.constant_image_value(default_model_obj().fc(
        ndvi=ee.Image.constant(ndvi), fc_min=fc_min, fc_max=fc_max))
    assert abs(output['fc'] - expected) <= tol


def test_Model_kc_row_crop_constant_value(fc=0.8, tol=0.0001):
    expected = ((fc ** 2) * -0.4771) + (1.4047 * fc) + 0.15
    output = utils.constant_image_value(
        default_model_obj(crop_type_source=1).kc_row_crop(
            fc=ee.Image.constant(fc)).rename('kc'))
    assert abs(output['kc'] - expected) <= tol


# def test_Model_kc_row_generic_masked(crop_type=0):
#     output = utils.constant_image_value(
#         default_model_obj(crop_type_source=crop_type).kc_row_crop(
#             fc=ee.Image.constant(0.7)).rename('kc'))
#     assert output['kc'] == None


@pytest.mark.parametrize(
    'fc, expected',
    [
        [0.8, 0.92832],
    ]
)
def test_Model_kc_row_crop_custom_constant_value(fc, expected, tol=0.0001):
    output = utils.constant_image_value(
        default_model_obj(crop_type_source=1).kc_row_crop_custom(
            fc=ee.Image.constant(fc)).rename('kc'))
    assert abs(output['kc'] - expected) <= tol


@pytest.mark.parametrize(
    'fc, expected',
    [
        [0.0, 0.0],
        [0.5, 0.75],
        [0.6, 0.8434],  # 0.6 ** (1/3)
        # [0.7, 0.8879],  # 0.7 ** (1/3)
        [0.8, 0.9283],  # 0.8 ** (1/3)
        # [0.9, 0.9655],  # 0.9 ** (1/3)
        [1.0, 1.0],  # 1.0 ** (1/3)
    ]
)
def test_Model_kc_vine_constant_value(fc, expected, tol=0.0001):
    output = utils.constant_image_value(
        default_model_obj(crop_type_source=69).kc_vine(
            fc=ee.Image.constant(fc)).rename('kc'))
    assert abs(output['kc'] - expected) <= tol


# def test_Model_kc_vine_masked(crop_type=0):
#     output = utils.constant_image_value(
#         default_model_obj(crop_type_source=crop_type).kc_vine(
#             fc=ee.Image.constant(0.7)).rename('kc'))
#     assert output['kc'] == None


def test_Model_kc_tree_constant_value(fc=0.8, expected=0.8*1.48+0.007, tol=0.0001):
    output = utils.constant_image_value(
        default_model_obj(crop_type_source=66).kc_tree(
            fc=ee.Image.constant(fc)).rename('kc'))
    assert abs(output['kc'] - expected) <= tol


@pytest.mark.parametrize(
    'fc, expected',
    [
        [0.8, 0.4096],
    ]
)
def test_Model_kc_tree_custom_constant_value(fc, expected, tol=0.0001):
    output = utils.constant_image_value(
        default_model_obj(crop_type_source=66).kc_tree_custom(
            fc=ee.Image.constant(fc)).rename('kc'))
    assert abs(output['kc'] - expected) <= tol


@pytest.mark.parametrize(
    'ndvi, fc, expected',
    [
        [-0.1, 0.0, 1.05],
        [0.14, 0.0, 1.05],
        # An NDVI in the range [0.14, 0.142857] will be clamped to 0 in fc(),
        # but is above the 0.14 threshold in kc() so it is not set to 1.05.
        [0.142, 0, 0],
        [0.143, 1.26 * 0.143 - 0.18, 1.26 * 0.143 - 0.18],
        [0.8, 1.26 * 0.8 - 0.18, 1.26 * 0.8 - 0.18],
    ]
)
def test_Model_kc_rice_constant_value(ndvi, fc, expected, tol=0.0001):
    output = utils.constant_image_value(
        default_model_obj(crop_type_source=3).kc_rice(
            fc=ee.Image.constant(fc), ndvi=ee.Image.constant(ndvi)).rename('kc'))
    assert abs(output['kc'] - expected) <= tol


# def test_kcb_full():
#     assert False
#
#
# def test_fr():
#     assert False


@pytest.mark.parametrize('crop_type', [1, 69, 66, 3])
def test_Model_kc_constant_value(crop_type):
    # Check that a number is returned for all crop classes
    output = utils.constant_image_value(
        default_model_obj(crop_type_source=crop_type).kc(
            fc=ee.Image.constant(0.8), ndvi=ee.Image.constant(0.5)).rename('kc'))
    assert output['kc'] is not None


def test_Model_kc_crop_class_0():
    output = utils.constant_image_value(
        default_model_obj(crop_type_source=0).kc(
            fc=ee.Image.constant(0.8), ndvi=ee.Image.constant(0.5)).rename('kc'))
    assert output['kc'] == 0.0



# def test_Model_kc_constant_nodata():
#     output = utils.constant_image_value(model.kc(
#         crop_type_source=ee.Image.constant(0)))
#     assert output['kc'] is None


# CGM - This doesn't work because crop_type defaults to CDL
# def test_Model_kc_default_value(ndvi=0.8, expected=1.0, tol=0.0001):
#     output = utils.constant_image_value(default_image_obj(ndvi=ndvi).kc)
#     assert abs(output['kc'] - expected) <= tol





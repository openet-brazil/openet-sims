import ee
import pytest

import openet.sims.data as data
import openet.sims.utils as utils


def test_int_scalar():
    assert data.int_scalar == 100
    # assert data.int_scalar
    # assert data.int_scalar % 10 == 0


def test_cdl_dict():
    assert type(data.cdl) is dict


# CGM - This doesn't really need to be 4 separate tests
#   It could probably be rewritten to make a single call on the collection
# @pytest.mark.parametrize('year', [2016, 2017, 2018, 2019])
@pytest.mark.parametrize('year', [2019])
def test_cdl_crop_types(year):
    output = list(map(round, utils.getinfo(
        ee.Image(f'USDA/NASS/CDL/{year}').get('cropland_class_values'))))
    for crop_type, crop_data in data.cdl.items():
        # Crop type 78 is non-standard CDL code being used for Grapes (table/raisin)
        if crop_type == 78:
            continue
        assert crop_type in output
    # assert all(crop_type in output for crop_type, crop_data in data.cdl.items())

# CGM - Testing to see if crop type keys have changed or all present doesn't
#   seem like a very useful test.
# def test_cdl_crop_types():
# #     # CDL codes in data file:
# #     assert set(data.cdl.keys()) == set([
# #         1, 2, 3, 4, 5, 6, 12, 14, 21, 23, 24, 27, 28, 29, 31, 32, 33, 36,
# #         41, 42, 43, 46, 48, 49, 51, 52, 53, 54, 58,
# #         66, 67, 68, 69, 72, 75, 76, 77, 141, 142,
# #         204, 206, 207, 208, 209, 211, 212, 214, 221, 222, 223, 227, 229,
# #         243, 244, 245, 246, 247, 248])
# #     # CDL codes not in data file:
# #     #   10, 11, 13, 22, 25, 26, 30, 32, 34, 35, 37, 38, 39, 44, 45, 47,
# #     #   50, 55, 56, 57, 59, 61, 70, 71, 74,
# #     #   205, 210, 213, 215, 216, 217, 218, 219, 220, 224, 225, 226,
# #     #   230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
# #     #   240, 241, 242, 249, 250, 254


@pytest.mark.parametrize('param', ['crop_class', 'h_max', 'm_l', 'fr_mid'])
def test_cdl_parameters(param):
    # Check that all default parameter keys have a value
    # Crops without a key will use general Kc equation
    # CGM - This test isn't very informative about which crop is the problem
    assert all(crop_data[param] for crop_data in data.cdl.values()
               if param in crop_data.keys())


@pytest.mark.parametrize('param', ['fr_end', 'ls_start', 'ls_stop'])
def test_cdl_class3_parameters(param):
    assert all(crop_data[param] for crop_data in data.cdl.values()
               if crop_data['crop_class'] == 3 and param in crop_data.keys())


@pytest.mark.parametrize(
    'crop_type, crop_class',
    [
        [1, 1],
        [69, 2],
        [66, 3],
        [3, 5],    # Rice was switched to class 5 instead of 1
        [61, 6],   # Fallow was switched to class 6 instead of 1
        [176, 7],  # Grass/pasture was switched to class 7 instead of 1
    ]
)
def test_cdl_crop_classes(crop_type, crop_class):
    assert data.cdl[crop_type]['crop_class'] == crop_class


# CGM - How would I do this?
# def test_cdl_int_scalar_digits():
#     # Check if any values have more digits than can be handled by int_scalar
#     assert False

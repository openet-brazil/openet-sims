
import pytest

from . import data


# Check that all entries have: crop_class, h_max, m_l, fr_mid
# Check that all CDL crops are present
# Check that crop_class 3 entries have fr_end, ls_start, and lst_stop entries and values
# Check that crop 3 (rice) is a separate crop_class
# Check that h_max and m_l don't have entries with more than 2 digits past the decimal place
#   and can be scaled by 100 in the remap
# Check that int_scalar is set





# def test_make_profile():
#     output = crop_data.make_profile(crop_type=69)
#
#     # Check that the expected names are present
#     assert set(output._asdict().keys()) == set([
#         'crop_class', 'h_max', 'm_l', 'fr_mid', 'fr_end', 'ls_start', 'ls_stop'])
#
#     # Check that the values can be called by name
#     assert output.crop_class == 2
#
#
# # CGM - Would it make sense to test every value to ensure it hasn't changed?
# @pytest.mark.parametrize(
#     'crop_type, crop_class, h_max, m_l, fr_mid, fr_end, ls_start, ls_stop',
#     [
#         [69, 2, 2, 1.5, 0.95, 0.51, 205.0, 265.0],
#         # [75, 3, 4, 1.5, 0.81, 0.59, 270.0, 300.0]
#     ]
# )
# def test_make_profile(crop_type, crop_class, h_max, m_l, fr_mid, fr_end,
#                       ls_start, ls_stop):
#     # CGM - Would it be easier to build a new namedtuple from the inputs
#     #   instead of checking each term separately
#     output = crop_data.make_profile(crop_type)
#     assert output.crop_class == crop_class
#     assert output.h_max == h_max
#     assert output.m_l == m_l
#     assert output.fr_mid == fr_mid
#     assert output.fr_end == fr_end
#     assert output.ls_start == ls_start
#     assert output.ls_stop == ls_stop

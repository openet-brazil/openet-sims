from collections import namedtuple


CropProfile = namedtuple(
    'CropProfile',
    ['crop_class', 'h_max', 'm_l', 'fr_mid', 'fr_end', 'ls_start', 'ls_stop'])


# def make_profile(crop_type):
#     """Return the CropProfile for a given crop type.
#
#     Parameters
#     ----------
#     crop_type : int
#         CDL crop type value
#
#     Returns
#     -------
#     CropProfile
#         Includes various parameters for determining k_c given crop type
#
#     """
#
#     # Vine
#     if crop_type == 69: return CropProfile(2, 2, 1.5, 0.95, 0.51, 205.0, 265.0)
#
#     # Trees
#     # Using citrus coefficient for orange
#     elif crop_type == 66: return CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0)
#     elif crop_type == 67: return CropProfile(3, 3, 1.5, 1.0, 0.71, 270.0, 300.0)
#     elif crop_type == 68: return CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0)
#     elif crop_type == 72: return CropProfile(3, 2.5, 1.5, 0.71, 0.94, 270.0, 365.0)
#     elif crop_type == 75: return CropProfile(3, 4, 1.5, 0.81, 0.59, 270.0, 300.0)
#     elif crop_type == 76: return CropProfile(3, 5, 1.5, 0.9, 0.52, 250.0, 280.0)
#     elif crop_type == 77: return CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0)
#     elif crop_type == 141: return CropProfile(3, 4, 1.5, 0.88, 0.62, 270.0, 300.0)
#     elif crop_type == 142: return CropProfile(3, 3, 1.5, 0.67, 0.71, 270.0, 365.0)
#     elif crop_type == 204: return CropProfile(3, 3, 1.5, 0.81, 0.57, 200.0, 240.0)
#     elif crop_type == 211: return CropProfile(3, 4, 1.5, 0.48, 0.46, 240, 330.0)
#     elif crop_type == 212: return CropProfile(3, 2.5, 1.5, 0.71, 0.94, 270.0, 365.0)
#     elif crop_type == 223: return CropProfile(3, 3, 1.5, 1.0, 0.71, 270.0, 300.0)
#
#     # Field crops
#     elif crop_type == 49: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 206: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 208: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 214: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 227: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 243: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 244: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 245: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 246: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#
#     # Veg, solanum family
#     elif crop_type == 54: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 248: return CropProfile(1, 0.8, 2, 1, -9999, -9999, -9999)
#
#     # Veg, cucurb family
#     elif crop_type == 48: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 209: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 222: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 228: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 229: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
#
#     # Roots & tubers
#     elif crop_type == 41: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 43: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 46: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 247: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
#
#     # Legumes
#     elif crop_type == 5: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 42: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 51: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 52: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 53: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
#
#     # Perennial veg
#     elif crop_type == 14: return CropProfile(1, 0.7, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 207: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 221: return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999)
#
#     # Fiber
#     elif crop_type == 2: return CropProfile(1, 1.35, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 6: return CropProfile(1, 2, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 31: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 32: return CropProfile(1, 1.2, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 33: return CropProfile(1, 0.8, 2, 1, -9999, -9999, -9999)
#
#     # Cereal
#     elif crop_type == 1: return CropProfile(1, 2, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 3: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 4: return CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 12: return CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 21: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 23: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 24: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 28: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 29: return CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999)
#
#     # Forage
#     elif crop_type == 27: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 36: return CropProfile(1, 0.7, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 58: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
#     elif crop_type == 62: return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999)
#
#     # Duplicating grazing pasture as pasture/hay
#     elif crop_type == 181: return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999)
#     # Duplicating Other Hay/Non Alfalfa as pasture/hay
#     #elif crop_type ==  37:   return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999)
#
#     # CGM - Should these be -9999 instead of -999?
#     else: return CropProfile(-999, -999, -999, -999, -999, -999, -999)



int_scalar = 100


# CGM - Trying out a more generic data structure
# This could be stored/read from a CSV file instead
# TODO: Add the name property to each entry
# TODO: Unpack this master data dictionary into separate dictionaries for each param?
cdl = {
    # Grapes / vines
    69:  {'crop_class': 2, 'h_max': 2, 'm_l': 1.5, 'fr_mid': 0.95, 'fr_end': 0.51,
          'ls_start': 205.0, 'ls_stop': 265.0, 'name': 'Grapes'},

    # Trees
    # Using citrus coefficient for orange
    66:  {'crop_class': 3, 'h_max': 3, 'm_l': 2, 'fr_mid': 0.95, 'fr_end': 0.75,
          'ls_start': 270.0, 'ls_stop': 300.0},
    67:  {'crop_class': 3, 'h_max': 3, 'm_l': 1.5, 'fr_mid': 1.0, 'fr_end': 0.71,
          'ls_start': 270.0, 'ls_stop': 300.0},
    68:  {'crop_class': 3, 'h_max': 3, 'm_l': 2, 'fr_mid': 0.95, 'fr_end': 0.75,
          'ls_start': 270.0, 'ls_stop': 300.0},
    72:  {'crop_class': 3, 'h_max': 2.5, 'm_l': 1.5, 'fr_mid': 0.71, 'fr_end': 0.94,
          'ls_start': 270.0, 'ls_stop': 365.0},
    75:  {'crop_class': 3, 'h_max': 4, 'm_l': 1.5, 'fr_mid': 0.81, 'fr_end': 0.59,
          'ls_start': 270.0, 'ls_stop': 300.0},
    76:  {'crop_class': 3, 'h_max': 5, 'm_l': 1.5, 'fr_mid': 0.9, 'fr_end': 0.52,
          'ls_start': 250.0, 'ls_stop': 280.0},
    77:  {'crop_class': 3, 'h_max': 3, 'm_l': 2, 'fr_mid': 0.95, 'fr_end': 0.75,
          'ls_start': 270.0, 'ls_stop': 300.0},
    141: {'crop_class': 3, 'h_max': 4, 'm_l': 1.5, 'fr_mid': 0.88, 'fr_end': 0.62,
          'ls_start': 270.0, 'ls_stop': 300.0},
    142: {'crop_class': 3, 'h_max': 3, 'm_l': 1.5, 'fr_mid': 0.67, 'fr_end': 0.71,
          'ls_start': 270.0, 'ls_stop': 365.0},
    204: {'crop_class': 3, 'h_max': 3, 'm_l': 1.5, 'fr_mid': 0.81, 'fr_end': 0.57,
          'ls_start': 200.0, 'ls_stop': 240.0},
    211: {'crop_class': 3, 'h_max': 4, 'm_l': 1.5, 'fr_mid': 0.48, 'fr_end': 0.46,
          'ls_start': 240.0, 'ls_stop': 330.0},
    212: {'crop_class': 3, 'h_max': 2.5, 'm_l': 1.5, 'fr_mid': 0.71, 'fr_end': 0.94,
          'ls_start': 270.0, 'ls_stop': 365.0},
    223: {'crop_class': 3, 'h_max': 3, 'm_l': 1.5, 'fr_mid': 1.0, 'fr_end': 0.71,
          'ls_start': 270.0, 'ls_stop': 300.0},

    # Field crops
    49:  {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1},
    206: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},
    208: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},
    214: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},
    227: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},
    243: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1},
    244: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1},
    245: {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1},
    246: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},

    # Veg, solanum family
    54:  {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1},
    248: {'crop_class': 1, 'h_max': 0.8, 'm_l': 2, 'fr_mid': 1},

    # Veg, cucurb family
    48:  {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1},
    209: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},
    222: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},
    228: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},
    229: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1},

    # Roots & tubers
    41:  {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1},
    43:  {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1},
    46:  {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1},
    247: {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1},

    # Legumes
    5:  {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1},
    42: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1},
    51: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1},
    52: {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1},
    53: {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1},

    # Perennial vegetables
    14:  {'crop_class': 1, 'h_max': 0.7, 'm_l': 2, 'fr_mid': 1},
    207: {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1},
    221: {'crop_class': 1, 'h_max': 0.2, 'm_l': 2, 'fr_mid': 1},

    # Fiber
    2:  {'crop_class': 1, 'h_max': 1.35, 'm_l': 2, 'fr_mid': 1},
    6:  {'crop_class': 1, 'h_max': 2.0, 'm_l': 2, 'fr_mid': 1},
    31: {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1},
    32: {'crop_class': 1, 'h_max': 1.2, 'm_l': 2, 'fr_mid': 1},
    33: {'crop_class': 1, 'h_max': 0.8, 'm_l': 2, 'fr_mid': 1},

    # Cereal
    1:  {'crop_class': 1, 'h_max': 2.0, 'm_l': 2, 'fr_mid': 1},
    # DEADBEEF - Should this be clop_class 5?
    3:  {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1},
    4:  {'crop_class': 1, 'h_max': 1.5, 'm_l': 2, 'fr_mid': 1},
    12: {'crop_class': 1, 'h_max': 1.5, 'm_l': 2, 'fr_mid': 1},
    21: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1},
    23: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1},
    24: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1},
    28: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1},
    29: {'crop_class': 1, 'h_max': 1.5, 'm_l': 2, 'fr_mid': 1},

    # Forage
    27: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1},
    36: {'crop_class': 1, 'h_max': 0.7, 'm_l': 2, 'fr_mid': 1},
    58: {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1},
    62: {'crop_class': 1, 'h_max': 0.2, 'm_l': 2, 'fr_mid': 1},

    # Duplicating grazing pasture as pasture/hay
    181: {'crop_class': 1, 'h_max': 0.2, 'm_l': 2, 'fr_mid': 1},
    # Duplicating Other Hay/Non Alfalfa as pasture/hay
    #37: {'crop_class': 1, 'h_max': 0.2, 'm_l': 2, 'fr_mid': 1}),
}

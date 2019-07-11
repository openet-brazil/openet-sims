from collections import namedtuple


CropProfile = namedtuple(
    'CropProfile',
    ['crop_class', 'h_max', 'm_l', 'fr_mid', 'fr_end', 'ls_start', 'ls_stop'])


def make_profile(crop_type):
    """Return the CropProfile for a given crop type.

    Parameters
    ----------
    crop_type : int
        CDL crop type value

    Returns
    -------
    CropProfile
        Includes various parameters for determining k_c given crop type

    """
 
    # Vine
    if crop_type == 69: return CropProfile(2, 2, 1.5, 0.95, 0.51, 205.0, 265.0)
        
    # Trees
    # Using citrus coefficient for orange
    elif crop_type == 66: return CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0)
    elif crop_type == 67: return CropProfile(3, 3, 1.5, 1.0, 0.71, 270.0, 300.0)
    elif crop_type == 68: return CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0)
    elif crop_type == 72: return CropProfile(3, 2.5, 1.5, 0.71, 0.94, 270.0, 365.0)
    elif crop_type == 75: return CropProfile(3, 4, 1.5, 0.81, 0.59, 270.0, 300.0)
    elif crop_type == 76: return CropProfile(3, 5, 1.5, 0.9, 0.52, 250.0, 280.0)
    elif crop_type == 77: return CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0)
    elif crop_type == 141: return CropProfile(3, 4, 1.5, 0.88, 0.62, 270.0, 300.0)
    elif crop_type == 142: return CropProfile(3, 3, 1.5, 0.67, 0.71, 270.0, 365.0)
    elif crop_type == 204: return CropProfile(3, 3, 1.5, 0.81, 0.57, 200.0, 240.0)
    elif crop_type == 211: return CropProfile(3, 4, 1.5, 0.48, 0.46, 240, 330.0)
    elif crop_type == 212: return CropProfile(3, 2.5, 1.5, 0.71, 0.94, 270.0, 365.0)
    elif crop_type == 223: return CropProfile(3, 3, 1.5, 1.0, 0.71, 270.0, 300.0)

    # Field crops
    elif crop_type == 49: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
    elif crop_type == 206: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
    elif crop_type == 208: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
    elif crop_type == 214: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
    elif crop_type == 227: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
    elif crop_type == 243: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
    elif crop_type == 244: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
    elif crop_type == 245: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
    elif crop_type == 246: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)

    # Veg, solanum family
    elif crop_type == 54: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
    elif crop_type == 248: return CropProfile(1, 0.8, 2, 1, -9999, -9999, -9999)

    # Veg, cucurb family
    elif crop_type == 48: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
    elif crop_type == 209: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
    elif crop_type == 222: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
    elif crop_type == 228: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
    elif crop_type == 229: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)

    # Roots & tubers
    elif crop_type == 41: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
    elif crop_type == 43: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
    elif crop_type == 46: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
    elif crop_type == 247: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)

    # Legumes
    elif crop_type == 5: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
    elif crop_type == 42: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
    elif crop_type == 51: return CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999)
    elif crop_type == 52: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
    elif crop_type == 53: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)

    # Perennial veg
    elif crop_type == 14: return CropProfile(1, 0.7, 2, 1, -9999, -9999, -9999)
    elif crop_type == 207: return CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999)
    elif crop_type == 221: return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999)

    # Fiber
    elif crop_type == 2: return CropProfile(1, 1.35, 2, 1, -9999, -9999, -9999)
    elif crop_type == 6: return CropProfile(1, 2, 2, 1, -9999, -9999, -9999)
    elif crop_type == 31: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
    elif crop_type == 32: return CropProfile(1, 1.2, 2, 1, -9999, -9999, -9999)
    elif crop_type == 33: return CropProfile(1, 0.8, 2, 1, -9999, -9999, -9999)

    # Cereal
    elif crop_type == 1: return CropProfile(1, 2, 2, 1, -9999, -9999, -9999)
    elif crop_type == 3: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
    elif crop_type == 4: return CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999)
    elif crop_type == 12: return CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999)
    elif crop_type == 21: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
    elif crop_type == 23: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
    elif crop_type == 24: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
    elif crop_type == 28: return CropProfile(1, 1, 2, 1, -9999, -9999, -9999)
    elif crop_type == 29: return CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999)

    # Forage
    elif crop_type == 27: return CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999)
    elif crop_type == 36: return CropProfile(1, 0.7, 2, 1, -9999, -9999, -9999)
    elif crop_type == 58: return CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999)
    elif crop_type == 62: return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999)

    # Duplicating grazing pasture as pasture/hay
    elif crop_type == 181: return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999)
    # Duplicating Other Hay/Non Alfalfa as pasture/hay
    #elif crop_type ==  37:   return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999)

    # CGM - Should these be -9999 instead of -999?
    else: return CropProfile(-999, -999, -999, -999, -999, -999, -999)



# CGM - What about a more generic structure for this data
# This could be stored/read from a CSV file instead
crop_data = {
    # 69: {'crop_class': 2, 'h_max': 2, 'm_l': 1.5, 'fr_mid': 0.95,
    #      'fr_end': 0.51, 'ls_start': 205.0, 'ls_stop': 265.0,
    #      'name': 'Grapes'},

    # Vines (grapes)
    69: CropProfile(2, 2, 1.5, 0.95, 0.51, 205.0, 265.0),

    # Trees
    # Using citrus coefficient for orange
    66: CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0),
    67: CropProfile(3, 3, 1.5, 1.0, 0.71, 270.0, 300.0),
    68: CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0),
    72: CropProfile(3, 2.5, 1.5, 0.71, 0.94, 270.0, 365.0),
    75: CropProfile(3, 4, 1.5, 0.81, 0.59, 270.0, 300.0),
    76: CropProfile(3, 5, 1.5, 0.9, 0.52, 250.0, 280.0),
    77: CropProfile(3, 3, 2, 0.95, 0.75, 270.0, 300.0),
    141: CropProfile(3, 4, 1.5, 0.88, 0.62, 270.0, 300.0),
    142: CropProfile(3, 3, 1.5, 0.67, 0.71, 270.0, 365.0),
    204: CropProfile(3, 3, 1.5, 0.81, 0.57, 200.0, 240.0),
    211: CropProfile(3, 4, 1.5, 0.48, 0.46, 240, 330.0),
    212: CropProfile(3, 2.5, 1.5, 0.71, 0.94, 270.0, 365.0),
    223: CropProfile(3, 3, 1.5, 1.0, 0.71, 270.0, 300.0),

    # Field crops
    49: CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999),
    206: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),
    208: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),
    214: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),
    227: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),
    243: CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999),
    244: CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999),
    245: CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999),
    246: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),

    # Veg, solanum family
    54: CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999),
    248: CropProfile(1, 0.8, 2, 1, -9999, -9999, -9999),

    # Veg, cucurb family
    48: CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999),
    209: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),
    222: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),
    228: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),
    229: CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999),

    # Roots & tubers
    41: CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999),
    43: CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999),
    46: CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999),
    247: CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999),

    # Legumes
    5: CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999),
    42: CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999),
    51: CropProfile(1, 0.4, 2, 1, -9999, -9999, -9999),
    52: CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999),
    53: CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999),

    # Perennial veg
    14: CropProfile(1, 0.7, 2, 1, -9999, -9999, -9999),
    207: CropProfile(1, 0.5, 2, 1, -9999, -9999, -9999),
    221: CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999),

    # Fiber
    2: CropProfile(1, 1.35, 2, 1, -9999, -9999, -9999),
    6: CropProfile(1, 2, 2, 1, -9999, -9999, -9999),
    31: CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999),
    32: CropProfile(1, 1.2, 2, 1, -9999, -9999, -9999),
    33: CropProfile(1, 0.8, 2, 1, -9999, -9999, -9999),

    # Cereal
    1: CropProfile(1, 2, 2, 1, -9999, -9999, -9999),
    3: CropProfile(1, 1, 2, 1, -9999, -9999, -9999),
    4: CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999),
    12: CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999),
    21: CropProfile(1, 1, 2, 1, -9999, -9999, -9999),
    23: CropProfile(1, 1, 2, 1, -9999, -9999, -9999),
    24: CropProfile(1, 1, 2, 1, -9999, -9999, -9999),
    28: CropProfile(1, 1, 2, 1, -9999, -9999, -9999),
    29: CropProfile(1, 1.5, 2, 1, -9999, -9999, -9999),

    # Forage
    27: CropProfile(1, 0.3, 2, 1, -9999, -9999, -9999),
    36: CropProfile(1, 0.7, 2, 1, -9999, -9999, -9999),
    58: CropProfile(1, 0.6, 2, 1, -9999, -9999, -9999),
    62: CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999),

    # Duplicating grazing pasture as pasture/hay
    181: CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999),
    # Duplicating Other Hay/Non Alfalfa as pasture/hay
    #37: return CropProfile(1, 0.2, 2, 1, -9999, -9999, -9999),

    # CGM - Should these be -9999 instead of -999?
    # else: return CropProfile(-999, -999, -999, -999, -999, -999, -999)

}

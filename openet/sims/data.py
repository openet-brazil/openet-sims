int_scalar = 100

# CGM - Trying out a more generic data structure
# This could be stored/read from a CSV file instead
# TODO: Add the name property to each entry
# TODO: Unpack this master data dictionary into separate dictionaries for each param?
cdl = {
    # Grapes / vines
    69:  {'crop_class': 2, 'h_max': 2, 'm_l': 1.5, 'fr_mid': 0.95,
          'fr_end': 0.51, 'ls_start': 205.0, 'ls_stop': 265.0,
          'name': 'Grapes'},

    # Trees
    66:  {'crop_class': 3, 'h_max': 3, 'm_l': 2, 'fr_mid': 0.95,
          'fr_end': 0.75, 'ls_start': 270.0, 'ls_stop': 300.0,
          'name': 'Cherries'},
    67:  {'crop_class': 3, 'h_max': 3, 'm_l': 1.5, 'fr_mid': 1.0,
          'fr_end': 0.71, 'ls_start': 270.0, 'ls_stop': 300.0,
          'name': 'Peaches'},
    68:  {'crop_class': 3, 'h_max': 3, 'm_l': 2, 'fr_mid': 0.95,
          'fr_end': 0.75, 'ls_start': 270.0, 'ls_stop': 300.0,
          'name': 'Apples'},
    72:  {'crop_class': 3, 'h_max': 2.5, 'm_l': 1.5, 'fr_mid': 0.71,
          'fr_end': 0.94, 'ls_start': 270.0, 'ls_stop': 365.0,
          'name': 'Citrus'},
    75:  {'crop_class': 3, 'h_max': 4, 'm_l': 1.5, 'fr_mid': 0.81,
          'fr_end': 0.59, 'ls_start': 270.0, 'ls_stop': 300.0,
          'name': 'Almonds'},
    76:  {'crop_class': 3, 'h_max': 5, 'm_l': 1.5, 'fr_mid': 0.9,
          'fr_end': 0.52, 'ls_start': 250.0, 'ls_stop': 280.0,
          'name': 'Walnuts'},
    77:  {'crop_class': 3, 'h_max': 3, 'm_l': 2, 'fr_mid': 0.95,
          'fr_end': 0.75, 'ls_start': 270.0, 'ls_stop': 300.0,
          'name': 'Pears'},
    204: {'crop_class': 3, 'h_max': 3, 'm_l': 1.5, 'fr_mid': 0.81,
          'fr_end': 0.57, 'ls_start': 200.0, 'ls_stop': 240.0,
          'name': 'Pistachios'},
    211: {'crop_class': 3, 'h_max': 4, 'm_l': 1.5, 'fr_mid': 0.48,
          'fr_end': 0.46, 'ls_start': 240.0, 'ls_stop': 330.0,
          'name': 'Olives'},
    # Using citrus coefficient for orange
    212: {'crop_class': 3, 'h_max': 2.5, 'm_l': 1.5, 'fr_mid': 0.71,
          'fr_end': 0.94, 'ls_start': 270.0, 'ls_stop': 365.0,
          'name': 'Oranges'},
    223: {'crop_class': 3, 'h_max': 3, 'm_l': 1.5, 'fr_mid': 1.0,
          'fr_end': 0.71, 'ls_start': 270.0, 'ls_stop': 300.0,
          'name': 'Honeydew Melons'},
    # CGM - Should SIMS be computed for all NLCD forest pixels?
    141: {'crop_class': 3, 'h_max': 4, 'm_l': 1.5, 'fr_mid': 0.88,
          'fr_end': 0.62, 'ls_start': 270.0, 'ls_stop': 300.0,
          'name': 'Deciduous Forest'},
    142: {'crop_class': 3, 'h_max': 3, 'm_l': 1.5, 'fr_mid': 0.67,
          'fr_end': 0.71, 'ls_start': 270.0, 'ls_stop': 365.0,
          'name': 'Evergreen Forest'},
    # Tree crops without custom coefficients
    70: {'crop_class': 3, 'name': 'Christmas Trees'},
    71: {'crop_class': 3, 'name': 'Other Tree Crops'},
    74: {'crop_class': 3, 'name': 'Pecans'},
    210: {'crop_class': 3, 'name': 'Prunes'},
    # CGM - There are no Avocado pixels in the 2015-2018 CDL
    # 215: {'crop_class': 3, 'name': 'Avocados'},
    217: {'crop_class': 3, 'name': 'Pomegranates'},
    218: {'crop_class': 3, 'name': 'Nectarines'},
    220: {'crop_class': 3, 'name': 'Plums'},

    # Field crops
    49:  {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1, 'name': 'Onions'},
    206: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Carrots'},
    208: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Garlic'},
    214: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Broccoli'},
    227: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Lettuce'},
    243: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1, 'name': 'Cabbage'},
    244: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1, 'name': 'Cauliflower'},
    245: {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1, 'name': 'Celery'},
    246: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Radishes'},

    # Veg, solanum family
    54:  {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1, 'name': 'Tomatoes'},
    248: {'crop_class': 1, 'h_max': 0.8, 'm_l': 2, 'fr_mid': 1, 'name': 'Eggplants'},

    # Veg, cucurb family
    48:  {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1, 'name': 'Watermelons'},
    209: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Cantaloupes'},
    222: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Squash'},
    # CGM - 228 is not a valid CDL code, changed to 227
    227: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Lettuce'},
    229: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1, 'name': 'Pumpkins'},

    # Roots & tubers
    41:  {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1, 'name': 'Sugarbeets'},
    43:  {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1, 'name': 'Potatoes'},
    46:  {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1, 'name': 'Sweet Potatoes'},
    247: {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1, 'name': 'Turnips'},

    # Legumes
    5:  {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1, 'name': 'Soybeans'},
    42: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1, 'name': 'Dry Beans'},
    51: {'crop_class': 1, 'h_max': 0.4, 'm_l': 2, 'fr_mid': 1, 'name': 'Chick Peas'},
    52: {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1, 'name': 'Lentils'},
    53: {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1, 'name': 'Peas'},

    # Perennial vegetables
    14:  {'crop_class': 1, 'h_max': 0.7, 'm_l': 2, 'fr_mid': 1, 'name': 'Mint'},
    207: {'crop_class': 1, 'h_max': 0.5, 'm_l': 2, 'fr_mid': 1, 'name': 'Asparagus'},
    221: {'crop_class': 1, 'h_max': 0.2, 'm_l': 2, 'fr_mid': 1, 'name': 'Strawberries'},

    # Fiber
    2:  {'crop_class': 1, 'h_max': 1.35, 'm_l': 2, 'fr_mid': 1, 'name': 'Cotton'},
    6:  {'crop_class': 1, 'h_max': 2.0, 'm_l': 2, 'fr_mid': 1, 'name': 'Sunflower'},
    31: {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1, 'name': 'Canola'},
    32: {'crop_class': 1, 'h_max': 1.2, 'm_l': 2, 'fr_mid': 1, 'name': 'Flaxseed'},
    33: {'crop_class': 1, 'h_max': 0.8, 'm_l': 2, 'fr_mid': 1, 'name': 'Safflower'},

    # Cereal
    1:  {'crop_class': 1, 'h_max': 2.0, 'm_l': 2, 'fr_mid': 1, 'name': 'Corn'},
    4:  {'crop_class': 1, 'h_max': 1.5, 'm_l': 2, 'fr_mid': 1, 'name': 'Sorghum'},
    12: {'crop_class': 1, 'h_max': 1.5, 'm_l': 2, 'fr_mid': 1, 'name': 'Sweet Corn'},
    21: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1, 'name': 'Barley'},
    23: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1, 'name': 'Spring Wheat'},
    24: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1, 'name': 'Winter Wheat'},
    28: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1, 'name': 'Oats'},
    29: {'crop_class': 1, 'h_max': 1.5, 'm_l': 2, 'fr_mid': 1, 'name': 'Millet'},

    # Rice
    # CGM - Should this be clop_class 5 instead?
    3: {'crop_class': 1, 'h_max': 1.0, 'm_l': 2, 'fr_mid': 1, 'name': 'Rice'},

    # Forage
    27: {'crop_class': 1, 'h_max': 0.3, 'm_l': 2, 'fr_mid': 1, 'name': 'Rye'},
    36: {'crop_class': 1, 'h_max': 0.7, 'm_l': 2, 'fr_mid': 1, 'name': 'Alfalfa'},
    58: {'crop_class': 1, 'h_max': 0.6, 'm_l': 2, 'fr_mid': 1,
         'name': 'Clover/Wildflowers'},
    # CGM - 62 is not a valid CDL code, should this be 61?
    #   If this is changed, make sure to comment out entry for 61 below
    # 62: {'crop_class': 1, 'h_max': 0.2, 'm_l': 2, 'fr_mid': 1, 'name': ''},

    # Duplicating grazing pasture as pasture/hay
    # 181: {'crop_class': 1, 'h_max': 0.2, 'm_l': 2, 'fr_mid': 1, 'name': },
    # Duplicating Other Hay/Non Alfalfa as pasture/hay
    # 37: {'crop_class': 1, 'h_max': 0.2, 'm_l': 2, 'fr_mid': 1, 'name': }),

    # Crops without custom coefficients
    10: {'crop_class': 1, 'name': 'Peanuts'},
    11: {'crop_class': 1, 'name': 'Tobacco'},
    13: {'crop_class': 1, 'name': 'Pop or Orn Corn'},
    22: {'crop_class': 1, 'name': 'Durum Wheat'},
    25: {'crop_class': 1, 'name': 'Other Small Grains'},
    26: {'crop_class': 1, 'name': 'Dbl Crop WinWht/Soybeans'},
    30: {'crop_class': 1, 'name': 'Speltz'},
    32: {'crop_class': 1, 'name': 'Flaxseed'},
    34: {'crop_class': 1, 'name': 'Rape Seed'},
    35: {'crop_class': 1, 'name': 'Mustard'},
    37: {'crop_class': 1, 'name': 'Other Hay/Non Alfalfa'},
    38: {'crop_class': 1, 'name': 'Camelina'},
    39: {'crop_class': 1, 'name': 'Buckwheat'},
    44: {'crop_class': 1, 'name': 'Other Crops'},
    45: {'crop_class': 1, 'name': 'Sugarcane'},
    47: {'crop_class': 1, 'name': 'Misc Vegs & Fruits'},
    50: {'crop_class': 1, 'name': 'Cucumbers'},
    55: {'crop_class': 1, 'name': 'Caneberries'},
    56: {'crop_class': 1, 'name': 'Hops'},
    57: {'crop_class': 1, 'name': 'Herbs'},
    59: {'crop_class': 1, 'name': 'Sod/Grass Seed'},
    61: {'crop_class': 1, 'name': 'Fallow/Idle Cropland'},
    205: {'crop_class': 1, 'name': 'Triticale'},
    213: {'crop_class': 1, 'name': 'Honeydew Melons'},
    216: {'crop_class': 1, 'name': 'Peppers'},
    219: {'crop_class': 1, 'name': 'Greens'},
    224: {'crop_class': 1, 'name': 'Vetch'},
    225: {'crop_class': 1, 'name': 'Dbl Crop WinWht/Corn'},
    226: {'crop_class': 1, 'name': 'Dbl Crop Oats/Corn'},
    230: {'crop_class': 1, 'name': 'Dbl Crop Lettuce/Durum Wht'},
    231: {'crop_class': 1, 'name': 'Dbl Crop Lettuce/Cantaloupe'},
    232: {'crop_class': 1, 'name': 'Dbl Crop Lettuce/Cotton'},
    233: {'crop_class': 1, 'name': 'Dbl Crop Lettuce/Barley'},
    234: {'crop_class': 1, 'name': 'Dbl Crop Durum Wht/Sorghum'},
    235: {'crop_class': 1, 'name': 'Dbl Crop Barley/Sorghum'},
    236: {'crop_class': 1, 'name': 'Dbl Crop WinWht/Sorghum'},
    237: {'crop_class': 1, 'name': 'Dbl Crop Barley/Corn'},
    238: {'crop_class': 1, 'name': 'Dbl Crop WinWht/Cotton'},
    239: {'crop_class': 1, 'name': 'Dbl Crop Soybeans/Cotton'},
    240: {'crop_class': 1, 'name': 'Dbl Crop Soybeans/Oats'},
    241: {'crop_class': 1, 'name': 'Dbl Crop Corn/Soybeans'},
    242: {'crop_class': 1, 'name': 'Blueberries'},
    249: {'crop_class': 1, 'name': 'Gourds'},
    250: {'crop_class': 1, 'name': 'Cranberries'},
    254: {'crop_class': 1, 'name': 'Dbl Crop Barley/Soybeans'},
}

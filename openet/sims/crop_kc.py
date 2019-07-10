from collections import namedtuple

import ee


CropProfile = namedtuple(
    'CropProfile',
    ['crop_class', 'h_max', 'm_l', 'fr_mid', 'fr_end', 'ls_start', 'ls_stop'])


def make_profile(classVal):
    """Return the CropProfile for a given crop type.

    Parameters
    ----------
    classVal : int
        CDL crop type value

    Returns
    -------
    CropProfile
        Includes various parameters for determining k_c given crop type

    """
 
    # Vine
    if classVal ==  69:   return CropProfile(2,2,1.5,0.95,0.51,205.0,265.0)
        
    # Trees
    elif classVal ==  75:   return CropProfile(3,4,1.5,0.81,0.59,270.0,300.0)
    elif classVal ==  68:   return CropProfile(3,3,2,0.95,0.75,270.0,300.0)
    elif classVal ==  77:   return CropProfile(3,3,2,0.95,0.75,270.0,300.0)
    elif classVal ==  66:   return CropProfile(3,3,2,0.95,0.75,270.0,300.0)
    elif classVal ==  223:   return CropProfile(3,3,1.5,1.0,0.71,270.0,300.0)
    elif classVal ==  67:   return CropProfile(3,3,1.5,1.0,0.71,270.0,300.0)
    # Using same coeff as citrus for orange
    elif classVal ==  212:   return CropProfile(3,2.5,1.5,0.71,0.94,270.0,365.0)
    elif classVal ==  72:   return CropProfile(3,2.5,1.5,0.71,0.94,270,365.0)
    elif classVal ==  211:   return CropProfile(3,4,1.5,0.48,0.46,240,330.0)
    elif classVal ==  204:   return CropProfile(3,3,1.5,0.81,0.57,200.0,240.0)
    elif classVal ==  76:   return CropProfile(3,5,1.5,0.9,0.52,250,280.0)
    elif classVal ==  141:   return CropProfile(3,4,1.5,0.88,0.62,270,300.0)
    elif classVal ==  142:   return CropProfile(3,3,1.5,0.67,0.71,270,365.0)

    # Field crops
    elif classVal ==  214:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  243:   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  206:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    elif classVal ==  244:   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  245:   return CropProfile(1,0.6,2,1,-9999,-9999,-9999)
    elif classVal ==  208:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    elif classVal ==  227:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    elif classVal ==  49:   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.5,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    elif classVal ==  246:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.37,2,1,-9999,-9999,-9999)

    # Veg, solanum family
    elif classVal ==  248:   return CropProfile(1,0.8,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.7,2,1,-9999,-9999,-9999)
    elif classVal ==  54:   return CropProfile(1,0.6,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.7,2,1,-9999,-9999,-9999)

    # Veg, cucurb family
    elif classVal ==  209:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    elif classVal ==  228:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    elif classVal ==  229:   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  222:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  48:   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.35,2,1,-9999,-9999,-9999)

    # Roots & tubers
    #elif classVal ==  :   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,1,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,1.5,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  43:   return CropProfile(1,0.6,2,1,-9999,-9999,-9999)
    elif classVal ==  46:   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  247:   return CropProfile(1,0.6,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.6,2,1,-9999,-9999,-9999)
    elif classVal ==  41:   return CropProfile(1,0.5,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.675,2,1,-9999,-9999,-9999)

    # Legumes
    #elif classVal ==  :   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  42:   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  51:   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.8,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.8,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.4,2,1,-9999,-9999,-9999)
    elif classVal ==  52:   return CropProfile(1,0.5,2,1,-9999,-9999,-9999)
    elif classVal ==  53:   return CropProfile(1,0.5,2,1,-9999,-9999,-9999)
    elif classVal ==  5:   return CropProfile(1,0.5,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.51,2,1,-9999,-9999,-9999)

    # Perennial veg
    #elif classVal ==  :   return CropProfile(1,0.7,2,1,-9999,-9999,-9999)
    elif classVal ==  207:   return CropProfile(1,0.5,2,1,-9999,-9999,-9999)
    elif classVal ==  14:   return CropProfile(1,0.7,2,1,-9999,-9999,-9999)
    elif classVal ==  221:   return CropProfile(1,0.2,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.525,2,1,-9999,-9999,-9999)

    # Fiber
    elif classVal ==  2:   return CropProfile(1,1.35,2,1,-9999,-9999,-9999)
    elif classVal ==  32:   return CropProfile(1,1.2,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,1.5,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,1.35,2,1,-9999,-9999,-9999)
    #   [1,'oil',,2,1,-9999,-9999,-9999
    #elif classVal ==  :   return CropProfile(1,apeseed',0.6,2,1,-9999,-9999,-9999)
    elif classVal ==  31:   return CropProfile(1,0.6,2,1,-9999,-9999,-9999)
    elif classVal ==  33:   return CropProfile(1,0.8,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,1,2,1,-9999,-9999,-9999)
    elif classVal ==  6:   return CropProfile(1,2,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.94,2,1,-9999,-9999,-9999)

    # Cereal
    elif classVal ==  21:   return CropProfile(1,1,2,1,-9999,-9999,-9999)
    elif classVal ==  28:   return CropProfile(1,1,2,1,-9999,-9999,-9999)
    elif classVal ==  23:   return CropProfile(1,1,2,1,-9999,-9999,-9999)
    elif classVal ==  24:   return CropProfile(1,1,2,1,-9999,-9999,-9999)
    elif classVal ==  1:   return CropProfile(1,2,2,1,-9999,-9999,-9999)
    elif classVal ==  12:   return CropProfile(1,1.5,2,1,-9999,-9999,-9999)
    elif classVal ==  29:   return CropProfile(1,1.5,2,1,-9999,-9999,-9999)
    elif classVal ==  4:   return CropProfile(1,1.5,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,3,2,1,-9999,-9999,-9999)
    elif classVal ==  3:   return CropProfile(1,1,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,1.45,2,1,-9999,-9999,-9999)

    # Forage
    elif classVal ==  36:   return CropProfile(1,0.7,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.35,2,1,-9999,-9999,-9999)
    elif classVal ==  58:   return CropProfile(1,0.6,2,1,-9999,-9999,-9999)
    elif classVal ==  27:   return CropProfile(1,0.3,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,1.2,2,1,-9999,-9999,-9999)
    elif classVal ==  62:   return CropProfile(1,0.2,2,1,-9999,-9999,-9999)

    # Duplicating grazing pasture as pasture/hay
    elif classVal ==  181:   return CropProfile(1,0.2,2,1,-9999,-9999,-9999)
    # Duplicating Other Hay/Non Alfalfa as pasture/hay
    #elif classVal ==  37:   return CropProfile(1,0.2,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.1,2,1,-9999,-9999,-9999)
    #elif classVal ==  :   return CropProfile(1,0.49,2,1,-9999,-9999,-9999)

    # CGM - Should these be -9999 instead of -999?
    else: return CropProfile(-999,-999,-999,-999,-999,-999,-999)


def make_kcb_full(doy, crop_prof):
    """Basal crop coefficient (Kcb) for a given crop on day-of-year.

    Parameters
    ----------
    doy : int
    crop_prof : CropProfile

    Returns
    -------
    ee.Number

    """
    return ee.Number(make_fr(doy, crop_prof))\
        .multiply(min(1 + 0.1 * crop_prof.h_max, 1.2))


def make_fr(doy, crop_prof):
    """Reduction factor (f_r) for adjusting Kcb of tree crops

    Estimated using a mean leaf stomatal resistance term.

    Parameters
    ----------
    doy : int
    crop_prof : CropProfile

    Returns
    -------
    ee.Number

    """
    doy_gt_ls_stop = ee.Algorithms.If(
        doy.gt(crop_prof.ls_stop), crop_prof.fr_end, 0)

    doy_geq_ls_start_and_doy_leq_ls_stop = ee.Algorithms.If(
        doy.gte(crop_prof.ls_start).And(doy.lte(crop_prof.ls_stop)),
        ee.Number(crop_prof.fr_mid)\
            .subtract(
                (doy.subtract(crop_prof.ls_start))\
                .divide(crop_prof.ls_stop - crop_prof.ls_start)\
                .multiply(crop_prof.fr_mid - crop_prof.fr_end)
            ),
        doy_gt_ls_stop)

    doy_lt_ls_start = ee.Algorithms.If(
        doy.lt(crop_prof.ls_start), crop_prof.fr_mid,
        doy_geq_ls_start_and_doy_leq_ls_stop)

    fr = ee.Algorithms.If(crop_prof.crop_class == 1, 1, doy_lt_ls_start)

    return fr

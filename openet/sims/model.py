import ee

from . import utils


def crop_type(crop_type_source, year=None):
    """Crop type

    Parameters
    ----------
    crop_type_source : int, str
        CDL image collection ID: 'USDA/NASS/CDL'
            Collection will be filtered to a single year that is closest
            to the Image year.
        CDL image ID for a specific year: 'USDA/NASS/CDL/2018'
        OpenET crop type image collection ID: 'projects/openet/crop_type'
            Collection will be mosaiced to a single image.
        Integer (will be converted to an EE constant image)
    year : ee.Number
        Year must be set if crop_type_source is the CDL collection.

    Returns
    -------
    ee.Image

    Raises
    ------
    ValueError for unsupported crop_type_sources

    """
    properties = ee.Dictionary()

    if utils.is_number(crop_type_source):
        # Interpret numbers as constant images
        # CGM - Should we use the ee_types here instead?
        #   i.e. ee.ee_types.isNumber(self.etr_source)
        crop_type_img = ee.Image.constant(crop_type_source)
        #     .rename('crop_type')
        # properties = properties.set('id', 'constant')

    elif (type(crop_type_source) is str and
          crop_type_source.upper() == 'USDA/NASS/CDL'):
        # Use the CDL image closest to the image date
        # Hardcoding the CDL year range but it could be computed dynamically
        cdl_year_min = ee.Number(2008)
        cdl_year_max = ee.Number(2018)
        # cdl_year_max = ee.Date(ee.ImageCollection('USDA/NASS/CDL')
        #     .limit(1, 'system:index', False).first()
        #     .get('system:time_start')).get('year')
        # cdl_year_max = ee.Number.parse(ee.ImageCollection('USDA/NASS/CDL')\
        #     .limit(1, 'system:index', False).first().get('system:index'))

        start_year = year.min(cdl_year_max).max(cdl_year_min)
        start_date = ee.Date.fromYMD(start_year, 1, 1)
        end_date = ee.Date.fromYMD(start_year.add(1), 1, 1)
        cdl_coll = ee.ImageCollection('USDA/NASS/CDL')\
            .filterDate(start_date, end_date)\
            .select(['cropland'])
        crop_type_img = ee.Image(cdl_coll.first())
        # pprint.pprint(crop_type_img.getInfo())
        properties = properties.set('id', crop_type_img.get('system:id'))
        # pprint.pprint(properties.getInfo())

    elif (type(crop_type_source) is str and
          crop_type_source.upper().startswith('USDA/NASS/CDL')):
        crop_type_img = ee.Image(crop_type_source)\
            .select(['cropland'])
        # pprint.pprint(crop_type_img.getInfo())
        properties = properties.set('id', crop_type_img.get('system:id'))
        # pprint.pprint(properties.getInfo())

    elif (type(crop_type_source) is str and
          crop_type_source.lower() == 'projects/openet/crop_type'):
        crop_type_img = ee.ImageCollection(crop_type_source).mosaic()
        # properties = properties.set('id', 'projects/openet/crop_type')

    # TODO: Support ee.Image and ee.ImageCollection sources
    # elif isinstance(self.crop_type_source, computedobject.ComputedObject):

    else:
        raise ValueError('unsupported crop_type_source: {}'.format(
            crop_type_source))

    # Should the image properties be set onto the image also?
    return crop_type_img.rename(['crop_type']).set(properties)


def crop_class(crop_type, crop_type_remap, crop_type_band='crop_type'):
    """Generic crop classes

    The current OpenET SIMS model only supports three generic crop classes.
    This method will map the crop type codes to the three classes.
    Currently, only CDL crop type codes are supported.

    Parameters
    ----------
    crop_type : ee.Image
    crop_type_remap : str
    crop_type_band : str

    Returns
    -------
    ee.Image

    Raises
    ------
    ValueError for unsupported crop_type_remap

    """
    if crop_type_remap.upper() == 'CDL':
        # Group the "from" values in a list for each "to" value
        remap_dict = {
            1: [1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14,
                21, 22, 23, 24, 25, 26, 27, 28, 29,
                30, 31, 32, 33, 34, 35, 36, 37, 38,
                41, 42, 43, 44, 45, 46, 47, 48, 49,
                50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 80, 182,
                202, 205, 206, 207, 208, 209, 213, 214, 216, 219,
                221, 222, 224, 225, 226, 227, 228, 229,
                230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
                240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 254],
            2: [69],
            3: [66, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77,
                201, 203, 204, 210, 211, 212, 215, 217, 218, 220, 223],
        }
    else:
        raise ValueError('unsupported crop_type_remap: "{}"'.format(
            crop_type_remap))

    remap_dict = {f: t for t, from_list in remap_dict.items() for f in from_list}
    remap_from, remap_to = zip(*sorted(remap_dict.items()))

    return crop_type.remap(remap_from, remap_to, 0, crop_type_band)\
        .rename(['crop_class'])


def fc(ndvi, fc_min=0.0, fc_max=1.0):
    """Fraction of cover (fc)

    Parameters
    ----------
    ndvi : ee.Image
    fc_min : float
    fc_max : float

    Returns
    -------
    ee.Image

    """
    return ndvi.multiply(1.26).subtract(0.18)\
        .clamp(fc_min, fc_max)\
        .rename(['fc'])


def kc(fc, crop_class):
    """Crop coefficient (Kc)

    Parameters
    ----------
    fc : ee.Image
        Band must be named "fc".
    crop_class : ee.Image

    Returns
    -------
    ee.Image

    Notes
    ----
    Generic Fc-Kcb conversion for:
    Annuals-
        Melton, F., L. Johnson, C. Lund, L. Pierce, A. Michaelis, S. Hiatt,
        A. Guzman, D. Adhikari, A. Purdy, C. Rosevelt, P. Votava, T. Trout,
        B. Temesgen, K. Frame, E. Sheffner, and R. Nemani, 2012.
        Satellite Irrigation Management Support with the Terrestrial
        Observation and Prediction System: An Operational Framework for
        Integration of Satellite and Surface Observations to Support
        Improvements in Agricultural Water Resource Management.
        IEEE J. Selected Topics in Applied Earth Observations & Remote Sensing
        5:1709-1721.  [FIG 2b]
    Vines-
        Williams, L. and J. Ayars, 2005.  Grapevine water use and the crop
        coefficient are linear functions of the shaded area measured beneath
        the canopy, Ag. For. Meteor 132:201-211.  [FIG 10]
    Trees-
        Ayars, J., R. Johnson, C. Phene, T. Trout, D. Clark, and R. Mead, 2003.
        Water use by drip-irrigated late-season peaches.
        Irrig. Sci. 22:187-194.  [EQN 7]

    Crop specific Fc-Kcb conversion:
        Allen, R., and L. Pereira, 2009.  Estimating crop coefficients from
        fraction of ground cover and height.  Irrig. Sci. 28:17-34.
        [EQNS 10 (Kd); 7a (Kcb_full) using tree/vine Fr vals from Table 2; 5a (Kcb)]

    """
    # I haven't implemented the crop-specific equations for this version.
    # We would first run the crop-specific before doing the generic equations
    fc_zero = fc.multiply(0)

    # Generic equation for annual crops
    # TODO: This equation should be modified to use the first band in the image
    #   or the band name should be a parameter to the function.
    img_expr = fc.expression(
        "((b('fc') ** 2) * -0.4771) + (1.4047 * b('fc')) + 0.15")
    kc1 = fc_zero.where(crop_class.eq(1), img_expr)

    # Generic equation for vines
    kc2 = fc_zero.where(crop_class.eq(2), fc.multiply(1.7))

    # Generic equation for trees
    kc3 = fc_zero.where(
        crop_class.eq(3),
        fc.multiply(1.48).add(0.007))

    # Add up all the Kcs
    kc = kc1.add(kc2).add(kc3).clamp(0, 1.25)

    # CGM - Set all non-ag cells to nodata
    #   It might make more sense to do this to crop_type or crop_class
    kc = kc.updateMask(crop_class.gt(0))

    return kc.rename(['kc'])

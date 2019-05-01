# title           : image.py
# description     : Script used to run the Earth Engine version of SIMS.
#                   This is based on the Charles Morton's openET model
#                   template(https://github.com/Open-ET/openet-ndvi-beta).
#                   This is an early version that comes without support and
#                   might change at anytime without notice
# author          : Alberto Guzman
# date            : 03-01-2017
# version         : 0.1
# usage           :
# notes           :
# python_version  : 3.2

import ee

from . import utils
import openet.core.common as common
# import utils

def lazy_property(fn):
    """Decorator that makes a property lazy-evaluated

    https://stevenloria.com/lazy-properties/
    """
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property


class Image():
    """GEE based model for computing SIMS ETcb"""

    def __init__(
            self,
            image,
            etr_source=None,
            etr_band=None,
            etr_factor=1.0,
            landcover_source='USDA/NASS/CDL',
            landcover_band='cropland',
            ):
        """Construct a SIMS model based ET Image

        Parameters
        ----------
        image : ee.Image
            Must have bands: 'ndvi'
            Must have properties: 'system:time_start', 'system:index', and
                                  'system:id'
        etr_source : str, float, optional
            Reference ET source (the default is None).
            Parameter is required if computing 'et'.
        etr_band : str, optional
            Reference ET band name (the default is None).
            Parameter is required if computing 'etr' or 'et'.
        etr_factor : float, optional
            Reference ET scaling factor (the default is 1.0).
        landcover_source : str, optional
            Landcover source (the default is CDL).  The source should be an
            Earth Engine Image ID (or ee.Image).  Currently only NLCD
            landcovers are supported.
        landcover_band : str, optional
            Landcover band (the default is None).  The source should be an
            Earth Engine Image ID (or ee.Image).  Currently only NLCD
            landcovers are supported.

        Notes
        -----
        Fc = (NDVI * 1.26) - 0.18
        Journal reference for NDVI->Fc conversion equation:
            Johnson, L. and T. Trout, 2012. Satellite NDVI assisted monitoring of
            vegetable crop evapotranspiration in California's San Joaquin Valley. REM
            Sens. 4:439-455. [EQN 1]

        Kc = Fc based on crop type
        ETcb = Kc * ETo

        """
        self.image = image

        self.etr_source = etr_source
        self.etr_band = etr_band
        self.etr_factor = etr_factor

        self.landcover_source = landcover_source
        self.landcover_band = landcover_band

        # Get system properties from the input image
        self._id = self.image.get('system:id')
        self._index = self.image.get('system:index')
        self._time_start = self.image.get('system:time_start')
        self._properties = {
            'system:index': self._index,
            'system:time_start': self._time_start,
            'image_id': self._id,
        }

        # Build date properties from the system:time_start
        self._date = ee.Date(self._time_start)
        self._year = ee.Number(self._date.get('year'))
        self._start_date = ee.Date(utils.date_to_time_0utc(self._date))
        self._end_date = self._start_date.advance(1, 'day')

    def calculate(self, variables=['et']):
        """Return a multiband image of calculated variables

        Parameters
        ----------
        variables : list

        Returns
        -------
        ee.Image

        """
        output_images = []
        for v in variables:
            if v.lower() == 'et':
                output_images.append(self.et)
            elif v.lower() == 'etr':
                output_images.append(self.etr)
            elif v.lower() == 'etf':
                output_images.append(self.etf)
            elif v.lower() == 'fc':
                output_images.append(self.fc)
            elif v.lower() == 'kc':
                output_images.append(self.kc)
            # elif v.lower() == 'landcover':
            #     output_images.append(self.landcover)
            elif v.lower() == 'mask':
                output_images.append(self.mask)
            elif v.lower() == 'ndvi':
                output_images.append(self.ndvi)
            elif v.lower() == 'time':
                output_images.append(self.time)
            else:
                raise ValueError('unsupported variable: {}'.format(v))

        return ee.Image(output_images).set(self._properties)

    @lazy_property
    def etf(self):
        """Return Kc as ETf"""
        return self.kc.rename(['etf']).set(self._properties).double()
        # ETf could also be calculated from ET and ETr
        # return self.et.divide(self.etr) \
        #     .rename(['etf']).set(self._properties).double()

    @lazy_property
    def etr(self):
        """Compute reference ET for the image date"""
        if utils.is_number(self.etr_source):
            # Interpret numbers as constant images
            # CGM - Should we use the ee_types here instead?
            #   i.e. ee.ee_types.isNumber(self.etr_source)
            etr_img = ee.Image.constant(self.etr_source)
        elif type(self.etr_source) is str:
            # Assume a string source is an image collection ID (not an image ID)
            etr_img = ee.Image(
                ee.ImageCollection(self.etr_source) \
                    .filterDate(self._start_date, self._end_date) \
                    .select([self.etr_band]) \
                    .first())
        else:
            raise ValueError('unsupported etr_source: {}'.format(
                self.etr_source))

        return self.ndvi.multiply(0).add(etr_img) \
            .multiply(self.etr_factor)\
            .rename(['etr']).set(self._properties).double()

    @lazy_property
    def et(self):
        """Compute ETcb as Kc * etr"""
        return self.kc.multiply(self.etr) \
            .rename(['et']).set(self._properties).double()

    @lazy_property
    def fc(self):
        """Compute and return the Fc image"""
        return self.ndvi.multiply(1.26).subtract(0.18) \
            .clamp(0, 1)\
            .rename(['fc']).set(self._properties).double()

    @lazy_property
    def kc(self):
        """Compute and return the Kc image"""
        """
        Generic Fc-Kcb conversion for:
            Annuals-
            Melton, F., L. Johnson, C. Lund, L. Pierce, A. Michaelis, S. Hiatt, A. Guzman, D. Adhikari,
            A. Purdy, C. Rosevelt, P. Votava, T. Trout, B. Temesgen, K. Frame, E. Sheffner, and R. Nemani, 2012.
            Satellite Irrigation Management Support with the Terrestrial Observation and Prediction System:
            An Operational Framework for Integration of Satellite and Surface Observations to Support
            Improvements in Agricultural Water Resource Management.  IEEE J. Selected Topics in Applied
            Earth Observations & Remote Sensing 5:1709-1721.  [FIG 2b]
            Vines-
            Williams, L. and J. Ayars, 2005.  Grapevine water use and the crop coefficient are linear
            functions of the shaded area measured beneath the canopy, Ag. For. Meteor 132:201-211.  [FIG 10]
            Trees-
            Ayars, J., R. Johnson, C. Phene, T. Trout, D. Clark, and R. Mead, 2003.  Water use by
            drip-irrigated late-season peaches.  Irrig. Sci. 22:187-194.  [EQN 7]
        Crop specific Fc-Kcb conversion:
            Allen, R., and L. Pereira, 2009.  Estimating crop coefficients from fraction of ground cover
            and height.  Irrig. Sci. 28:17-34.  [EQNS 10 (Kd); 7a (Kcb_full) using tree/vine Fr vals
            from Table 2; 5a (Kcb)]
        """
        # I haven't implemented the crop-specific equations for this version.
        # We would first run the crop-specific before doing the generic equations
        fc_zero = self.fc.multiply(0)

        # Generic equation for annual crops
        img_expr = self.fc.expression(
            "((b('fc') ** 2) * -0.4771) + (1.4047 * b('fc')) + 0.15")
        kc1 = fc_zero.where(self.landcover.eq(1), img_expr)

        # Generic equation for vines
        kc2 = fc_zero.where(self.landcover.eq(2), self.fc.multiply(1.7))

        # Generic equation for trees
        kc3 = fc_zero.where(
            self.landcover.eq(3), self.fc.multiply(1.48).add(0.007))

        # Add up all the Kcs
        return kc1.add(kc2).add(kc3)\
            .clamp(0, 1.25)\
            .rename(['kc']).set(self._properties).double()

    @lazy_property
    def landcover(self):
        """"Get the land cover type"""
        if utils.is_number(self.landcover_source):
            # Interpret numbers as constant images
            # CGM - Should we use the ee_types here instead?
            #   i.e. ee.ee_types.isNumber(self.etr_source)
            landcover_img = ee.Image.constant(self.landcover_source)\
                .rename(['cropland'])
        elif (type(self.landcover_source) is str and
              self.landcover_source.upper() == 'USDA/NASS/CDL'):
            # Use 2018 CDL even if image date is in 2019
            start_year = self._year.min(2018)
            start_date = ee.Date.fromYMD(start_year, 1, 1)
            end_date = ee.Date.fromYMD(start_year.add(1), 1, 1)
            cdl_coll = ee.ImageCollection(self.landcover_source) \
                .filterDate(start_date, end_date)\
                .select(['cropland'])
            #     .select([self.landcover_band])
            landcover_img = ee.Image(cdl_coll.first())
        else:
            raise ValueError('unsupported landcover_source: {}'.format(
                self.landcover_source))

        # Now we need to resample the CDL to our 3 generic classes
        # CGM - Trying out some other ways of defining the remap table that are
        #   a little less prone to error

        # CGM - Group the "from" values in a list for each "to" value
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
        remap_dict = {f: t for t, from_list in remap_dict.items() for f in from_list}
        remap_from, remap_to = zip(*sorted(remap_dict.items()))
        landcover_img = landcover_img.remap(remap_from, remap_to, 0, 'cropland')

        # # CGM - Define the map directly for each crop
        # remap_dict = {
        #     1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1,
        #     10: 1, 11: 1, 12: 1, 13: 1, 14: 1,
        #     21: 1, 22: 1, 23: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 1, 29: 1,
        #     30: 1, 31: 1, 32: 1, 33: 1, 34: 1, 35: 1, 36: 1, 37: 1, 38: 1,
        #     41: 1, 42: 1, 43: 1, 44: 1, 45: 1, 46: 1, 47: 1, 48: 1, 49: 1,
        #     50: 1, 51: 1, 52: 1, 53: 1, 54: 1, 55: 1, 56: 1, 57: 1, 58: 1, 59: 1,
        #     60: 1, 61: 1, 80: 1, 182: 1,
        #     202: 1, 205: 1, 206: 1, 207: 1, 208: 1, 209: 1,
        #     213: 1, 214: 1, 216: 1, 219: 1,
        #     221: 1, 222: 1, 224: 1, 225: 1, 226: 1, 227: 1, 228: 1, 229: 1,
        #     230: 1, 231: 1, 232: 1, 233: 1, 234: 1, 235: 1, 236: 1, 237: 1, 238: 1, 239: 1,
        #     240: 1, 241: 1, 242: 1, 243: 1, 244: 1, 245: 1, 246: 1, 247: 1, 248: 1, 249: 1,
        #     250: 1, 254: 1,
        #     69: 2,
        #     66: 3, 67: 3, 68: 3,
        #     70: 3, 71: 3, 72: 3, 73: 3, 74: 3, 75: 3, 76: 3, 77: 3,
        #     201: 3, 203: 3, 204: 3,
        #     210: 3, 211: 3, 212: 3, 215: 3, 217: 3, 218: 3, 220: 3, 223: 3,
        # }
        # remap_from, remap_to = zip(*remap_dict.items())
        # landcover_img = landcover_img.remap(remap_from, remap_to, 0, 'cropland')

        # # CGM - Original Remap
        # remapFrom = (
        #     1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14,
        #     21, 22, 23, 24, 25, 26, 27, 28, 29,
        #     30, 31, 32, 33, 34, 35, 36, 37, 38,
        #     41, 42, 43, 44, 45, 46, 47, 48, 49,
        #     50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 80, 182,
        #     202, 205, 206, 207, 208, 209, 213, 214, 216, 219,
        #     221, 222, 224, 225, 226, 227, 228, 229,
        #     230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
        #     240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 254,
        #     69,
        #     66, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77,
        #     201, 203, 204, 210, 211, 212, 215, 217, 218, 220, 223)
        # remapTo = (
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        #     2,
        #     3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
        #     3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)
        # landcover_img = landcover_img.remap(remapFrom, remapTo, 0, 'cropland')

        return self.ndvi.multiply(0).add(landcover_img) \
            .rename('cropland').set(self._properties).double()

    @lazy_property
    def mask(self):
        """Mask of all active pixels (based on the final kc)

        Using Kc here to capture any masking that might be in the Landcover
        """
        return self.kc.multiply(0).add(1).updateMask(1)\
            .rename(['mask']).set(self._properties).uint8()

    @lazy_property
    def ndvi(self):
        """Return NDVI image"""
        return self.image.select(['ndvi']).set(self._properties).double()

    # @lazy_property
    # def quality(self):
    #     """Set quality to 1 for all active pixels (for now)"""
    #     return self.mask\
    #         .rename(['quality']).set(self._properties)

    @lazy_property
    def time(self):
        """Return an image of the 0 UTC time (in milliseconds)"""
        return self.mask \
            .double().multiply(0).add(utils.date_to_time_0utc(self._date)) \
            .rename(['time']).set(self._properties).double()

    @classmethod
    def from_image_id(cls, image_id, **kwargs):
        """Constructs an NDVI-ET Image instance from an image ID

        Parameters
        ----------
        image_id : str
            An earth engine image ID.
            (i.e. 'LANDSAT/LC08/C01/T1_SR/LC08_044033_20170716')
        kwargs
            Keyword arguments to pass through to model init.

        Returns
        -------
        new instance of Image class

        """

        # For SIMS we only use the surface reflectance product
        collection_methods = {
            'LANDSAT/LC08/C01/T1_SR': 'from_landsat_c1_sr',
            'LANDSAT/LE07/C01/T1_SR': 'from_landsat_c1_sr',
            'LANDSAT/LT05/C01/T1_SR': 'from_landsat_c1_sr',
            'LANDSAT/LT04/C01/T1_SR': 'from_landsat_c1_sr',
        }

        try:
            method_name = collection_methods[image_id.rsplit('/', 1)[0]]
        except KeyError:
            raise ValueError('unsupported collection ID: {}'.format(image_id))
        except Exception as e:
            raise Exception('unhandled exception: {}'.format(e))

        method = getattr(Image, method_name)

        return method(ee.Image(image_id), **kwargs)

    @classmethod
    def from_landsat_c1_sr(cls, sr_image, **kwargs):
        """Constructs an NDVI-ET Image instance from a Landsat SR image

        Parameters
        ----------
        sr_image : ee.Image, str
            A raw Landsat Collection 1 SR image or image ID.
        kwargs : dict
            Keyword arguments to pass through to model init.

        Returns
        -------
        new instance of Image class

        """
        sr_image = ee.Image(sr_image)

        # Use the SATELLITE property identify each Landsat type
        spacecraft_id = ee.String(sr_image.get('SATELLITE'))

        # Rename bands to generic names
        input_bands = ee.Dictionary({
            'LANDSAT_4': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'B6', 'pixel_qa'],
            'LANDSAT_5': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'B6', 'pixel_qa'],
            'LANDSAT_7': ['B1', 'B2', 'B3', 'B4', 'B5', 'B7', 'B6', 'pixel_qa'],
            'LANDSAT_8': ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B10', 'pixel_qa'],
        })
        output_bands = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'lst',
                        'pixel_qa']
        prep_image = sr_image.select(input_bands.get(spacecraft_id),
                                     output_bands)

        # Build the input image
        # Eventually send the BQA band or a cloud mask through also
        input_image = ee.Image([
            cls._ndvi(prep_image)
        ])

        # Apply the cloud mask and add properties
        input_image = input_image \
            .updateMask(common.landsat_c1_sr_cloud_mask(sr_image)) \
            .set({
                'system:index': sr_image.get('system:index'),
                'system:time_start': sr_image.get('system:time_start'),
                'system:id': sr_image.get('system:id'),
            })

        # Instantiate the class
        return cls(input_image, **kwargs)

    @staticmethod
    def _ndvi(sr_image):
        """Compute NDVI

        Parameters
        ----------
        toa_image : ee.Image
            Renamed SR image with 'nir' and 'red bands.

        Returns
        -------
        ee.Image

        """
        return sr_image.normalizedDifference(['nir', 'red']) \
            .rename(['ndvi'])

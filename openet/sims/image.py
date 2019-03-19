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

import utils
import openet.core.common as common

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
            landcover_source='USDA/NASS/CDL',
            landcover_band='cropland'
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

        Kc = Fc based on croptype
        ETcb = Kc * ETo

        """
        self.image = image

        self.etr_source = etr_source
        self.etr_band = etr_band

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
            elif v.lower() == 'ndvi':
                output_images.append(self.ndvi)
            elif v.lower() == 'time':
                output_images.append(self.time)
            else:
                raise ValueError('unsupported variable: {}'.format(v))

        return ee.Image(output_images).set(self._properties)

    @lazy_property
    def ndvi(self):
        """Return NDVI image"""
        return self.image.select(['ndvi']).set(self._properties).double()

    @lazy_property
    def fc(self):
        """Compute and return the Fc image"""

        return self.ndvi.multiply(1.26).subtract(-0.18) \
            .rename(['fc']).set(self._properties).double()

    @lazy_property
    def landcover(self):
        """"Get the land cover type"""
        start_date = self._start_date
        end_date = self._end_date

        #There is no CDL for 2017-present
        if int(start_date[0:3]) > 2016:
           start_date = '2016-01-01'
        if int(end_date[0:3]) > 2016:
           end_date = '2017-01-01'
        # Assume a string source is an image collection ID (not an image ID)
        landcover_img = ee.Image(ee.ImageCollection(self.landcover_source) \
                                 .filterDate(start_date,end_date) \
                                 .select('cropland') \
                                 .first())

        # Now we need to resample the CDL to our 3 generic classes
        remapFrom = (1, 2, 3, 4, 5, 6, 10, 11, 12, 13, 14, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35,
                     36, 37, 38, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 80,
                     182, 202, 205, 206, 207, 208, 209, 213, 214, 216, 219, 221, 222, 224, 225, 226, 227, 228, 229, 230,
                     231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250,
                     254,
                     69,
                     66, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77, 201, 203, 204, 210, 211, 212, 215, 217, 218, 220, 223)

        remapTo = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                   2,
                   3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3)

        landcover_img = ee.Image(landcover_img.remap(remapFrom, remapTo, 0, 'cropland'))

        return self.ndvi.multiply(0).add(landcover_img) \
            .rename('cropland').set(self._properties).double()

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

        # First get the lancover and reclassify
        landcover_img = self.landcover
        fc_img = self.fc

        # Generic equation for annual crops
        landcover_expr = landcover_img.expression("b('cropland') == 1")
        img_expr = fc_img.expression("((b('fc') ** 2)* -0.4771) + (1.4047*b('fc'))+0.15")
        kc1 = fc_img.where(landcover_expr, img_expr)

        # Generic equation for vines
        img_expr = landcover_img.expression("b('cropland') == 2")
        kc2 = fc_img.where(img_expr, fc_img.multiply(1.7))

        # Generic equation for trees
        img_expr = landcover_img.expression("b('cropland') == 3")
        kc3 = fc_img.where(img_expr, fc_img.multiply(1.48).add(0.007))

        # Add up all the Kcs
        kc = kc1.add(kc2).add(kc3)

        return kc.rename(['kc']).set(self._properties).double()

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
            .rename(['etr']).set(self._properties).double()

    @lazy_property
    def et(self):
        """Compute ETcb as Kc * etr"""
        return self.kc.multiply(self.etr) \
            .rename(['et']).set(self._properties).double()

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
            'COPERNICUS/S2': 'from_sentinel2_toa',
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

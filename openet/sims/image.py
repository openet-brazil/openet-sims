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
            crop_type_source='USDA/NASS/CDL',
            crop_type_remap='CDL',
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
        crop_type_source : str, optional
            Crop type source.  The default is the OpenET crop type image collection.
            The source should be an Earth Engine Image ID (or ee.Image).
            Currently only the OpenET collection and CDL images are supported.
        crop_type_remap : {'CDL'}, optional
            Currently only CDL crop type values are supported.

        Notes
        -----
        Fc = (NDVI * 1.26) - 0.18
        Kc = f(Fc) [based on crop type]
        ETcb = Kc * ETo

        References
        ----------
        .. [1] Johnson, L. and T. Trout, 2012. Satellite NDVI assisted
            monitoring of vegetable crop evapotranspiration in California's San
            Joaquin Valley. Remote Sensing 4:439-455. [EQN 1]

        """
        self.image = image

        self.etr_source = etr_source
        self.etr_band = etr_band
        self.etr_factor = etr_factor

        self.crop_type_source = crop_type_source
        self.crop_type_remap = crop_type_remap

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
            # elif v.lower() == 'crop_class':
            #     output_images.append(self.crop_class)
            # elif v.lower() == 'crop_type':
            #     output_images.append(self.crop_type)
            elif v.lower() == 'fc':
                output_images.append(self.fc)
            elif v.lower() == 'kc':
                output_images.append(self.kc)
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
        """Fraction of reference ET (equivalent to the Kc)

        This method is basically identical to the "kc" method and is only
        provided to simplify interaction with the interpolation tools in the
        Collection.

        Returns
        -------
        ee.Image

        """
        return self.kc.rename(['etf']).set(self._properties).double()
        # ETf could also be calculated from ET and ETr
        # return self.et.divide(self.etr)\
        #     .rename(['etf']).set(self._properties).double()

    @lazy_property
    def etr(self):
        """Reference ET for the image date

        Returns
        -------
        ee.Image

        """
        if utils.is_number(self.etr_source):
            # Interpret numbers as constant images
            # CGM - Should we use the ee_types here instead?
            #   i.e. ee.ee_types.isNumber(self.etr_source)
            etr_img = ee.Image.constant(self.etr_source)
        elif type(self.etr_source) is str:
            # Assume a string source is an image collection ID (not an image ID)
            etr_img = ee.Image(
                ee.ImageCollection(self.etr_source)\
                    .filterDate(self._start_date, self._end_date)\
                    .select([self.etr_band])\
                    .first())
        else:
            raise ValueError('unsupported etr_source: {}'.format(
                self.etr_source))

        return self.ndvi.multiply(0).add(etr_img)\
            .multiply(self.etr_factor)\
            .rename(['etr']).set(self._properties).double()

    @lazy_property
    def et(self):
        """Actual ET (ETcb)

        Returns
        -------
        ee.Image

        """
        return self.kc.multiply(self.etr)\
            .rename(['et']).set(self._properties).double()

    @lazy_property
    def crop_class(self):
        """Generic crop classes

        The current OpenET SIMS model only supports three generic crop classes.
        This method will map the crop type codes to the three classes.
        Currently, only CDL crop type codes are supported.

        Parameters
        ----------
        self.crop_type : ee.Image
        self.crop_type_remap : str

        Returns
        -------
        ee.Image

        Raises
        ------
        ValueError for unsupported crop_type_remap

        """
        if self.crop_type_remap.upper() == 'CDL':
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
                self.crop_type_remap))

        remap_dict = {f: t for t, from_list in remap_dict.items() for f in from_list}
        remap_from, remap_to = zip(*sorted(remap_dict.items()))

        # Map the the crop class values to the NDVI image
        return self.ndvi.multiply(0)\
            .add(self.crop_type.remap(remap_from, remap_to, 0, 'crop_type'))\
            .rename('crop_class').set(self._properties)
        # CGM I'm not sure why this was being mapped to a double
        #     .double()

    @lazy_property
    def crop_type(self):
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

        Returns
        -------
        ee.Image

        Raises
        ------
        ValueError for unsupported crop_type_sources

        """
        properties = ee.Dictionary()

        if utils.is_number(self.crop_type_source):
            # Interpret numbers as constant images
            # CGM - Should we use the ee_types here instead?
            #   i.e. ee.ee_types.isNumber(self.etr_source)
            crop_type_img = self.crop_type_source
            # properties = properties.set('id', 'constant')

        elif (type(self.crop_type_source) is str and
              self.crop_type_source.upper() == 'USDA/NASS/CDL'):
            # Use the CDL image closest to the image date
            # Hardcoding the CDL year range but it could be computed dynamically
            cdl_year_min = ee.Number(2008)
            cdl_year_max = ee.Number(2018)
            # cdl_year_max = ee.Date(ee.ImageCollection('USDA/NASS/CDL')
            #     .limit(1, 'system:index', False).first()
            #     .get('system:time_start')).get('year')
            # cdl_year_max = ee.Number.parse(ee.ImageCollection('USDA/NASS/CDL')\
            #     .limit(1, 'system:index', False).first().get('system:index'))

            start_year = self._year.min(cdl_year_max).max(cdl_year_min)
            start_date = ee.Date.fromYMD(start_year, 1, 1)
            end_date = ee.Date.fromYMD(start_year.add(1), 1, 1)
            cdl_coll = ee.ImageCollection('USDA/NASS/CDL')\
                .filterDate(start_date, end_date)\
                .select(['cropland'])
            crop_type_img = ee.Image(cdl_coll.first())
            # pprint.pprint(crop_type_img.getInfo())
            properties = properties.set('id', crop_type_img.get('system:id'))
            # pprint.pprint(properties.getInfo())

        elif (type(self.crop_type_source) is str and
              self.crop_type_source.upper().startswith('USDA/NASS/CDL')):
            crop_type_img = ee.Image(self.crop_type_source)\
                .select(['cropland'])
            # pprint.pprint(crop_type_img.getInfo())
            properties = properties.set('id', crop_type_img.get('system:id'))
            # pprint.pprint(properties.getInfo())

        elif (type(self.crop_type_source) is str and
              self.crop_type_source.lower() == 'projects/openet/crop_type'):
            crop_type_img = ee.ImageCollection(self.crop_type_source).mosaic()
            # properties = properties.set('id', 'projects/openet/crop_type')

        # TODO: Support ee.Image and ee.ImageCollection sources
        # elif isinstance(self.crop_type_source, computedobject.ComputedObject):

        else:
            raise ValueError('unsupported crop_type_source: {}'.format(
                self.crop_type_source))

        # CGM - Should the crop type images all be mapped onto the Image
        #   or just returned as is
        # Should the image properties be set onto the image also?
        return self.ndvi.multiply(0).add(crop_type_img).rename(['crop_type'])\
            .set(properties)

    @lazy_property
    def fc(self):
        """Fraction of cover (fc)

        Returns
        -------
        ee.Image

        """
        return self.ndvi.multiply(1.26).subtract(0.18)\
            .clamp(0, 1)\
            .rename(['fc']).set(self._properties).double()

    @lazy_property
    def kc(self):
        """Crop coefficient (Kc)

        Returns
        -------
        ee.Image

        Noes
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
        fc_zero = self.fc.multiply(0)

        # Generic equation for annual crops
        img_expr = self.fc.expression(
            "((b('fc') ** 2) * -0.4771) + (1.4047 * b('fc')) + 0.15")
        kc1 = fc_zero.where(self.crop_class.eq(1), img_expr)

        # Generic equation for vines
        kc2 = fc_zero.where(self.crop_class.eq(2), self.fc.multiply(1.7))

        # Generic equation for trees
        kc3 = fc_zero.where(
            self.crop_class.eq(3),
            self.fc.multiply(1.48).add(0.007))

        # Add up all the Kcs
        kc = kc1.add(kc2).add(kc3).clamp(0, 1.25)

        # CGM - Set all non-ag cells to nodata
        #   It might make more sense to do this to crop_type or crop_class
        kc = kc.updateMask(self.crop_class.gt(0))

        return kc.rename(['kc']).set(self._properties).double()

    @lazy_property
    def mask(self):
        """Mask of all active pixels based on the final Kc

        Using Kc here to capture any masking that might be in the crop_type

        Returns
        -------
        ee.Image

        """
        return self.kc.multiply(0).add(1).updateMask(1)\
            .rename(['mask']).set(self._properties).uint8()

    @lazy_property
    def ndvi(self):
        """Normalized difference vegetation index (NDVI)

        Returns
        -------
        ee.Image

        """
        return self.image.select(['ndvi']).set(self._properties).double()

    # @lazy_property
    # def quality(self):
    #     """Set quality to 1 for all active pixels (for now)"""
    #     return self.mask\
    #         .rename(['quality']).set(self._properties)

    @lazy_property
    def time(self):
        """Image of the 0 UTC time (in milliseconds)

        Returns
        -------
        ee.Image

        """
        return self.mask\
            .double().multiply(0).add(utils.date_to_time_0utc(self._date))\
            .rename(['time']).set(self._properties).double()

    @classmethod
    def from_image_id(cls, image_id, **kwargs):
        """Construct a SIMS Image instance from an image ID

        Parameters
        ----------
        image_id : str
            A full earth engine image ID.
            (i.e. 'LANDSAT/LC08/C01/T1_SR/LC08_044033_20170716')
        kwargs : dict
            Keyword arguments to pass through to model init.

        Returns
        -------
        new instance of Image class

        Raises
        ------
        ValueError for an unsupported collection ID.

        """

        # For SIMS, only support the surface reflectance collections
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
        """Construct a SIMS Image instance from a Landsat SR image

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
        input_image = input_image\
            .updateMask(common.landsat_c1_sr_cloud_mask(sr_image))\
            .set({
                'system:index': sr_image.get('system:index'),
                'system:time_start': sr_image.get('system:time_start'),
                'system:id': sr_image.get('system:id'),
            })

        return cls(input_image, **kwargs)

    @staticmethod
    def _ndvi(sr_image):
        """Compute NDVI

        Parameters
        ----------
        sr_image : ee.Image
            Renamed SR image with bands 'nir' and 'red'.

        Returns
        -------
        ee.Image

        """
        return sr_image.normalizedDifference(['nir', 'red']).rename(['ndvi'])

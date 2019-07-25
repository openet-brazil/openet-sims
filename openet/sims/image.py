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

from .model import Model
# from . import model
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
            crop_type_kc_flag=False,  # CGM - Not sure what to call this parameter yet
            crop_type_mask_flag=False,
            ):
        """Earth Engine based SIMS image object

        Parameters
        ----------
        image : ee.Image
            Required band: ndvi
            Required properties: system:time_start, system:index, system:id
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
        crop_type_kc_flag : bool, optional
            If True, compute Kc using crop type specific coefficients.
            If False, use generic crop class coefficients.
            The default is False.
        crop_type_mask_flag : bool, optional
            If True, mask all pixels that don't map to a crop_class.
            The default is False.

        Notes
        -----
        Fc = (NDVI * 1.26) - 0.18
        Kc = f(Fc) [based on crop type or crop class]
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
        self._doy = self._date.getRelative('day', 'year').add(1).int()

        # CGM - Model class could inherit these from Image instead of passing them
        #   Could pass time_start instead of separate year and doy
        self.model = Model(
            year=self._year, doy=self._doy,
            crop_type_source=crop_type_source,
            crop_type_remap=crop_type_remap,
            crop_type_kc_flag=crop_type_kc_flag,
            crop_type_mask_flag=crop_type_mask_flag,
        )

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

        Returns
        -------
        ee.Image

        """
        # Map the the crop class values to the NDVI image
        return self.ndvi.multiply(0)\
            .add(self.model.crop_class)\
            .rename('crop_class').set(self._properties)

    @lazy_property
    def crop_type(self):
        """Crop type

        Returns
        -------
        ee.Image

        """
        # Map the the crop class values to the NDVI image
        # Crop type image ID property is set in model function
        return self.ndvi.multiply(0)\
            .add(self.model.crop_type)\
            .rename(['crop_type'])

    @lazy_property
    def fc(self):
        """Fraction of cover (fc)

        Returns
        -------
        ee.Image

        """
        return self.model.fc(self.ndvi)\
            .rename(['fc']).set(self._properties).double()

    @lazy_property
    def kc(self):
        """Crop coefficient (Kc)

        Returns
        -------
        ee.Image

        """
        return self.model.kc(self.ndvi)\
            .rename(['kc']).set(self._properties).double()


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
    def _ndvi(landsat_image):
        """Normalized difference vegetation index

        Parameters
        ----------
        landsat_image : ee.Image
            "Prepped" Landsat image with standardized band names.

        Returns
        -------
        ee.Image

        """
        return landsat_image.normalizedDifference(['nir', 'red'])\
            .rename(['ndvi'])

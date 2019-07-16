import pprint

import ee

from . import data
from . import utils


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


class Model():
    """GEE based model for computing SIMS ETcb"""

    def __init__(
            self,
            year,
            doy,
            crop_type_source='USDA/NASS/CDL',
            crop_type_remap='CDL',
            crop_type_kc_flag=False,  # CGM - Not sure what to call this parameter yet
            ):
        """Earth Engine based SIMS model object"""

        # Model could inherit these values from Image instead of being passed in
        self.year = year
        self.doy = doy
        # self.date = ee.Date(self.time_start)
        # self.year = ee.Number(self.date.get('year'))
        # self.doy = self._date.getRelative('day', 'year').add(1).int()

        self.crop_type_source = crop_type_source
        self.crop_type_remap = crop_type_remap
        self.crop_type_kc_flag = crop_type_kc_flag

        # CGM - Trying out setting as properties in init
        #   instead of as lazy properties below
        self.crop_data = self._crop_data()
        self.crop_type = self._crop_type()
        self.crop_class = self._crop_class()

        # Dynamically set the crop data parameter images as class properties
        # This only works if crop_type and crop_data are set in init
        for param in ['m_l', 'h_max']:
            setattr(self, param,
                    crop_data_image(param, self.crop_type, self.crop_data))


    # # CGM - Currently setting these in init so they can be set dynamically
    # @lazy_property
    # def h_max(self):
    #     return crop_data_image('h_max', self.crop_type, self.crop_data)
    #
    # @lazy_property
    # def m_l(self):
    #     return crop_data_image('m_l', self.crop_type, self.crop_data)


    # CGM - crop_type, crop_class, and crop_data could be lazy properties?
    #   It might be confusing though to have kc and fc not be.
    # @lazy_property
    def _crop_type(self):
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
            Year is needed if crop_type_source is the CDL collection.

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
            crop_type_img = ee.Image.constant(self.crop_type_source)
            #     .rename('crop_type')
            # properties = properties.set('id', 'constant')

        elif (type(self.crop_type_source) is str and
              self.crop_type_source.upper() == 'USDA/NASS/CDL'):
            # Use the CDL image closest to the image date
            # Hard coding the CDL year range but it could be computed dynamically
            cdl_year_min = ee.Number(2008)
            cdl_year_max = ee.Number(2018)
            # cdl_year_max = ee.Date(ee.ImageCollection('USDA/NASS/CDL')
            #     .limit(1, 'system:index', False).first()
            #     .get('system:time_start')).get('year')
            # cdl_year_max = ee.Number.parse(ee.ImageCollection('USDA/NASS/CDL')\
            #     .limit(1, 'system:index', False).first().get('system:index'))

            start_year = self.year.min(cdl_year_max).max(cdl_year_min)
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

        # Should the image properties be set onto the image also?
        return crop_type_img.rename(['crop_type']).set(properties)

    # @lazy_property
    def _crop_class(self):
        """Map crop type values to generic crop classes

        The current OpenET SIMS model only supports three generic crop classes.
        This method will map the crop type codes to the three classes.
        Currently, only CDL crop type codes are supported.

        Parameters
        ----------
        crop_type : ee.Image
        crop_data : dict

        Returns
        -------
        ee.Image

        """
        remap_dict = {crop_type: crop_data['crop_class']
                      for crop_type, crop_data in self.crop_data.items()}
        remap_from, remap_to = zip(*sorted(remap_dict.items()))
        return self.crop_type.remap(remap_from, remap_to, 0)\
            .rename(['crop_class'])

    # @lazy_property
    def _crop_data(self):
        """Load the crop data dictionary

        Currently the data is in data.py but this method could also be used to
        read the data from a json or csv file.

        Parameters
        ----------
        crop_type : ee.Image
        crop_type_remap : str

        Returns
        -------
        dict

        Raises
        ------
        ValueError for unsupported crop_type_remap

        """
        if self.crop_type_remap.upper() == 'CDL':
            return data.cdl
        else:
            raise ValueError('unsupported crop_type_remap: "{}"'.format(
                self.crop_type_remap))

    # CGM - This could be lazy if ndvi was inherited from Image
    # @lazy_property
    def fc(self, ndvi, fc_min=0.0, fc_max=1.0):
        """Fraction of cover (fc)

        Parameters
        ----------
        ndvi : ee.Image
        fc_min : float, optional
        fc_max : float, optional

        Returns
        -------
        ee.Image

        """
        return ndvi.multiply(1.26).subtract(0.18)\
            .clamp(fc_min, fc_max)\
            .rename(['fc'])

    # CGM - It doesn't really make sense to have kc be lazy unless fc is also
    # @lazy_property
    def kc(self, fc, ndvi):
        """

        Parameters
        ----------
        fc : ee.Image
            Fraction of cover
        ndvi : ee.Image
            Normalized difference vegetation index.  Used to compute rice Kc.

        Returns
        -------
        ee.Image

        """
        # Compute generic/general Kc for each crop class and combine
        # CGM - Not sure which approach is best or most efficient
        kc = fc.multiply(0)
        kc = kc.where(self.crop_class.eq(1), self.kc_row_crop(fc))
        kc = kc.where(self.crop_class.eq(2), self.kc_vine(fc))
        kc = kc.where(self.crop_class.eq(3), self.kc_tree(fc))
        kc = kc.where(self.crop_class.eq(5), self.kc_rice(fc, ndvi))

        # kc0 = fc.multiply(0)
        # kc1 = kc0.where(self.crop_class.eq(1), self.kc_row_crop(fc))
        # kc2 = kc0.where(self.crop_class.eq(2), self.kc_vine(fc))
        # kc3 = kc0.where(self.crop_class.eq(3), self.kc_tree(fc))
        # kc5 = kc0.where(self.crop_class.eq(5), self.kc_rice(fc))
        # kc = kc1.add(kc2).add(kc3).add(kc5)

        # CGM - How would I combine these?
        # kc0 = fc.multiply(0)
        # kc1 = self.kc_row_crop(fc).updateMask(self.crop_class.eq(1))
        # kc2 = self.kc_vine(fc).updateMask(self.crop_class.eq(2))
        # kc3 = self.kc_tree(fc).updateMask(self.crop_class.eq(3))
        # kc5 = self.kc_rice(fc).updateMask(self.crop_class.eq(4))
        # kc = ee.Image([kc1, kc2, kc3, kc5]).reduce(ee.Reducer.first())

        if self.crop_type_kc_flag:
            # CGM - Is there a better way of masking/selecting the updated pixels?
            kc = kc.where(self.crop_class.eq(1).And(self.h_max.gte(0)),
                          self.kc_row_crop_custom(fc))
            kc = kc.where(self.crop_class.eq(3).And(self.h_max.gte(0)),
                          self.kc_tre_custom(fc))

    #     # kc = zero.where(
    #     #     self.crop_type.eq(crop_type_num),
    #     #     kd.multiply(kc_help.kcb_full(self.doy, crop_prof).subtract(kc_min))\
    #     #         .add(kc_min)\
    #     #         .clamp(0, 1.1)
    #     # )

        return kc.clamp(0, 1.1)

    def kc_row_crop(self, fc):
        """General row crop coefficient

        Parameters
        ----------
        fc : ee.Image
            Fraction of cover

        Returns
        -------
        ee.Image

        """
        return fc.expression("((b(0) ** 2) * -0.4771) + (1.4047 * b(0)) + 0.15")

    def kc_row_crop_custom(self, fc):
        """Custom row crop coefficient based on CDL crop type

        Parameters
        ----------
        fc : ee.Image
            Fraction of cover

        Returns
        -------
        ee.Image

        """
        # First calculation is the fc.divide(0.7).lte(1) case
        # CGM - Add an expression example of this calculation
        kc = fc.multiply(self.m_l)\
            .min(fc.pow(fc.divide(0.7).multiply(self.h_max).pow(-1).add(1)))\
            .min(1)
        kc = kc.where(
            fc.divide(0.7).gt(1),
            fc.multiply(self.m_l).min(fc.pow(self.h_max.add(1).pow(-1))).min(1))
        return kc

    def kc_vine(self, fc):
        """Vine (grape) crop coefficient

        Parameters
        ----------
        fc : ee.Image
            Fraction of cover

        Returns
        -------
        ee.Image

        """
        # fc is clamped to <= 1 so the final .min(1) may be redundant
        return fc.multiply(1.5).min(fc.pow(1 / (1 + 2))).min(1)

    def kc_tree(self, fc):
        """General tree crop coefficient

        Parameters
        ----------
        fc : ee.Image
            Fraction of cover

        Returns
        -------

        """
        return fc.multiply(1.48).add(0.007)

    def kc_tree_custom(self, fc):
        """Custom tree crop coefficient based on CDL crop type

        Parameters
        ----------
        fc : ee.Image
            Fraction of cover

        Returns
        -------
        ee.Image

        """
        # CGM - Add an expression example of this calculation
        kc = fc.multiply(self.m_l).min(fc.pow(self.h_max.add(1).pow(1)))\
            .min(1)
        kc = kc.where(
            fc.lte(0.5),
            fc.multiply(self.m_l).min(fc.pow(self.h_max.pow(-1))).min(1))
        return kc

    def kc_rice(self, fc, ndvi):
        """Rice crop coefficient

        Parameters
        ----------
        fc : ee.Image
            Fraction of cover
        ndvi : ee.Image
            Normalized difference vegetation index

        Returns
        -------
        ee.Image

        """
        # Can't use fc for determining water since it is clamped to >= 0
        #   for low ndvi values (i.e. ndvi <= 0.142857)
        return fc.where(ndvi.lte(0.14), 1.05)

    # def kcb_full(doy, crop_prof):
    #     """Basal crop coefficient (Kcb) for a given crop on day-of-year.
    #
    #     Parameters
    #     ----------
    #     doy : int
    #     crop_prof : CropProfile
    #
    #     Returns
    #     -------
    #     ee.Number
    #
    #     """
    #     return ee.Number(fr(doy, crop_prof))\
    #         .multiply(min(1 + 0.1 * crop_prof.h_max, 1.2))
    #
    # def fr(doy, crop_prof):
    #     """Reduction factor (f_r) for adjusting Kcb of tree crops
    #
    #     Estimated using a mean leaf stomatal resistance term.
    #
    #     Parameters
    #     ----------
    #     doy : int
    #     crop_prof : CropProfile
    #
    #     Returns
    #     -------
    #     ee.Number
    #
    #     """
    #     doy_gt_ls_stop = ee.Algorithms.If(
    #         doy.gt(crop_prof.ls_stop), crop_prof.fr_end, 0)
    #
    #     doy_geq_ls_start_and_doy_leq_ls_stop = ee.Algorithms.If(
    #         doy.gte(crop_prof.ls_start).And(doy.lte(crop_prof.ls_stop)),
    #         ee.Number(crop_prof.fr_mid)\
    #             .subtract(
    #                 (doy.subtract(crop_prof.ls_start))\
    #                 .divide(crop_prof.ls_stop - crop_prof.ls_start)\
    #                 .multiply(crop_prof.fr_mid - crop_prof.fr_end)
    #             ),
    #         doy_gt_ls_stop)
    #
    #     doy_lt_ls_start = ee.Algorithms.If(
    #         doy.lt(crop_prof.ls_start), crop_prof.fr_mid,
    #         doy_geq_ls_start_and_doy_leq_ls_stop)
    #
    #     fr = ee.Algorithms.If(crop_prof.crop_class == 1, 1, doy_lt_ls_start)
    #
    #     return fr


def crop_data_image(param_name, crop_type, crop_data):
    """Build a constant Image of crop type data for one parameter"""

    # Scale floating point values by integer factor, then divide after remap
    # Should the default be 0 or nodata for pixels that don't remap
    #   crop_type.remap(m_l_from, m_l_to, 0)
    data_dict = {
        c_type: c_data[param_name] * data.int_scalar
        for c_type, c_data in crop_data.items()
        if param_name in c_data.keys()}
    remap_from, remap_to = zip(*sorted(data_dict.items()))
    return crop_type.remap(remap_from, remap_to) \
        .double().divide(data.int_scalar) \
        .rename([param_name])









# # CGM - crop class is not being used directly here and is being read from img
# def kc(img, crop_class):
#     """Crop coefficient (Kc)
#
#     Parameters
#     ----------
#     img : openet.sims.Image
#     crop_class : ee.Image
#
#     Returns
#     -------
#     ee.Image
#
#     Notes
#     ----
#     Generic Fc-Kcb conversion for:
#     Annuals-
#         Melton, F., L. Johnson, C. Lund, L. Pierce, A. Michaelis, S. Hiatt,
#         A. Guzman, D. Adhikari, A. Purdy, C. Rosevelt, P. Votava, T. Trout,
#         B. Temesgen, K. Frame, E. Sheffner, and R. Nemani, 2012.
#         Satellite Irrigation Management Support with the Terrestrial
#         Observation and Prediction System: An Operational Framework for
#         Integration of Satellite and Surface Observations to Support
#         Improvements in Agricultural Water Resource Management.
#         IEEE J. Selected Topics in Applied Earth Observations & Remote Sensing
#         5:1709-1721.  [FIG 2b]
#     Vines-
#         Williams, L. and J. Ayars, 2005.  Grapevine water use and the crop
#         coefficient are linear functions of the shaded area measured beneath
#         the canopy, Ag. For. Meteor 132:201-211.  [FIG 10]
#     Trees-
#         Ayars, J., R. Johnson, C. Phene, T. Trout, D. Clark, and R. Mead, 2003.
#         Water use by drip-irrigated late-season peaches.
#         Irrig. Sci. 22:187-194.  [EQN 7]
#
#     Crop specific Fc-Kcb conversion:
#         Allen, R., and L. Pereira, 2009.  Estimating crop coefficients from
#         fraction of ground cover and height.  Irrig. Sci. 28:17-34.
#         [EQNS 10 (Kd); 7a (Kcb_full) using tree/vine Fr vals from Table 2; 5a (Kcb)]
#
#     """
#     fc_zero = img.fc.multiply(0)
#
#     # Crop-specific vine kc
#     kc2 = kc_crop_specific(img, fc_zero, 2, 69)
#
#     # Try crop-specific kc for trees, default back to generic
#     tree_nums = [
#         66, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77,
#         201, 203, 204, 210, 211, 212, 215, 217, 218, 220, 223]
#
#     trees_collec = ee.ImageCollection(\
#             list(map(\
#                 lambda num: kc_crop_specific(img, fc_zero, 3, num),
#                 tree_nums
#             ))\
#         )
#     kc3 = trees_collec.reduce(ee.Reducer.sum())
#
#     # Try crop-specific kc for field crops, default back to generic
#     field_nums = [
#         1, 2, 3, 4, 5, 6,
#         10, 11, 12, 13, 14,
#         21, 22, 23, 24, 25, 26, 27, 28, 29,
#         30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
#         41, 42, 43, 44, 45, 46, 47, 48, 49,
#         50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
#         60, 61, 80, 182,
#         202, 205, 206, 207, 208, 209,
#         213, 214, 216, 219,
#         221, 222, 224, 225, 226, 227, 228, 229,
#         230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
#         240, 241, 242, 243, 244, 245, 246, 247, 248, 249,
#         250, 254]
#
#     field_collec = ee.ImageCollection(\
#             list(map(\
#                 lambda num: kc_crop_specific(img, fc_zero, 1, num),
#                 field_nums
#             ))\
#         )
#     kc1 = field_collec.reduce(ee.Reducer.sum())
#
#     # Dealing with rice fields. For next version we'll do something
#     # more sophisticated. For now anything with ndvi less than 0.14
#     # gets a kc of 1.05
#     mask_rice = img.ndvi.lte(0.14).And(img.crop_class.eq(5))
#     # CGM - We aren't building a crop class of 5 yet but you could use the crop_type
#     # mask_rice = img.ndvi.lte(0.14).And(img.crop_type.eq(3))
#     kc5 = kc1.where(mask_rice, 1.05)
#     # mask_rice = self.ndvi.gt(0.14).And(self.crop_class.eq(5))
#     # kc5b = fc_zero.where(mask_rice, img_expr)
#     # kc5 = kc5a.add(kc5b)
#
#     # Add up all the Kcs
#     kc = kc1.add(kc2).add(kc3).add(kc5).clamp(0, 1.25)
#
#     # CGM - Set all non-ag cells to nodata
#     #   It might make more sense to do this to crop_type or crop_class
#     kc = kc.updateMask(img.crop_class.gt(0))
#
#     return kc.rename(['kc']).set(img._properties).double()
#
#
# # CGM - I really don't think passing the openet.sims.image object makes sense
# #   Doing that really hides what the inputs to the model are and it doesn't
# #   seem like it is needed since it is only a few parameters are being used
# #   (fc, ndvi, crop_class, etc.).
# def kc_crop_specific(img, zero, crop_class_num, crop_type_num, kc_min=0.15):
#     """Crop coefficient (Kc) calculation for a single crop
#
#     Parameters
#     ----------
#     img : openet.sims.Image
#     zero : ee.Image
#     crop_class_num : int
#     crop_type_num : int
#     kc_min : float, optional
#
#     Returns
#     -------
#     ee.Image
#
#     """
#
#     crop_prof = kc_help.make_profile(crop_type_num)
#     # CGM - crop_pixels isn't being used in this function?
#     crop_pixels = img.crop_type.eq(crop_type_num)
#
#     # Vine
#     if crop_type_num == 69:
#         kd = img.fc.multiply(1.5)\
#             .min(img.fc.pow(1 / (1 + 2)))\
#             .min(1)
#
#     # Trees
#     elif crop_class_num == 3:
#         # Generic tree - crop_type_num doesn't have specific coefficients
#         if crop_prof.h_max == -999:
#             kc_gen = zero.where(
#             img.crop_type.eq(crop_type_num),
#             img.fc.multiply(1.48).add(0.007))
#             return kc_gen
#         # Tree-specific coefficients
#         else:
#             # kd where fc > .5
#             kd1 = zero.where(img.fc.gt(0.5),
#                 img.fc.multiply(crop_prof.m_l)\
#                     .min(img.fc.pow(1 / (1 + crop_prof.h_max)))\
#                     .min(1))
#
#             # kd where fc <= .5
#             kd2 = zero.where(img.fc.lte(0.5),
#                 img.fc.multiply(crop_prof.m_l)\
#                     .min(img.fc.pow(1 / (1 + (crop_prof.h_max - 1))))\
#                     .min(1))
#
#             kd = kd1.add(kd2)
#
#     # Row crops
#     elif crop_class_num == 1:
#         if crop_prof.h_max == -999:
#             # Generic equation for annual crops
#             img_expr = img.fc.expression(
#                 "((b('fc') ** 2) * -0.4771) + (1.4047 * b('fc')) + 0.15")
#             kc_gen = zero.where(img.crop_type.eq(crop_type_num), img_expr)
#             return kc_gen
#         else:
#             # h = h_max*min((fc/0.7),1)
#             kd1 = zero.where(img.fc.divide(0.7).lte(1),
#                 img.fc.multiply(crop_prof.m_l)\
#                     .min(\
#                         img.fc.pow(
#                             img.fc.divide(0.7)\
#                                 .multiply(crop_prof.h_max)\
#                                 .pow(-1)\
#                                 .add(1)\
#                         )\
#                     )\
#                     .min(1))
#
#             kd2 = zero.where(img.fc.divide(0.7).gt(1),
#                 img.fc.multiply(crop_prof.m_l)\
#                     .min(img.fc.pow(1 / (1 + crop_prof.h_max)))\
#                     .min(1))
#             kd = kd1.add(kd2)
#
#     # CGM - I think DOY should be an input to this function instead of derived
#     #   here from img._date
#     #try:
#     doy = img._date.getRelative('day','year')
#     #except:
#     #    # print("DOY error for %s, setting to 20" )
#     #    doy = 20
#
#     kc_spec = zero.where(
#         img.crop_type.eq(crop_type_num),
#         kd.multiply(kc_help.kcb_full(doy, crop_prof).subtract(kc_min))\
#             .add(kc_min)\
#             .clamp(0, 1.1)
#     )
#
#     return kc_spec
#
#
# def kcb_full(doy, crop_prof):
#     """Basal crop coefficient (Kcb) for a given crop on day-of-year.
#
#     Parameters
#     ----------
#     doy : int
#     crop_prof : CropProfile
#
#     Returns
#     -------
#     ee.Number
#
#     """
#     return ee.Number(fr(doy, crop_prof))\
#         .multiply(min(1 + 0.1 * crop_prof.h_max, 1.2))
#
#
# def fr(doy, crop_prof):
#     """Reduction factor (f_r) for adjusting Kcb of tree crops
#
#     Estimated using a mean leaf stomatal resistance term.
#
#     Parameters
#     ----------
#     doy : int
#     crop_prof : CropProfile
#
#     Returns
#     -------
#     ee.Number
#
#     """
#     doy_gt_ls_stop = ee.Algorithms.If(
#         doy.gt(crop_prof.ls_stop), crop_prof.fr_end, 0)
#
#     doy_geq_ls_start_and_doy_leq_ls_stop = ee.Algorithms.If(
#         doy.gte(crop_prof.ls_start).And(doy.lte(crop_prof.ls_stop)),
#         ee.Number(crop_prof.fr_mid)\
#             .subtract(
#                 (doy.subtract(crop_prof.ls_start))\
#                 .divide(crop_prof.ls_stop - crop_prof.ls_start)\
#                 .multiply(crop_prof.fr_mid - crop_prof.fr_end)
#             ),
#         doy_gt_ls_stop)
#
#     doy_lt_ls_start = ee.Algorithms.If(
#         doy.lt(crop_prof.ls_start), crop_prof.fr_mid,
#         doy_geq_ls_start_and_doy_leq_ls_stop)
#
#     fr = ee.Algorithms.If(crop_prof.crop_class == 1, 1, doy_lt_ls_start)
#
#     return fr

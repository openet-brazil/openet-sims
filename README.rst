===================
OpenET - SIMS Model
===================

|version| |build|

**WARNING: This code is in development, is being provided without support, and is subject to change at any time without notification**

This repository provides an Earth Engine Python API based implementation of the SIMS model for computing evapotranspiration (ET).

Input Collections
=================

The SIMS model is currently implemented for the following Earth Engine image collections:

Landsat SR
 * LANDSAT/LC09/C02/T1_L2
 * LANDSAT/LC08/C02/T1_L2
 * LANDSAT/LE07/C02/T1_L2
 * LANDSAT/LT05/C02/T1_L2
 * LANDSAT/LT04/C02/T1_L2

Model Structure
===============

The primary way of interact with the SIMS model are through the "Collection" and "Image" classes.

Collection
==========

The Collection class should be used to generate image collections of ET (and and other model `Variables`_).  These collections can be for image "overpass" dates only or interpolated to daily, monthly, or annual time steps.  The collections can be built for multiple input collections types, such as merging Landsat 8 and Sentinel 2.

The Collection class is built based on a list of input collections ID's, a date range, and a study area geometry.

Required Inputs
---------------

collections
    List of Earth Engine collection IDs (see `Input Collections`_).
start_date
    ISO format start date string (i.e. YYYY-MM-DD) that is passed directly to the collection .filterDate() calls.
end_date
    ISO format end date string that is passed directly to .filterDate() calls.  The end date must be exclusive (i.e. data will go up to this date but not include it).
geometry
    ee.Geometry() that is passed to the collection .filterBounds() calls.
    All images with a footprint that intersects the geometry will be included.
et_reference_source
    Reference ET source collection ID  (see `Reference ET Sources`_).
et_reference_band
    Reference ET source band name.

Optional Inputs
---------------
cloud_cover_max
    Maximum cloud cover percentage.
    The input collections will be filtered to images with a cloud cover percentage less than this value.
    Optional, the default is 70 (%).
filter_args
    Custom filter arguments for teh input collections.
    This parameter is not yet fully implemented.
model_args
    A dictionary of argument to pass through to the Image class initialization.
    This parameter is not yet fully implemented.

Overpass Method
---------------

variables
    List of variables to calculate/return.

Interpolate Method
------------------

variables
    List of variables to calculate/return.
t_interval
    Time interval over which to interpolate and aggregate values.
    Choices: 'daily', 'monthly', 'annual', 'custom'
    Optional, the default is 'custom'.
interp_method
    Interpolation method.
    Choices: 'linear'
    Optional, the default is 'linear'.
interp_days
    Number of extra days before the start date and after the end date to include in the interpolation calculation.
    Optional, the default is 32.

Collection Examples
-------------------

.. code-block:: python

    import openet.sims as model

    overpass_coll = model.Collection(
            collections=['LANDSAT/LC08/C02/T1_L2'],
            start_date='2017-06-01',
            end_date='2017-09-01',
            geometry=ee.Geometry.Point(-121.5265, 38.7399),
            et_reference_source='IDAHO_EPSCOR/GRIDMET',
            et_reference_band='eto') \
        .overpass(variables=['et', 'et_reference', 'et_fraction'])

    monthly_coll = model.Collection(
            collections=['LANDSAT/LC08/C02/T1_L2'],
            start_date='2017-06-01',
            end_date='2017-09-01',
            geometry=ee.Geometry.Point(-121.5265, 38.7399),
            et_reference_source='IDAHO_EPSCOR/GRIDMET',
            et_reference_band='eto') \
        .interpolate(variables=['et', 'et_reference', 'et_fraction']
                     t_interval='monthly')

Image
=====

The Image class should be used to process a single image, an image collection with custom filtering, or to apply custom parameters to each image in a collection.

Typically the SIMS Image is initialized using one of the collection/sensor specific helper methods listed below (see below).  These methods rename the bands to a common naming scheme, apply basic cloud masking, and .

Image collections can be built by mapping one of the helper methods over an image collection.  Please see the `Image Mapping <examples/image_mapping.ipynb>`__ example notebook for more details.

The Image class can also be initialized using any Earth Engine image with an 'ndvi' band and a 'system:time_start' property.

Landsat Collection 2 Surface Reflectance (SR) Input Image
---------------------------------------------------------

To instantiate the class for a Landsat Collection 2 SR image, use the Image.from_landsat_c2_sr() method.

The input Landsat image must have the following bands and properties:

=================  =============================================
SATELLITE          Band Names
=================  =============================================
LANDSAT_4          SR_B1, SR_B2, SR_B3, SR_B4, SR_B5, SR_B7, SR_B6, QA_PIXEL
LANDSAT_5          SR_B1, SR_B2, SR_B3, SR_B4, SR_B5, SR_B7, SR_B6, QA_PIXEL
LANDSAT_7          SR_B1, SR_B2, SR_B3, SR_B4, SR_B5, SR_B7, SR_B6, QA_PIXEL
LANDSAT_8          SR_B2, SR_B3, SR_B4, SR_B5, SR_B6, SR_B7, SR_B10, QA_PIXEL
LANDSAT_9          SR_B2, SR_B3, SR_B4, SR_B5, SR_B6, SR_B7, SR_B10, QA_PIXEL
=================  =============================================

=================  =============================================
Property           Description
=================  =============================================
system:index       - Landsat Scene ID
                   - Must be in the Earth Engine format (e.g. LC08_044033_20170716)
system:time_start  Image datetime in milliseconds since 1970
SPACECRAFT_ID      - Used to determine which Landsat type (for band renaming)
                   - Must be: LANDSAT_4, LANDSAT_5, LANDSAT_7, LANDSAT_8, or LANDSAT_9
=================  =============================================

Image Example
-------------

.. code-block:: python

    import openet.sims as model
    et_img = model.Image.from_landsat_c2_sr(
        ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044033_20170716'),
        et_reference_source='IDAHO_EPSCOR/GRIDMET',
        et_reference_band='eto').et

Variables
=========

The SIMS model can compute the following variables:

ndvi
   Normalized difference vegetation index [unitless]
et_fraction
   Fraction of reference ET [unitless]
et_reference
   Reference ET [mm] (type will depend on `Reference ET`_ parameters)
et
   Actual ET [mm]

There is also a more general "calculate" method that can be used to return a multiband image of multiple variables (see example...)

Reference ET
============

The reference ET data source is controlled using the "et_reference_source" and "et_reference_band" parameters.

The model is expecting a grass reference ET (ETo) and will not return valid results if an alfalfa reference ET (ETr) is used.

Reference ET Sources
--------------------

GRIDMET
  | Collection ID: IDAHO_EPSCOR/GRIDMET
  | http://www.climatologylab.org/gridmet.html
  | Grass reference ET band: eto
Spatial CIMIS
  | Collection ID: projects/openet/assets/reference_et/california/cimis/daily/v1
  | https://cimis.water.ca.gov/SpatialData.aspx
  | Grass reference ET band: eto

Example Notebooks
=================

Detailed Jupyter Notebooks of the various approaches for calling the OpenET SIMS model are provided in the "examples" folder.

 * `Computing daily ET for a single Landsat image <examples/single_image.ipynb>`__
 * `Computing a collection of "overpass" ET images <examples/collection_overpass.ipynb>`__
 * `Computing a collection of interpolated monthly ET images <examples/collection_interpolate.ipynb>`__

Installation
============

The python OpenET SIMS module can be installed via pip:

.. code-block:: console

    pip install openet-sims

Dependencies
============

 * `earthengine-api <https://github.com/google/earthengine-api>`__
 * `openet-core <https://github.com/Open-ET/openet-core>`__

OpenET Namespace Package
========================

Each OpenET model is stored in the "openet" folder (namespace).  The model can then be imported as a "dot" submodule of the main openet module.

.. code-block:: console

    import openet.sims as model

Development and Testing
=======================

Please see the `CONTRIBUTING.rst <CONTRIBUTING.rst>`__.

References
==========



.. |build| image:: https://github.com/Open-ET/openet-sims/actions/workflows/build.yml/badge.svg
   :alt: Build status
   :target: https://github.com/Open-ET/openet-sims
.. |version| image:: https://badge.fury.io/py/openet-sims.svg
   :alt: Latest version on PyPI
   :target: https://badge.fury.io/py/openet-sims

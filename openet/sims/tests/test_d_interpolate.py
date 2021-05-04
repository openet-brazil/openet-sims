import datetime
import pprint

import ee
import pandas as pd
import pytest

import openet.sims.interpolate as interpolate
import openet.sims.utils as utils
import openet.sims as sims


def scene_coll(variables, et_fraction=0.4, et=5, ndvi=0.6):
    """Return a generic scene collection to test scene interpolation functions

    Parameters
    ----------
    variables : list
        The variables to return in the collection
    et_fraction : float
    et : float
    ndvi : float

    Returns
    -------
    ee.ImageCollection

    """
    img = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_044033_20170716') \
        .select(['B2']).double().multiply(0)
    mask = img.add(1).updateMask(1).uint8()

    time1 = ee.Number(ee.Date.fromYMD(2017, 7, 8).millis())
    time2 = ee.Number(ee.Date.fromYMD(2017, 7, 16).millis())
    time3 = ee.Number(ee.Date.fromYMD(2017, 7, 24).millis())

    # Mask and time bands currently get added on to the scene collection
    #   and images are unscaled just before interpolating in the export tool
    scene_img = ee.Image([img.add(et_fraction), img.add(et), img.add(ndvi), mask])\
        .rename(['et_fraction', 'et', 'ndvi', 'mask'])
    scene_coll = ee.ImageCollection([
        scene_img.addBands([img.add(time1).rename('time')]) \
            .set({'system:index': 'LE07_044033_20170708',
                  'system:time_start': time1}),
        scene_img.addBands([img.add(time2).rename('time')]) \
            .set({'system:index': 'LC08_044033_20170716',
                  'system:time_start': time2}),
        scene_img.addBands([img.add(time3).rename('time')]) \
            .set({'system:index': 'LE07_044033_20170724',
                  'system:time_start': time3}),
    ])
    return scene_coll.select(variables)


def test_from_scene_et_fraction_daily_values(tol=0.0001):
    output_coll = interpolate.from_scene_et_fraction(
        scene_coll(['et_fraction', 'ndvi', 'time', 'mask']),
        start_date='2017-07-01', end_date='2017-08-01',
        variables=['et', 'et_reference', 'et_fraction', 'ndvi'],
        interp_args={'interp_method': 'linear', 'interp_days': 32,},
        model_args={'et_reference_source': 'IDAHO_EPSCOR/GRIDMET',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 1.0,
                    'et_reference_resample': 'nearest'},
        t_interval='daily')

    TEST_POINT = (-121.5265, 38.7399)
    output = utils.point_coll_value(output_coll, TEST_POINT, scale=10)
    assert abs(output['ndvi']['2017-07-10'] - 0.6) <= tol
    assert abs(output['et_fraction']['2017-07-10'] - 0.4) <= tol
    assert abs(output['et_reference']['2017-07-10'] - 8.0) <= tol
    assert abs(output['et']['2017-07-10'] - (8.0 * 0.4)) <= tol
    assert abs(output['et_fraction']['2017-07-01'] - 0.4) <= tol
    assert abs(output['et_fraction']['2017-07-31'] - 0.4) <= tol
    assert '2017-08-01' not in output['et_fraction'].keys()
    # assert output['count']['2017-07-01'] == 3


def test_from_scene_et_fraction_monthly_values(tol=0.0001):
    output_coll = interpolate.from_scene_et_fraction(
        scene_coll(['et_fraction', 'ndvi', 'time', 'mask']),
        start_date='2017-07-01', end_date='2017-08-01',
        variables=['et', 'et_reference', 'et_fraction', 'ndvi', 'count'],
        interp_args={'interp_method': 'linear', 'interp_days': 32},
        model_args={'et_reference_source': 'IDAHO_EPSCOR/GRIDMET',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 1.0,
                    'et_reference_resample': 'nearest'},
        t_interval='monthly')

    TEST_POINT = (-121.5265, 38.7399)
    output = utils.point_coll_value(output_coll, TEST_POINT, scale=10)
    assert abs(output['ndvi']['2017-07-01'] - 0.6) <= tol
    assert abs(output['et_fraction']['2017-07-01'] - 0.4) <= tol
    assert abs(output['et_reference']['2017-07-01'] - 236.5) <= tol
    assert abs(output['et']['2017-07-01'] - (236.5 * 0.4)) <= tol
    assert output['count']['2017-07-01'] == 3


def test_from_scene_et_fraction_custom_values(tol=0.0001):
    output_coll = interpolate.from_scene_et_fraction(
        scene_coll(['et_fraction', 'ndvi', 'time', 'mask']),
        start_date='2017-07-01', end_date='2017-08-01',
        variables=['et', 'et_reference', 'et_fraction', 'ndvi', 'count'],
        interp_args={'interp_method': 'linear', 'interp_days': 32},
        model_args={'et_reference_source': 'IDAHO_EPSCOR/GRIDMET',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 1.0,
                    'et_reference_resample': 'nearest'},
        t_interval='custom')

    TEST_POINT = (-121.5265, 38.7399)
    output = utils.point_coll_value(output_coll, TEST_POINT, scale=10)
    assert abs(output['ndvi']['2017-07-01'] - 0.6) <= tol
    assert abs(output['et_fraction']['2017-07-01'] - 0.4) <= tol
    assert abs(output['et_reference']['2017-07-01'] - 236.5) <= tol
    assert abs(output['et']['2017-07-01'] - (236.5 * 0.4)) <= tol
    assert output['count']['2017-07-01'] == 3


def test_from_scene_et_fraction_monthly_et_reference_factor(tol=0.0001):
    output_coll = interpolate.from_scene_et_fraction(
        scene_coll(['et_fraction', 'ndvi', 'time', 'mask']),
        start_date='2017-07-01', end_date='2017-08-01',
        variables=['et', 'et_reference', 'et_fraction', 'ndvi', 'count'],
        interp_args={'interp_method': 'linear', 'interp_days': 32},
        model_args={'et_reference_source': 'IDAHO_EPSCOR/GRIDMET',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 0.5,
                    'et_reference_resample': 'nearest'},
        t_interval='monthly')

    TEST_POINT = (-121.5265, 38.7399)
    output = utils.point_coll_value(output_coll, TEST_POINT, scale=10)
    assert abs(output['ndvi']['2017-07-01'] - 0.6) <= tol
    assert abs(output['et_fraction']['2017-07-01'] - 0.4) <= tol
    assert abs(output['et_reference']['2017-07-01'] - 236.5 * 0.5) <= tol
    assert abs(output['et']['2017-07-01'] - (236.5 * 0.5 * 0.4)) <= tol
    assert output['count']['2017-07-01'] == 3


# CGM - Resampling is not being applied so this should be equal to nearest
def test_from_scene_et_fraction_monthly_et_reference_resample(tol=0.0001):
    output_coll = interpolate.from_scene_et_fraction(
        scene_coll(['et_fraction', 'ndvi', 'time', 'mask']),
        start_date='2017-07-01', end_date='2017-08-01',
        variables=['et', 'et_reference', 'et_fraction', 'ndvi', 'count'],
        interp_args={'interp_method': 'linear', 'interp_days': 32},
        model_args={'et_reference_source': 'IDAHO_EPSCOR/GRIDMET',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 1.0,
                    'et_reference_resample': 'bilinear'},
        t_interval='monthly')

    TEST_POINT = (-121.5265, 38.7399)
    output = utils.point_coll_value(output_coll, TEST_POINT, scale=10)
    assert abs(output['ndvi']['2017-07-01'] - 0.6) <= tol
    assert abs(output['et_fraction']['2017-07-01'] - 0.4) <= tol
    assert abs(output['et_reference']['2017-07-01'] - 236.5) <= tol
    assert abs(output['et']['2017-07-01'] - (236.5 * 0.4)) <= tol
    assert output['count']['2017-07-01'] == 3


@pytest.mark.parametrize(
    'landsat_coll_id',
    [
        'LANDSAT/LC08/C01/T1_SR',
        'LANDSAT/LC08/C02/T1_L2',
    ]
)
def test_soil_evaporation_landsat(landsat_coll_id, tol=0.001):
    TEST_POINT = (-120.201, 36.1696)
    et_reference_source = 'IDAHO_EPSCOR/GRIDMET'
    et_reference_band = 'eto'
    start_date = '2018-02-23'
    end_date = '2018-03-08'

    landsat_coll = ee.ImageCollection(landsat_coll_id)\
        .filterDate(start_date, end_date)\
        .filterBounds(ee.Geometry.Point(TEST_POINT))

    zero = landsat_coll.first().select(1).double().multiply(0)

    def make_et_frac(img):
        if 'C01' in landsat_coll_id:
            et_img = sims.Image.from_landsat_c1_sr(img,
                    et_reference_source=et_reference_source,
                    et_reference_band=et_reference_band)\
                .calculate(['ndvi', 'et_reference', 'et_fraction', 'et'])
        elif 'C02' in landsat_coll_id:
            et_img = sims.Image.from_landsat_c2_sr(img,
                    et_reference_source=et_reference_source,
                    et_reference_band=et_reference_band)\
                .calculate(['ndvi', 'et_reference', 'et_fraction', 'et'])

        time = ee.Number(img.get('system:time_start'))
        et_img = et_img.addBands([zero.add(time).rename('time')])
        return et_img

    test_imgs = landsat_coll.map(make_et_frac)
    normal_coll = interpolate.from_scene_et_fraction(
        test_imgs,
        start_date=start_date,
        end_date=end_date,
        variables=['et_reference', 'et_fraction', 'et'],
        interp_args={'interp_method': 'linear', 'interp_days': 14},
        model_args={'et_reference_source': 'IDAHO_EPSCOR/GRIDMET',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 1.0,
                    'et_reference_resample': 'nearest'},
        t_interval='daily')

    wb_coll = interpolate.from_scene_et_fraction(
        test_imgs,
        start_date=start_date,
        end_date=end_date,
        variables=['et_reference', 'et_fraction', 'ke', 'et', 'ndvi'],
        interp_args={'interp_method': 'linear', 'interp_days': 14,
                     'estimate_soil_evaporation': True},
        model_args={'et_reference_source': 'IDAHO_EPSCOR/GRIDMET',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 1.0,
                    'et_reference_resample': 'nearest'},
        t_interval='daily')

    normal = utils.point_coll_value(normal_coll, TEST_POINT, scale=30)
    wb = utils.point_coll_value(wb_coll, TEST_POINT, scale=30)

    for date in normal['et'].keys():
        # check that ET with soil evap >= ET without soil evap
        assert wb['et'][date] >= normal['et'][date]


# Global constants for soil evap tests
TEST_POINT = (-120.201, 36.1696)
et_reference_source = 'IDAHO_EPSCOR/GRIDMET'
et_reference_band = 'eto'
start_date = '2018-02-10'
end_date = '2018-03-14'
comp_data = pd.read_csv('openet/sims/tests/ee_wb_valid.csv')

@pytest.fixture
def synth_test_imgs():
    landsat_coll_id = f'LANDSAT/LC08/C01/T1_SR'
    landsat_coll = ee.ImageCollection(landsat_coll_id)\
        .filterDate(start_date, end_date)\
        .filterBounds(ee.Geometry.Point(TEST_POINT))

    first = landsat_coll.first().select(['B2']).double().multiply(0)
    zero = first

    first_day = comp_data.iloc[0]
    dt = datetime.datetime(2018, 1, 1) + datetime.timedelta(first_day.doy-1)
    time = ee.Number(ee.Date.fromYMD(2018, dt.month, dt.day).millis())
    first_img = zero.set({'system:time_start': time}) \
        .addBands([zero.add(time).rename('time')]) \
        .addBands([zero.add(first_day.ndvi_interp).rename('ndvi')]) \
        .addBands([zero.add(first_day.kc).rename('et_fraction')]) \
        .addBands([zero.add(first_day.eto).rename('et_reference')]) \
        .select(['time', 'ndvi', 'et_fraction', 'et_reference'])

    test_imgs = ee.ImageCollection(first_img)

    for i, doy in enumerate(comp_data.doy):
        if i == 0:
            continue

        day = comp_data.iloc[i]
        dt = datetime.datetime(2018, 1, 1) + datetime.timedelta(doy-1)
        time = ee.Number(ee.Date.fromYMD(2018, dt.month, dt.day).millis())
        next_img = zero.set({'system:time_start': time}) \
            .addBands([zero.add(time).rename('time')]) \
            .addBands([zero.add(day.ndvi_interp).rename('ndvi')]) \
            .addBands([zero.add(day.kc).rename('et_fraction')]) \
            .addBands([zero.add(day.eto).rename('et_reference')]) \
            .select(['time', 'ndvi', 'et_fraction', 'et_reference'])
        test_imgs = test_imgs.merge(ee.ImageCollection(next_img))
    
    return test_imgs


def test_soil_evaporation_synthetic(synth_test_imgs, tol=0.001):
    test_imgs = synth_test_imgs

    normal_coll = interpolate.from_scene_et_fraction(
        test_imgs,
        start_date=start_date,
        end_date=end_date,
        variables=['et_reference', 'et_fraction', 'et', 'ndvi'],
        interp_args={'interp_method': 'linear', 'interp_days': 10},
        model_args={'et_reference_source': 'provided',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 0.85,
                    'et_reference_resample': 'nearest'},
        t_interval='daily',
    )

    wb_coll = interpolate.from_scene_et_fraction(
        test_imgs,
        start_date=start_date,
        end_date=end_date,
        variables=['et_reference', 'et_fraction', 'ke', 'et', 'ndvi', 'precip'],
        interp_args={'interp_method': 'linear', 'interp_days': 10,
                     'estimate_soil_evaporation': True},
        model_args={'et_reference_source': 'provided',
                    'et_reference_band': 'eto',
                    'et_reference_factor': 0.85,
                    'et_reference_resample': 'nearest'},
        t_interval='daily',
    )

    normal = utils.point_coll_value(normal_coll, TEST_POINT, scale=30)
    wb = utils.point_coll_value(wb_coll, TEST_POINT, scale=30)

    # check that wb ET >= regular SIMS ET
    for date in normal['et'].keys():
        assert wb['et'][date] >= normal['et'][date]

    def get_doy(dt_str):
        return datetime.datetime.strptime(dt_str, '%Y-%m-%d').timetuple().tm_yday

    wb_df = pd.DataFrame(wb)
    wb_df = wb_df.reset_index()
    wb_df['doy'] = wb_df['index'].apply(get_doy)

    for i in range(59, 72):
        assert abs(wb_df[wb_df.doy==i]['et'].iloc[0] - comp_data[comp_data.doy==i]['etc'].iloc[0]) < tol


def test_soil_evap_fails_without_ndvi(synth_test_imgs):
    test_imgs = synth_test_imgs

    # daily_ke raises exception if `ndvi` band not present
    try:
        wb_coll = interpolate.from_scene_et_fraction(
            test_imgs,
            start_date=start_date,
            end_date=end_date,
            variables=['et_reference', 'et_fraction', 'ke', 'et', 'precip'],
            interp_args={'interp_method': 'linear', 'interp_days': 10,
                         'estimate_soil_evaporation': True},
            model_args={'et_reference_source': 'provided',
                        'et_reference_band': 'eto',
                        'et_reference_factor': 0.85,
                        'et_reference_resample': 'nearest'},
            t_interval='daily')
        # if from_scene_et_fraction doesn't raise, assert False
        assert False
    except:
        pass


def test_daily_ke(synth_test_imgs):
    test_imgs = synth_test_imgs

    model_args = {'et_reference_source': 'provided',
                  'et_reference_band': 'eto',
                  'et_reference_factor': 0.85,
                  'et_reference_resample': 'nearest'}

    evap_imgs = interpolate.daily_ke(
        test_imgs,
        model_args,  # CGM - model_args isn't used by daily_ke
        precip_source='IDAHO_EPSCOR/GRIDMET',
        precip_band='pr',
        fc_source='projects/eeflux/soils/gsmsoil_mu_a_fc_10cm_albers_100',
        fc_band='b1',
        wp_source='projects/eeflux/soils/gsmsoil_mu_a_wp_10cm_albers_100',
        wp_band='b1',
    )

    base_ts = utils.point_coll_value(test_imgs, TEST_POINT, scale=30)
    base_df = pd.DataFrame(base_ts).reset_index()
    
    evap_ts = utils.point_coll_value(evap_imgs, TEST_POINT, scale=30)
    evap_df = pd.DataFrame(evap_ts).reset_index()

    # Iterate through time series, stop one before end to avoid out of bounds
    # in "check next day state variable" tests
    for i in range(evap_df.shape[0]-1):
        # Check  that soil evap only increase et fraction
        assert base_df.loc[i, 'et_fraction'] <= evap_df.loc[i, 'et_fraction']

        # Check that etc strictly greater than etcb if it rained and
        # kcb isn't maxed out
        if evap_df.loc[i, 'precip'] > 0 and base_df.loc[i, 'et_fraction'] < 1.15:
            assert base_df.loc[i+1, 'et_fraction'] < evap_df.loc[i+1, 'et_fraction']

        # Check evaporation reduction coefficients
        # Should be nonzero next day when depletion > REW
        if evap_df.loc[i, 'de'] > evap_df.de_rew.max():
            assert evap_df.loc[i+1, 'kr'] < 1

        # should be one next day when depletion is less than REW
        if evap_df.loc[i, 'de'] < evap_df.de_rew.max():
            assert evap_df.loc[i+1, 'kr'] == 1

        # should be zero next day when fully depleted
        if evap_df.loc[i, 'de'] == evap_df.de.max():
            assert evap_df.loc[i+1, 'kr'] == 0

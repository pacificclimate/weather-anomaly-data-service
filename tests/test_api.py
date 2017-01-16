from pytest import mark, approx
from pycds.climate_baseline_helpers import pcic_climate_variable_network_name
from wads.api import baseline, weather


@mark.parametrize('variable, month', [
    ('tmax', 1),
    ('tmin', 2),
    ('precip', 3),
])
def test_baseline(baseline_session, histories, variable, month):
    result = baseline(baseline_session, variable, month)
    assert sorted(result, key=lambda r: r['station_name']) == \
           [{
                'network_name': pcic_climate_variable_network_name,
                'station_native_id': history.station.native_id,
                'station_name': history.station_name,
                'lon': history.lon,
                'lat': history.lat,
                'elevation': history.elevation,
                'datum': float(month)
            } for history in histories]


@mark.parametrize('variable, year, month, cell_method, statistic', [
    ('tmax', 2000, 1, 'time: point', 23.0),
    ('tmin', 2000, 1, 'time: point', 0.0),
    ('precip', 2000, 1, 'time: sum', float(24 * 31)),
])
def test_weather(weather_session, histories, variable, year, month, cell_method, statistic):
    result = weather(weather_session, variable, year, month)
    assert sorted(result, key=lambda r: r['station_name']) == \
           [{
                'network_name': 'Station Network',
                'station_native_id': history.station.native_id,
                'station_name': history.station_name,
                'lon': history.lon,
                'lat': history.lat,
                'elevation': history.elevation,
                'cell_method': cell_method,
                'statistic': statistic,
                'data_coverage': approx(1.0)
            } for history in histories]

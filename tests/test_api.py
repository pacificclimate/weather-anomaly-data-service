from pytest import mark, approx
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
                'station_name': history.station_name,
                'lon': history.lon,
                'lat': history.lat,
                'elevation': history.elevation,
                'datum': float(month)
            } for history in histories]


@mark.parametrize('variable, year, month, statistic', [
    ('tmax', 2000, 1, 23.0),
    ('tmin', 2000, 1, 0.0),
    ('precip', 2000, 1, float(24 * 31)),
])
def test_weather(weather_session, histories, variable, year, month, statistic):
    result = weather(weather_session, variable, year, month)
    assert sorted(result, key=lambda r: r['station_name']) == \
           [{
                'station_name': history.station_name,
                'lon': history.lon,
                'lat': history.lat,
                'elevation': history.elevation,
                'statistic': statistic,
                'data_coverage': approx(1.0)
            } for history in histories]

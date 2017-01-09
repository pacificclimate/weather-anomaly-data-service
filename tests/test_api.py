from pytest import mark
from wads.api import baseline


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
from pytest import mark
import json

@mark.parametrize('route, status', [
    ('/foo', 404),
    ('/baseline/tmax;0', 404),
    ('/baseline/tmax;1', 200),
    ('/baseline/tmax;5', 200),
    ('/baseline/tmax;12', 200),
    ('/baseline/tmax;13', 404),
    ('/baseline/tmin;1', 200),
    ('/baseline/precip;1', 200),
    ('/baseline/bad;1', 404),
    ('/weather/tmax;1849-1', 404),
    ('/weather/tmax;1850-0', 404),
    ('/weather/tmax;1850-1', 200),
    ('/weather/tmax;1850-12', 200),
    ('/weather/tmax;1850-13', 404),
    ('/weather/tmax;2000-1', 200),
    ('/weather/tmax;2100-12', 200),
    ('/weather/tmax;2101-1', 404),
    ('/weather/tmin;1850-1', 200),
    ('/weather/precip;1850-1', 200),
    ('/weather/bad;1850-1', 404),
])
def test_route_validity(app, route, status):
    with app.test_client() as client:
        response = client.get(route)
        assert response.status_code == status


@mark.parametrize('route, data', [
    ('/baseline/tmax;1', {u'dataset': u'baseline', u'variable': u'tmax', u'month': 1}),
    ('/weather/tmax;2000-1', {u'dataset': u'weather', u'variable': u'tmax', u'year': 2000, u'month': 1})
])
def test_route_response_data(app, route, data):
    with app.test_client() as client:
        response = client.get(route)
        assert json.loads(response.data) == data

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
    ('/weather/tmax;1850', 404),
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
@mark.usefixtures('session')   # need an empty database schema
def test_route_validity(app, route, status):
    with app.test_client() as client:
        response = client.get(route)
        assert response.status_code == status


@mark.parametrize('route', [
    ('/baseline/tmax;1'),
    ('/weather/tmax;2000-1'),
])
@mark.usefixtures('session')
def test_route_response_data(app, route):
    with app.test_client() as client:
        response = client.get(route)
        data = json.loads(response.data.decode('utf-8'))
        assert type(data) is list

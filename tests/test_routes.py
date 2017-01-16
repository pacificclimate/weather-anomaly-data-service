"""Tests for API routing and result processing. These tests are only of the routing and data
handling, not of the queries to the database (the latter are tested in test_api.py).

It's unnecessary and undesirable to invoke the database for these tests, so we mock the backend
query methods `baseline` and `weather` with a replacement function that returns a fixed,
known response. This is the function `mock`, which can serve for both `baseline` and `weather`.
"""

from pytest import mark
import json
import wads.api


def mock(s, **kwargs):
    """Mock for wads.api.method functions, e.g, wads.api.method['backend']"""
    return ['info']


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
def test_route_validity(monkeypatch, test_client, route, status):
    monkeypatch.setitem(wads.api.method, 'baseline', mock)
    monkeypatch.setitem(wads.api.method, 'weather', mock)
    response = test_client.get(route)
    assert response.status_code == status


@mark.parametrize('route', [
    ('/baseline/tmax;1'),
    ('/weather/tmax;2000-1'),
])
def test_route_response_data(monkeypatch, test_client, route):
    monkeypatch.setitem(wads.api.method, 'baseline', mock)
    monkeypatch.setitem(wads.api.method, 'weather', mock)
    response = test_client.get(route)
    data = json.loads(response.data.decode('utf-8'))
    assert data == ['info']

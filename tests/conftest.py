import datetime

from pytest import fixture
import testing.postgresql

from flask_sqlalchemy import SQLAlchemy

import pycds
from pycds import Network, Station, History, Variable, DerivedValue, Obs
from pycds.weather_anomaly import \
    DailyMaxTemperature, DailyMinTemperature, \
    MonthlyAverageOfDailyMaxTemperature, MonthlyAverageOfDailyMinTemperature, MonthlyTotalPrecipitation

from wads import get_app


# app, db, session fixtures based on http://alexmic.net/flask-sqlalchemy-pytest/

@fixture(scope='session')
def app():
    """Session-wide test Flask application"""
    with testing.postgresql.Postgresql() as pg:
        config_override = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': pg.url()
        }
        app = get_app(config_override)

        ctx = app.app_context()
        ctx.push()

        yield app

        ctx.pop()


@fixture(scope='session')
def test_client(app):
    with app.test_client() as client:
        yield client


@fixture(scope='session')
def db(app):
    """Session-wide test database"""
    db = SQLAlchemy(app)

    db.engine.execute("create extension postgis")
    pycds.Base.metadata.create_all(bind=db.engine)
    # TODO: Uncomment when full release of PyCDS with WA views
    pycds.weather_anomaly.Base.metadata.create_all(bind=db.engine)

    yield db

    # FIXME: Database hang on teardown
    # Irony: Attempting to tear down the database properly causes the tests to hang at the the end.
    # Workaround: Not tearing down the database prevents the hang, and causes no other apparent problems.
    # A similar problem with a more elegant solution is documented at
    # http://docs.sqlalchemy.org/en/latest/faq/metadata_schema.html#my-program-is-hanging-when-i-say-table-drop-metadata-drop-all
    # but the solution (to close connections before dropping tables) does not work. The `session` fixture does close
    # its connection as part of its teardown. That should work, but apparently not for 'drop extension postgis cascade'
    #
    # Nominally, the following commented out code ought to work, but it hangs at the indicated line

    # print('@fixture db: TEARDOWN')
    # db.engine.execute("drop extension postgis cascade")  # >>> hangs here
    # print('@fixture db: drop_all')
    # pycds.Base.metadata.drop_all(bind=db.engine)
    # # TODO: Uncomment when full release of PyCDS with WA views
    # # pycds.weather_anomaly.Base.metadata.drop_all(bind=db.engine)


@fixture(scope='function')
def session(db):
    """Single-test database session. All session actions are wrapped in a transaction and rolled back on teardown"""
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    db.session = session

    yield session

    transaction.rollback()
    connection.close()
    session.remove()


@fixture(scope='function')
def stn_networks():
    """Networks for stations"""
    return [Network(name='Station Network')]


@fixture(scope='function')
def stations(stn_networks):
    """Stations, some for each network"""
    return [Station(native_id=str(j*10+i), network=nw) for j, nw in enumerate(stn_networks) for i in range(0, 4)]


@fixture(scope='function')
def histories(stations):
    """Histories, one for each station"""
    return [History(
        station=station,
        station_name='Station {name}'.format(name=station.native_id),
        lon=-123.0,
        lat=48.5,
        elevation= 100.0 + i,
        sdate=datetime.datetime(2000, 1, 1),
        freq='1-hourly'
    ) for i, station in enumerate(stations)]


@fixture(scope='function')
def cv_network():
    """Network for baseline climate variables; name is prescribed by pycds"""
    return Network(name=pycds.climate_baseline_helpers.pcic_climate_variable_network_name)


@fixture(scope='function')
def cv_variables(cv_network):
    """Baseline climate variables in the climate network"""
    return [Variable(name=name, network=cv_network)
            for name in 'Tx_Climatology Tn_Climatology Precip_Climatology'.split()]


@fixture(scope='function')
def cv_values(cv_variables, histories):
    """Values for each baseline climate variable for each station for each month"""
    baseline_year = 2000
    baseline_day = 15  # fudged, but should not matter
    baseline_hour = 23
    return [DerivedValue(
        time=datetime.datetime(baseline_year, month, baseline_day, baseline_hour),
        datum=float(month),
        variable=variable,
        history=history
    ) for variable in cv_variables for history in histories for month in range(1, 13)]


@fixture(scope='function')
def stations_session(session, stn_networks, stations, histories):
    session.add_all(stn_networks)
    session.add_all(stations)
    session.add_all(histories)
    session.commit()
    yield session


@fixture(scope='function')
def baseline_session(stations_session, cv_network, cv_variables, cv_values):
    """Session containing data for testing baseline query"""
    stations_session.add(cv_network)
    stations_session.add_all(cv_variables)
    stations_session.add_all(cv_values)
    stations_session.commit()
    yield stations_session


@fixture(scope='function')
def air_temp_variables(stn_networks):
    """Variables for air temperature observations in the weather (station) networks"""
    return [Variable(standard_name='air_temperature', cell_method='time: point', network=network)
            for network in stn_networks]


@fixture(scope='function')
def precip_variables(stn_networks):
    """Variables for precipitation observations in the weather (station) networks"""
    return [Variable(standard_name='lwe_thickness_of_precipitation_amount', cell_method='time: sum', network=network)
            for network in stn_networks]


@fixture(scope='function')
def wx_values(stn_networks):
    """Values (observations) for each weather variable for each station for some times"""
    year = 2000
    month = 1
    days = range(1, 32)
    hours = range(0, 24)
    temps = [Obs(variable=network.variables[0], history=history,
                 time=datetime.datetime(year, month, day, hour), datum=float(hour))
             for network in stn_networks for station in network.stations for history in station.histories
             for day in days for hour in hours]
    precips = [Obs(variable=network.variables[1], history=history,
                   time=datetime.datetime(year, month, day, hour), datum=1.0)
               for network in stn_networks for station in network.stations for history in station.histories
               for day in days for hour in hours]
    return temps + precips


@fixture(scope='function')
def weather_session(stations_session, air_temp_variables, precip_variables, wx_values):
    """Session containing data for testing weather query"""
    stations_session.add_all(air_temp_variables)
    stations_session.add_all(precip_variables)
    stations_session.add_all(wx_values)
    stations_session.commit()
    for view in [DailyMaxTemperature, DailyMinTemperature,
                 MonthlyAverageOfDailyMaxTemperature, MonthlyAverageOfDailyMinTemperature, MonthlyTotalPrecipitation]:
        view.create(stations_session)
    yield stations_session

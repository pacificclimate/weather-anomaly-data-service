import datetime

from pytest import fixture
import testing.postgresql

from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import DDL, CreateSchema

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
    # pycds.weather_anomaly.Base.metadata.drop_all(bind=db.engine)


@fixture(scope='session')
def engine(db):
    """Session-wide database engine"""
    engine = db.engine
    engine.execute("create extension postgis")
    engine.execute(CreateSchema('crmp'))
    pycds.Base.metadata.create_all(bind=engine)
    # TODO: Is this CREATE OR REPLACE FUNCTION necessary?
    sqlalchemy.event.listen(
        pycds.weather_anomaly.Base.metadata,
        'before_create',
        DDL('''
                CREATE OR REPLACE FUNCTION crmp.DaysInMonth(date) RETURNS double precision AS
                $$
                    SELECT EXTRACT(DAY FROM CAST(date_trunc('month', $1) + interval '1 month' - interval '1 day'
                    as timestamp));
                $$ LANGUAGE sql;
            ''')
    )
    pycds.weather_anomaly.Base.metadata.create_all(bind=engine)

    yield engine

@fixture(scope='function')
def session(engine):
    """Single-test database session. All session actions are rolled back on teardown"""
    session = sessionmaker(bind=engine)()
    # Default search path is `"$user", public`. Need to reset that to search crmp (for our db/orm content) and
    # public (for postgis functions)
    session.execute('SET search_path TO crmp, public')
    # print('\nsearch_path', [r for r in session.execute('SHOW search_path')])
    yield session
    session.rollback()
    session.close()


@fixture(scope='function')
def stn_networks():
    """Networks for stations"""
    return [Network(name='Station Network')]


@fixture(scope='function')
def stations(stn_networks):
    """Stations, 2 for each network"""
    return [Station(native_id=str(j*10+i), network=nw) for j, nw in enumerate(stn_networks) for i in range(2)]


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
    session.flush()
    yield session


@fixture(scope='function')
def baseline_session(stations_session, cv_network, cv_variables, cv_values):
    """Session containing data for testing baseline query"""
    stations_session.add(cv_network)
    stations_session.add_all(cv_variables)
    stations_session.add_all(cv_values)
    stations_session.flush()
    yield stations_session


@fixture(scope='function')
def air_temp_variables(stn_networks):
    """Variables for air temperature observations in the weather (station) networks"""
    return [Variable(network=network,
                     name='{} air temp'.format(network.name),
                     standard_name='air_temperature',
                     cell_method='time: point')
            for network in stn_networks]


@fixture(scope='function')
def precip_variables(stn_networks):
    """Variables for precipitation observations in the weather (station) networks.
    Returns two sets of variables per network: lwe precipitation and snowfall thickness. Both types are processed
    by MonthlyTotalPrecipitation, but only lwe should be returned by the weather API."""
    return [Variable(network=network,
                     name='{} lwe precip'.format(network.name),
                     standard_name='lwe_thickness_of_precipitation_amount',
                     cell_method='time: sum')
            for network in stn_networks] \
           + \
           [Variable(network=network, name='{} snowfall'.format(network.name),
                     standard_name='thickness_of_snowfall_amount', cell_method='time: sum')
            for network in stn_networks]


# Constants for weather value fixtures
year = 2000
month = 1
days = range(1, 32)
hours = range(0, 24)


@fixture(scope='function')
def temp_values(air_temp_variables):
    """Values (observations) for the temperature variable for each station for each hour of each day of the month of
    Jan 2000"""
    return [Obs(variable=variable,
                history=station.histories[-1], # last history is latest
                time=datetime.datetime(year, month, day, hour),
                datum=float(hour))
            for variable in air_temp_variables
            for station in variable.network.stations
            for day in days
            for hour in hours]


@fixture(scope='function')
def precip_values(precip_variables):
    """Values (observations) for the precipitation variables for each station for each hour of each day of the month of
    Jan 2000"""
    return [Obs(variable=variable,
                history=station.histories[-1], # last history is latest
                time=datetime.datetime(year, month, day, hour),
                datum=1.0)
            for variable in precip_variables
            for station in variable.network.stations
            for day in days
            for hour in hours]


@fixture(scope='function')
def weather_session(stations_session, air_temp_variables, precip_variables, temp_values, precip_values):
    """Session containing data for testing weather query"""
    stations_session.add_all(air_temp_variables)
    stations_session.add_all(precip_variables)
    stations_session.add_all(temp_values)
    stations_session.add_all(precip_values)
    stations_session.flush()
    for view in [DailyMaxTemperature, DailyMinTemperature,
                 MonthlyAverageOfDailyMaxTemperature, MonthlyAverageOfDailyMinTemperature, MonthlyTotalPrecipitation]:
        view.create(stations_session)
    yield stations_session

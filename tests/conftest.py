import pytest
from pytest import fixture
import testing.postgresql

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import pycds

from was import get_app


# app, db, session fixtures based on http://alexmic.net/flask-sqlalchemy-pytest/

@fixture(scope='session')
def app():
    """Session-wide test Flask application"""
    with testing.postgresql.Postgresql() as pg:
        config_override = {
            'SQLALCHEMY_DATABASE_URI': pg.url()
        }
        app = get_app(config_override)

        ctx = app.app_context()
        ctx.push()

        yield app

        ctx.pop()


@fixture(scope='session')
def db(app):
    """Session-wide test database"""
    db = SQLAlchemy(app)

    db.engine.execute("create extension postgis")
    pycds.Base.metadata.create_all(bind=db.engine)
    # pycds.weather_anomaly.Base.metadata.create_all(bind=db.engine)

    yield db

    db.engine.execute("drop extension postgis cascade")
    pycds.Base.metadata.drop_all(bind=db.engine)
    # pycds.weather_anomaly.Base.metadata.drop_all(bind=db.engine)


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

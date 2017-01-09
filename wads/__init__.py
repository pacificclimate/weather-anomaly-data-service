import os

from flask import Flask
from flask.ext.cors import CORS

from wads.routes import add_routes


def get_app(config_override={}):
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'CRMP_DSN', 'postgresql://httpd_meta@monsoon.pcic.uvic.ca/crmp') # FIXME: Correct default database URI
    app.config.update(config_override)
    add_routes(app)
    return app
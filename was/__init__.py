import os

from flask import Flask
from flask.ext.cors import CORS

from was.routes import add_routes


def get_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'CRMP_DSN', 'postgresql://httpd_meta@monsoon.pcic.uvic.ca/crmp') # FIXME: Correct default database URI
    add_routes(app)
    return app
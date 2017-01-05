from werkzeug.routing import BaseConverter, IntegerConverter
from flask.ext.sqlalchemy import SQLAlchemy
import was.api


class ValidYearConverter(IntegerConverter):
    """This converter only accepts integer values between 1850 and 2100::

        Rule('/page/<valid_year:value>')

    This converter does not support negative values.

    :param map: the :class:`Map`.
    :param fixed_digits: the number of fixed digits in the URL.  If you set
                         this to ``4`` for example, the application will
                         only match if the url looks like ``/0001/``.  The
                         default is variable length.
    :param min: the minimal value.
    :param max: the maximal value.
    """
    regex = r'\d+'
    num_convert = int

    def __init__(self, map):
        IntegerConverter.__init__(self, map, min=1850, max=2100)


class MonthConverter(IntegerConverter):
    """This converter only accepts integer values between 1 and 12 (numeric encoding for months)::

        Rule('/page/<int_month:value>')

    This converter does not support negative values.

    :param map: the :class:`Map`.
    :param fixed_digits: the number of fixed digits in the URL.  If you set
                         this to ``4`` for example, the application will
                         only match if the url looks like ``/0001/``.  The
                         default is variable length.
    :param min: the minimal value.
    :param max: the maximal value.
    """
    regex = r'\d+'
    num_convert = int

    def __init__(self, map):
        IntegerConverter.__init__(self, map, min=1, max=12)


def add_routes(app):
    app.url_map.converters['valid_year'] = ValidYearConverter
    app.url_map.converters['int_month'] = MonthConverter

    # Helpers for setting up routes
    def dataset(name):
        return '<any({}):dataset>'.format(name)
    variable = '<any(tmax, tmin, precip):variable>'
    month = '<int_month:month>'
    # month = '<any({}):month>'.format(','.join("'{}'".format(m) for m in range(1, 13)))

    db = SQLAlchemy(app)

    @app.route('/{}/{};{}'.format(dataset('baseline'), variable, month),
               methods=['GET'])
    def baseline(**kwargs):
        return was.api.dispatch(db.session, **kwargs)

    @app.route('/{}/{};<valid_year:year>-{}'.format(dataset('weather'), variable, month),
               methods=['GET'])
    def weather(**kwargs):
        return was.api.dispatch(db.session, **kwargs)

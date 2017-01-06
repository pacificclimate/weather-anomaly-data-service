from werkzeug.routing import IntegerConverter
from flask.ext.sqlalchemy import SQLAlchemy
import was.api


class ValidYearConverter(IntegerConverter):
    """This converter only accepts integer values between 1850 and 2100::

        Rule('/page/<valid_year:value>')

    :param map: the :class:`Map`.
    """
    regex = r'\d+'
    num_convert = int

    def __init__(self, map):
        IntegerConverter.__init__(self, map, min=1850, max=2100)


class MonthConverter(IntegerConverter):
    """This converter only accepts integer values between 1 and 12 (numeric encoding for months)::

        Rule('/page/<int_month:value>')

    :param map: the :class:`Map`.
    """
    regex = r'\d+'
    num_convert = int

    def __init__(self, map):
        IntegerConverter.__init__(self, map, min=1, max=12)


def add_routes(app):
    app.url_map.converters['valid_year'] = ValidYearConverter
    app.url_map.converters['int_month'] = MonthConverter

    def components(dataset):
        """Helper for setting up routes"""
        return {
            'dataset': '<any({}):dataset>'.format(dataset),
            'variable': '<any(tmax, tmin, precip):variable>',
            'year': '<valid_year:year>',
            'month': '<int_month:month>',
        }

    db = SQLAlchemy(app)

    @app.route('/{dataset}/{variable};{month}'.format(**components('baseline')), methods=['GET'])
    @app.route('/{dataset}/{variable};{year}-{month}'.format(**components('weather')), methods=['GET'])
    def dispatch(**kwargs):
        return was.api.dispatch(db.session, **kwargs)
    # dispatch = partial(was.api.dispatch, db.session)  # rats, this doesn't work

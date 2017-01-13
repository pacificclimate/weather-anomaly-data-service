import datetime
from pycds import History
from pycds.weather_anomaly import \
    MonthlyAverageOfDailyMaxTemperature, MonthlyAverageOfDailyMinTemperature, MonthlyTotalPrecipitation
from wads.util import dicts_from_rows

def weather(session, variable, year, month):
    """Returns a list of items containing station info and the value of the weather variable specified by `variable`,
    for the month specified by `year` and `month`, for each station in the CRMP database monthly weather views.

    :param session: (sqlalchemy.orm.session.Session) database session
    :param variable: (string) requested weather variable ('tmax' | 'tmin' | 'precip')
    :param year: (int) requested year
    :param month: (int) requested month (1...12)
    :return: (list) see above
    """
    view_for_variable = {
        'tmax': MonthlyAverageOfDailyMaxTemperature,
        'tmin': MonthlyAverageOfDailyMinTemperature,
        'precip': MonthlyTotalPrecipitation,
    }

    WeatherView = view_for_variable[variable]

    q = session.query(
        History.station_name,
        History.lon,
        History.lat,
        History.elevation,
        WeatherView.statistic,
        WeatherView.data_coverage,
    ) \
        .select_from(WeatherView) \
        .join(History, WeatherView.history_id == History.id) \
        .filter(WeatherView.obs_month == datetime.datetime(year, month, 1))

    return dicts_from_rows(q.all())

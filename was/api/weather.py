from sqlalchemy import func
import datetime
# from pycds import History, \
#     MonthlyAverageOfDailyMaxTemperature, MonthlyAverageOfDailyMinTemperature, MonthlyTotalPrecipitation


def weather(session, variable, month, year):
    """Returns a list of items containing station info and the value of the weather variable specified by `variable`,
    for the month specified by `year` and `month`, for each station in the CRMP database monthly weather views.

    :param session: (sqlalchemy.orm.session.Session) database session
    :param variable: (string) requested weather variable ('tmax' | 'tmin' | 'precip')
    :param year: (int) requested year
    :param month: (int) requested month (1...12)
    :return: (list) see above
    """
    return { 'dataset': 'weather', 'variable': variable, 'year': year, 'month': month}

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
        WeatherView.datum,
    ) \
        .select_from(WeatherView) \
        .join(History, WeatherView.history_id == History.id) \
        .filter(WeatherView.obs_date == datetime.datetime(year, month))
    return q.all()

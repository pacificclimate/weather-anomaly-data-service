import datetime
from pycds import Network, Station, History, Variable
from pycds.weather_anomaly import \
    MonthlyAverageOfDailyMaxTemperature, MonthlyAverageOfDailyMinTemperature, MonthlyTotalPrecipitation
from wads.util import dicts_from_rows

def weather(session, variable, year, month):
    """Returns a list of aggregated weather observations.

    :param session: (sqlalchemy.orm.session.Session) database session
    :param variable: (string) requested weather variable ('tmax' | 'tmin' | 'precip')
    :param year: (int) requested year
    :param month: (int) requested month (1...12)
    :return: (list) a list of items containing station info and the value of the weather variable specified by `variable`,
    for the month specified by `year` and `month`, for each station in the CRMP database monthly weather views.
        [
            {
                'network_name': (str) network name,
                'station_native_id': (str) station native id,
                'station_name': (str) station name,
                'lon': (num) station longitude,
                'lat': (num) station latitude,
                'elevation': (num) station elevation,
                'frequency': (str) observation frequency,
                'network_variable_name': (str) network-specific name for this variable,
                'cell_method': (str) observation method of this variable,
                'statistic': (num) variable value,
                'data_coverage': (num) fraction in range [0,1] of count of actual observations to possible observations
                    in month for aggregate (depends on frequency of observation of specific variable),
            },
            ...
        ]
    """
    view_for_variable = {
        'tmax': MonthlyAverageOfDailyMaxTemperature,
        'tmin': MonthlyAverageOfDailyMinTemperature,
        'precip': MonthlyTotalPrecipitation,
    }

    WeatherView = view_for_variable[variable]

    q = session.query(
        Network.name.label('network_name'),
        Station.native_id.label('station_native_id'),
        History.station_name,
        History.lon,
        History.lat,
        History.elevation,
        History.freq.label('frequency'),
        Variable.name.label('network_variable_name'),
        Variable.cell_method,
        WeatherView.statistic,
        WeatherView.data_coverage,
    ) \
        .select_from(WeatherView) \
        .join(History, WeatherView.history_id == History.id) \
        .join(History.station) \
        .join(Station.network) \
        .join(Variable, WeatherView.vars_id == Variable.id) \
        .filter(WeatherView.obs_month == datetime.datetime(year, month, 1))

    return dicts_from_rows(q.all())

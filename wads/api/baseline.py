from sqlalchemy import func, cast, Float
from pycds import Network, Station, History, Variable, DerivedValue
from pycds.climate_baseline_helpers import pcic_climate_variable_network_name
from wads.util import dicts_from_rows


def baseline(session, variable, month):
    """Returns list of climate baseline data.

    :param session: (sqlalchemy.orm.session.Session) database session
    :param variable: (string) requested baseline climate variable ('tmax' | 'tmin' | 'precip')
    :param month: (int) requested baseline month (1...12)
    :return: list of dicts containing station info and the value of the climate baseline variable specified by
    `variable`, for the month specified by `month`, for each station in the CRMP database climate baseline dataset
        [
            {
                'network_name': (str) network name,
                'station_native_id': (str) station native id,
                'station_name': (str) station name,
                'lon': (num) station longitude,
                'lat': (num) station latitude,
                'elevation': (num) station elevation,
                'datum': (num) value for variable
            },
            ...
        ]
    """

    db_variable_name = {
        'tmax': 'Tx_Climatology',
        'tmin': 'Tn_Climatology',
        'precip': 'Precip_Climatology',
    }

    values = session.query(DerivedValue) \
        .select_from(DerivedValue) \
        .join(Variable, DerivedValue.vars_id == Variable.id) \
        .join(Network, Variable.network_id == Network.id) \
        .filter(Network.name == pcic_climate_variable_network_name) \
        .filter(Variable.name == db_variable_name[variable]) \
        .filter(func.date_part('month', DerivedValue.time) == float(month)) \
        .subquery()

    values_with_station_info = session.query(
        Network.name.label('network_name'),
        Station.native_id.label('station_native_id'),
        History.station_name.label('station_name'),
        cast(History.lon, Float).label('lon'),
        cast(History.lat, Float).label('lat'),
        cast(History.elevation, Float).label('elevation'),
        values.c.datum.label('datum'),
    ) \
        .select_from(values) \
        .join(History, values.c.history_id == History.id) \
        .join(Station, History.station_id == Station.id) \
        .join(Network, Station.network_id == Network.id)

    return dicts_from_rows(values_with_station_info.all())

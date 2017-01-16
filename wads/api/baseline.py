from sqlalchemy import func
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
                'station_name': (str) station name
                'lon': (num) station longitude
                'lat': (num) station latitude
                'elevation': (num) station elevatino
                'datum': (num) observation value for variable
            },
            ...
        ]
    """

    db_variable_name = {
        'tmax': 'Tx_Climatology',
        'tmin': 'Tn_Climatology',
        'precip': 'Precip_Climatology',
    }

    q = session.query(
        Network.name.label('network_name'),
        Station.native_id.label('station_native_id'),
        History.station_name,
        History.lon,
        History.lat,
        History.elevation,
        DerivedValue.datum,
    )\
        .select_from(DerivedValue)\
        .join(DerivedValue.history)\
        .join(DerivedValue.variable)\
        .join(History.station)\
        .join(Variable.network)\
        .filter(Network.name == pcic_climate_variable_network_name)\
        .filter(Variable.name == db_variable_name[variable])\
        .filter(func.date_part('month', DerivedValue.time) == float(month))

    return dicts_from_rows(q.all())

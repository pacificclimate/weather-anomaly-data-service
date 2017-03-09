""""Test basic database functionality - essentially, test the test db"""

from sqlalchemy import text, inspect


def test_db_session_works(session):
    result = session.execute(text("""SELECT 1 AS one""")).first()
    assert result
    assert result.one == 1


def test_db_has_some_expected_tables(db):
    expected_table_names = '''meta_contact
        meta_vars
        meta_history
        meta_sensor
        meta_network
        meta_station
        vars_per_history_mv
        obs_raw
        obs_derived_values
        meta_native_flag
        obs_raw_native_flags
    '''.split()
    table_names = inspect(db.engine).get_table_names()
    for name in expected_table_names:
        assert name in table_names
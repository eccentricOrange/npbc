"""
test data-dependent functions from the core
- all of these depend on the DB
- for consistency, the DB will always be initialised with the same data
- the test data is contained in `data/test.sql`
- the schema is the same as the core (`data/schema.sql` during development)
"""


from datetime import date, datetime
from multiprocessing.connection import Connection
from pathlib import Path
from sqlite3 import connect
from typing import Counter

from pytest import raises

import npbc_cli
import npbc_core
import npbc_exceptions

ACTIVE_DIRECTORY = Path("data")
DATABASE_PATH = ACTIVE_DIRECTORY / "npbc.sqlite"
SCHEMA_PATH = ACTIVE_DIRECTORY / "schema.sql"
TEST_SQL = ACTIVE_DIRECTORY / "test.sql"


def setup_db():
    DATABASE_PATH.unlink(missing_ok=True)

    connection = connect(DATABASE_PATH)
    connection.executescript(SCHEMA_PATH.read_text())
    connection.commit()
    connection.executescript(TEST_SQL.read_text())
    connection.commit()

    return connection

def test_db_creation():
    DATABASE_PATH.unlink(missing_ok=True)
    assert not DATABASE_PATH.exists()

    npbc_cli.main(['init'])

    assert DATABASE_PATH.exists()


def test_get_papers():
    connection = setup_db()

    known_data = (
        (1, 'paper1', 0, 0, 0),
        (1, 'paper1', 1, 1, 6.4),
        (1, 'paper1', 2, 0, 0),
        (1, 'paper1', 3, 0, 0),
        (1, 'paper1', 4, 0, 0),
        (1, 'paper1', 5, 1, 7.9),
        (1, 'paper1', 6, 1, 4),
        (2, 'paper2', 0, 0, 0),
        (2, 'paper2', 1, 0, 0),
        (2, 'paper2', 2, 0, 0),
        (2, 'paper2', 3, 0, 0),
        (2, 'paper2', 4, 1, 3.4),
        (2, 'paper2', 5, 0, 0),
        (2, 'paper2', 6, 1, 8.4),
        (3, 'paper3', 0, 1, 2.4),
        (3, 'paper3', 1, 1, 4.6),
        (3, 'paper3', 2, 0, 0),
        (3, 'paper3', 3, 0, 0),
        (3, 'paper3', 4, 1, 3.4),
        (3, 'paper3', 5, 1, 4.6),
        (3, 'paper3', 6, 1, 6)
    )

    assert Counter(npbc_core.get_papers(connection)) == Counter(known_data)
    connection.close()


def test_get_undelivered_strings():
    connection = setup_db()

    known_data = (
        (1, 1, 2020, 11, '5'),
        (2, 1, 2020, 11, '6-12'),
        (3, 2, 2020, 11, 'sundays'),
        (4, 3, 2020, 11, '2-tuesday'),
        (5, 3, 2020, 10, 'all')
    )

    assert Counter(npbc_core.get_undelivered_strings(connection)) == Counter(known_data)
    assert Counter(npbc_core.get_undelivered_strings(connection, string_id=3)) == Counter([known_data[2]])
    assert Counter(npbc_core.get_undelivered_strings(connection, month=11)) == Counter(known_data[:4])
    assert Counter(npbc_core.get_undelivered_strings(connection, paper_id=1)) == Counter(known_data[:2])
    assert Counter(npbc_core.get_undelivered_strings(connection, paper_id=1, string='6-12')) == Counter([known_data[1]])

    with raises(npbc_exceptions.StringNotExists):
        npbc_core.get_undelivered_strings(connection, year=1986)

    connection.close()


def test_delete_paper():
    connection = setup_db()

    npbc_core.delete_existing_paper(connection, 2)

    known_data = (
        (1, 'paper1', 0, 0, 0),
        (1, 'paper1', 1, 1, 6.4),
        (1, 'paper1', 2, 0, 0),
        (1, 'paper1', 3, 0, 0),
        (1, 'paper1', 4, 0, 0),
        (1, 'paper1', 5, 1, 7.9),
        (1, 'paper1', 6, 1, 4),
        (3, 'paper3', 0, 1, 2.4),
        (3, 'paper3', 1, 1, 4.6),
        (3, 'paper3', 2, 0, 0),
        (3, 'paper3', 3, 0, 0),
        (3, 'paper3', 4, 1, 3.4),
        (3, 'paper3', 5, 1, 4.6),
        (3, 'paper3', 6, 1, 6)
    )

    assert Counter(npbc_core.get_papers(connection)) == Counter(known_data)

    with raises(npbc_exceptions.PaperNotExists):
        npbc_core.delete_existing_paper(connection, 7)
        npbc_core.delete_existing_paper(connection, 2)

    connection.close()


def test_add_paper():
    connection = setup_db()

    known_data = (
        (1, 'paper1', 0, 0, 0),
        (1, 'paper1', 1, 1, 6.4),
        (1, 'paper1', 2, 0, 0),
        (1, 'paper1', 3, 0, 0),
        (1, 'paper1', 4, 0, 0),
        (1, 'paper1', 5, 1, 7.9),
        (1, 'paper1', 6, 1, 4),
        (2, 'paper2', 0, 0, 0),
        (2, 'paper2', 1, 0, 0),
        (2, 'paper2', 2, 0, 0),
        (2, 'paper2', 3, 0, 0),
        (2, 'paper2', 4, 1, 3.4),
        (2, 'paper2', 5, 0, 0),
        (2, 'paper2', 6, 1, 8.4),
        (3, 'paper3', 0, 1, 2.4),
        (3, 'paper3', 1, 1, 4.6),
        (3, 'paper3', 2, 0, 0),
        (3, 'paper3', 3, 0, 0),
        (3, 'paper3', 4, 1, 3.4),
        (3, 'paper3', 5, 1, 4.6),
        (3, 'paper3', 6, 1, 6),
        (4, 'paper4', 0, 1, 4),
        (4, 'paper4', 1, 0, 0),
        (4, 'paper4', 2, 1, 2.6),
        (4, 'paper4', 3, 0, 0),
        (4, 'paper4', 4, 0, 0),
        (4, 'paper4', 5, 1, 1),
        (4, 'paper4', 6, 1, 7)
    )

    npbc_core.add_new_paper(
        connection,
        'paper4',
        [True, False, True, False, False, True, True],
        [4, 0, 2.6, 0, 0, 1, 7]
    )

    assert Counter(npbc_core.get_papers(connection)) == Counter(known_data)

    with raises(npbc_exceptions.PaperAlreadyExists):
        npbc_core.add_new_paper(
            connection,
            'paper4',
            [True, False, True, False, False, True, True],
            [4, 0, 2.6, 0, 0, 1, 7]
        )

    connection.close()


def test_edit_paper():
    connection = setup_db()

    known_data = [
        (1, 'paper1', 0, 0, 0),
        (1, 'paper1', 1, 1, 6.4),
        (1, 'paper1', 2, 0, 0),
        (1, 'paper1', 3, 0, 0),
        (1, 'paper1', 4, 0, 0),
        (1, 'paper1', 5, 1, 7.9),
        (1, 'paper1', 6, 1, 4),
        (2, 'paper2', 0, 0, 0),
        (2, 'paper2', 1, 0, 0),
        (2, 'paper2', 2, 0, 0),
        (2, 'paper2', 3, 0, 0),
        (2, 'paper2', 4, 1, 3.4),
        (2, 'paper2', 5, 0, 0),
        (2, 'paper2', 6, 1, 8.4),
        (3, 'paper3', 0, 1, 2.4),
        (3, 'paper3', 1, 1, 4.6),
        (3, 'paper3', 2, 0, 0),
        (3, 'paper3', 3, 0, 0),
        (3, 'paper3', 4, 1, 3.4),
        (3, 'paper3', 5, 1, 4.6),
        (3, 'paper3', 6, 1, 6)
    ]

    npbc_core.edit_existing_paper(
        connection,
        1,
        days_delivered=[True, False, True, False, False, True, True],
        days_cost=[6.4, 0, 0, 0, 0, 7.9, 4]
    )

    known_data[0] = (1, 'paper1', 0, 1, 6.4)
    known_data[1] = (1, 'paper1', 1, 0, 0)
    known_data[2] = (1, 'paper1', 2, 1, 0)
    known_data[3] = (1, 'paper1', 3, 0, 0)
    known_data[4] = (1, 'paper1', 4, 0, 0)
    known_data[5] = (1, 'paper1', 5, 1, 7.9)
    known_data[6] = (1, 'paper1', 6, 1, 4)

    assert Counter(npbc_core.get_papers(connection)) == Counter(known_data)

    npbc_core.edit_existing_paper(
        connection,
        3,
        name="New paper"
    )

    known_data[14] = (3, 'New paper', 0, 1, 2.4)
    known_data[15] = (3, 'New paper', 1, 1, 4.6)
    known_data[16] = (3, 'New paper', 2, 0, 0)
    known_data[17] = (3, 'New paper', 3, 0, 0)
    known_data[18] = (3, 'New paper', 4, 1, 3.4)
    known_data[19] = (3, 'New paper', 5, 1, 4.6)
    known_data[20] = (3, 'New paper', 6, 1, 6)

    assert Counter(npbc_core.get_papers(connection)) == Counter(known_data)

    with raises(npbc_exceptions.PaperNotExists):
        npbc_core.edit_existing_paper(connection, 7, name="New paper")

    connection.close()


def test_delete_string():
    known_data = (
        (1, 1, 2020, 11, '5'),
        (2, 1, 2020, 11, '6-12'),
        (3, 2, 2020, 11, 'sundays'),
        (4, 3, 2020, 11, '2-tuesday'),
        (5, 3, 2020, 10, 'all')
    )

    connection = setup_db()
    npbc_core.delete_undelivered_string(connection, string='all')
    assert Counter(npbc_core.get_undelivered_strings(connection)) == Counter(known_data[:4])
    connection.close()

    connection = setup_db()
    npbc_core.delete_undelivered_string(connection, month=11)
    assert Counter(npbc_core.get_undelivered_strings(connection)) == Counter([known_data[4]])
    connection.close()

    connection = setup_db()
    npbc_core.delete_undelivered_string(connection, paper_id=1)
    assert Counter(npbc_core.get_undelivered_strings(connection)) == Counter(known_data[2:])
    connection.close()

    connection = setup_db()
    with raises(npbc_exceptions.StringNotExists):
        npbc_core.delete_undelivered_string(connection, string='not exists')

    with raises(npbc_exceptions.NoParameters):
        npbc_core.delete_undelivered_string(connection)

    connection.close()


def test_add_string():
    connection = setup_db()

    known_data = [
        (1, 1, 2020, 11, '5'),
        (2, 1, 2020, 11, '6-12'),
        (3, 2, 2020, 11, 'sundays'),
        (4, 3, 2020, 11, '2-tuesday'),
        (5, 3, 2020, 10, 'all')
    ]

    npbc_core.add_undelivered_string(connection, 4, 2017, 3, 'sundays')
    known_data.append((6, 3, 2017, 4, 'sundays'))
    assert Counter(npbc_core.get_undelivered_strings(connection)) == Counter(known_data)

    npbc_core.add_undelivered_string(connection, 9, 2017, None, '11')
    known_data.append((7, 1, 2017, 9, '11'))
    known_data.append((8, 2, 2017, 9, '11'))
    known_data.append((9, 3, 2017, 9, '11'))
    assert Counter(npbc_core.get_undelivered_strings(connection)) == Counter(known_data)

    connection.close()


def test_save_results():
    connection = setup_db()

    known_data = (
        (1, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-01'),
        (1, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-02'),
        (2, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-01'),
        (2, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-05'),
        (2, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-03'),
        (1, 1, 2020, '04/01/2022 01:05:42 AM', 105.0),
        (2, 1, 2020, '04/01/2022 01:05:42 AM', 51.0),
        (3, 1, 2020, '04/01/2022 01:05:42 AM', 647.0)
    )

    npbc_core.save_results(
        connection,
        {1: 105, 2: 51, 3: 647},
        {
            1: set((date(month=1, day=1, year=2020), date(month=1, day=2, year=2020))),
            2: set((date(month=1, day=1, year=2020), date(month=1, day=5, year=2020), date(month=1, day=3, year=2020))),
            3: set()
        },
        1,
        2020,
        datetime(year=2022, month=1, day=4, hour=1, minute=5, second=42)
    )

    assert Counter(npbc_core.get_logged_data(connection)) == Counter(known_data)

    connection.close()

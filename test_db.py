"""
test data-dependent functions from the core
- all of these depend on the DB
- for consistency, the DB will always be initialised with the same data
- the test data is contained in `data/test.sql`
- the schema is the same as the core (`data/schema.sql` during development)
"""


from datetime import date, datetime
from pathlib import Path
from sqlite3 import connect
from typing import Counter

from pytest import raises

import npbc_core
import npbc_exceptions

DATABASE_PATH = Path("data") / "npbc.db"
SCHEMA_PATH = Path("data") / "schema.sql"
TEST_SQL = Path("data") / "test.sql"


def setup_db(database_path: Path, schema_path: Path, test_sql: Path):
    database_path.unlink(missing_ok=True)
    

    with connect(database_path) as connection:
        connection.executescript(schema_path.read_text())
        connection.commit()
        connection.executescript(test_sql.read_text())

    connection.close()


def test_get_papers():
    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)

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

    assert Counter(npbc_core.get_papers()) == Counter(known_data)


def test_get_undelivered_strings():
    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)

    known_data = [
        (1, 1, 2020, 11, '5'),
        (2, 1, 2020, 11, '6-12'),
        (3, 2, 2020, 11, 'sundays'),
        (4, 3, 2020, 11, '2-tuesday'),
        (5, 3, 2020, 10, 'all')
    ]

    assert Counter(npbc_core.get_undelivered_strings()) == Counter(known_data)
    assert Counter(npbc_core.get_undelivered_strings(string_id=3)) == Counter([known_data[2]])
    assert Counter(npbc_core.get_undelivered_strings(month=11)) == Counter(known_data[:4])
    assert Counter(npbc_core.get_undelivered_strings(paper_id=1)) == Counter(known_data[:2])
    assert Counter(npbc_core.get_undelivered_strings(paper_id=1, string='6-12')) == Counter([known_data[1]])

    with raises(npbc_exceptions.StringNotExists):
        npbc_core.get_undelivered_strings(year=1986)


def test_delete_paper():
    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)

    npbc_core.delete_existing_paper(2)

    known_data = [
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
    ]

    assert Counter(npbc_core.get_papers()) == Counter(known_data)

    with raises(npbc_exceptions.PaperNotExists):
        npbc_core.delete_existing_paper(7)
        npbc_core.delete_existing_paper(2)


def test_add_paper():
    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)

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
        (3, 'paper3', 6, 1, 6),
        (4, 'paper4', 0, 1, 4),
        (4, 'paper4', 1, 0, 0),
        (4, 'paper4', 2, 1, 2.6),
        (4, 'paper4', 3, 0, 0),
        (4, 'paper4', 4, 0, 0),
        (4, 'paper4', 5, 1, 1),
        (4, 'paper4', 6, 1, 7)
    ]

    npbc_core.add_new_paper(
        'paper4',
        [True, False, True, False, False, True, True],
        [4, 0, 2.6, 0, 0, 1, 7]
    )

    assert Counter(npbc_core.get_papers()) == Counter(known_data)

    with raises(npbc_exceptions.PaperAlreadyExists):
        npbc_core.add_new_paper(
            'paper4',
            [True, False, True, False, False, True, True],
            [4, 0, 2.6, 0, 0, 1, 7]
        )


def test_edit_paper():
    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)

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

    assert Counter(npbc_core.get_papers()) == Counter(known_data)

    npbc_core.edit_existing_paper(
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

    assert Counter(npbc_core.get_papers()) == Counter(known_data)

    with raises(npbc_exceptions.PaperNotExists):
        npbc_core.edit_existing_paper(7, name="New paper")


def test_delete_string():
    known_data = [
        (1, 1, 2020, 11, '5'),
        (2, 1, 2020, 11, '6-12'),
        (3, 2, 2020, 11, 'sundays'),
        (4, 3, 2020, 11, '2-tuesday'),
        (5, 3, 2020, 10, 'all')
    ]

    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)
    npbc_core.delete_undelivered_string(string='all')
    assert Counter(npbc_core.get_undelivered_strings()) == Counter(known_data[:4])

    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)
    npbc_core.delete_undelivered_string(month=11)
    assert Counter(npbc_core.get_undelivered_strings()) == Counter([known_data[4]])

    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)
    npbc_core.delete_undelivered_string(paper_id=1)
    assert Counter(npbc_core.get_undelivered_strings()) == Counter(known_data[2:])

    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)

    with raises(npbc_exceptions.StringNotExists):
        npbc_core.delete_undelivered_string(string='not exists')

    with raises(npbc_exceptions.NoParameters):
        npbc_core.delete_undelivered_string()


def test_add_string():
    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)

    known_data = [
        (1, 1, 2020, 11, '5'),
        (2, 1, 2020, 11, '6-12'),
        (3, 2, 2020, 11, 'sundays'),
        (4, 3, 2020, 11, '2-tuesday'),
        (5, 3, 2020, 10, 'all')
    ]

    npbc_core.add_undelivered_string(4, 2017, 3, 'sundays')
    known_data.append((6, 3, 2017, 4, 'sundays'))
    assert Counter(npbc_core.get_undelivered_strings()) == Counter(known_data)

    npbc_core.add_undelivered_string(9, 2017, None, '11')
    known_data.append((7, 1, 2017, 9, '11'))
    known_data.append((8, 2, 2017, 9, '11'))
    known_data.append((9, 3, 2017, 9, '11'))
    assert Counter(npbc_core.get_undelivered_strings()) == Counter(known_data)


def test_save_results():
    setup_db(DATABASE_PATH, SCHEMA_PATH, TEST_SQL)

    known_data = [
        (1, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-01'),
        (1, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-02'),
        (2, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-01'),
        (2, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-05'),
        (2, 1, 2020, '04/01/2022 01:05:42 AM', '2020-01-03'),
        (1, 1, 2020, '04/01/2022 01:05:42 AM', 105.0),
        (2, 1, 2020, '04/01/2022 01:05:42 AM', 51.0),
        (3, 1, 2020, '04/01/2022 01:05:42 AM', 647.0)
    ]

    npbc_core.save_results(
        {1: 105, 2: 51, 3: 647},
        {
            1: set([date(month=1, day=1, year=2020), date(month=1, day=2, year=2020)]),
            2: set([date(month=1, day=1, year=2020), date(month=1, day=5, year=2020), date(month=1, day=3, year=2020)]),
            3: set()
        },
        1,
        2020,
        datetime(year=2022, month=1, day=4, hour=1, minute=5, second=42)
    )

    assert Counter(npbc_core.get_logged_data()) == Counter(known_data)

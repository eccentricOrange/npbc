"""
test data-independent functions from the core
- none of these depend on data in the database
"""

from datetime import date as date_type

from numpy import array
from pytest import raises

import npbc_core
from npbc_exceptions import InvalidMonthYear, InvalidUndeliveredString


def test_get_number_of_each_weekday():
    test_function = npbc_core.get_number_of_each_weekday

    assert list(test_function(1, 2022)) == [5, 4, 4, 4, 4, 5, 5]
    assert list(test_function(2, 2022)) == [4, 4, 4, 4, 4, 4, 4]
    assert list(test_function(3, 2022)) == [4, 5, 5 ,5, 4, 4, 4]
    assert list(test_function(2, 2020)) == [4, 4, 4, 4, 4, 5, 4]
    assert list(test_function(12, 1954)) == [4, 4, 5, 5, 5, 4, 4]


def test_validate_undelivered_string():
    test_function = npbc_core.validate_undelivered_string

    with raises(InvalidUndeliveredString):
        test_function("a")
        test_function("monday")
        test_function("1-mondays")
        test_function("1monday")
        test_function("1 monday")
        test_function("monday-1")
        test_function("monday-1")

    test_function("")
    test_function("1")
    test_function("6")
    test_function("31")
    test_function("31","")
    test_function("3","1")
    test_function("3","1","")
    test_function("3","1")
    test_function("3","1")
    test_function("3","1")
    test_function("1","2","3-9")
    test_function("1","2","3-9","11","12","13-19")
    test_function("1","2","3-9","11","12","13-19","21","22","23-29")
    test_function("1","2","3-9","11","12","13-19","21","22","23-29","31")
    test_function("1","2","3","4","5","6","7","8","9")
    test_function("mondays")
    test_function("mondays,tuesdays")
    test_function("mondays","tuesdays","wednesdays")
    test_function("mondays","5-21")
    test_function("mondays","5-21","tuesdays","5-21")
    test_function("1-monday")
    test_function("2-monday")
    test_function("all")
    test_function("All")
    test_function("aLl")
    test_function("alL")
    test_function("aLL")
    test_function("ALL")


def test_undelivered_string_parsing():
    MONTH = 5
    YEAR = 2017
    test_function = npbc_core.parse_undelivered_strings


    assert test_function(MONTH, YEAR, '') == set([])

    assert test_function(MONTH, YEAR, '1') == set([
        date_type(year=YEAR, month=MONTH, day=1)
    ])

    assert test_function(MONTH, YEAR, '1-2') == set([
        date_type(year=YEAR, month=MONTH, day=1),
        date_type(year=YEAR, month=MONTH, day=2)
    ])

    assert test_function(MONTH, YEAR, '5-17') == set([
        date_type(year=YEAR, month=MONTH, day=5),
        date_type(year=YEAR, month=MONTH, day=6),
        date_type(year=YEAR, month=MONTH, day=7),
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=9),
        date_type(year=YEAR, month=MONTH, day=10),
        date_type(year=YEAR, month=MONTH, day=11),
        date_type(year=YEAR, month=MONTH, day=12),
        date_type(year=YEAR, month=MONTH, day=13),
        date_type(year=YEAR, month=MONTH, day=14),
        date_type(year=YEAR, month=MONTH, day=15),
        date_type(year=YEAR, month=MONTH, day=16),
        date_type(year=YEAR, month=MONTH, day=17)
    ])

    assert test_function(MONTH, YEAR, '5-17', '19') == set([
        date_type(year=YEAR, month=MONTH, day=5),
        date_type(year=YEAR, month=MONTH, day=6),
        date_type(year=YEAR, month=MONTH, day=7),
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=9),
        date_type(year=YEAR, month=MONTH, day=10),
        date_type(year=YEAR, month=MONTH, day=11),
        date_type(year=YEAR, month=MONTH, day=12),
        date_type(year=YEAR, month=MONTH, day=13),
        date_type(year=YEAR, month=MONTH, day=14),
        date_type(year=YEAR, month=MONTH, day=15),
        date_type(year=YEAR, month=MONTH, day=16),
        date_type(year=YEAR, month=MONTH, day=17),
        date_type(year=YEAR, month=MONTH, day=19)
    ])

    assert test_function(MONTH, YEAR, '5-17', '19-21') == set([
        date_type(year=YEAR, month=MONTH, day=5),
        date_type(year=YEAR, month=MONTH, day=6),
        date_type(year=YEAR, month=MONTH, day=7),
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=9),
        date_type(year=YEAR, month=MONTH, day=10),
        date_type(year=YEAR, month=MONTH, day=11),
        date_type(year=YEAR, month=MONTH, day=12),
        date_type(year=YEAR, month=MONTH, day=13),
        date_type(year=YEAR, month=MONTH, day=14),
        date_type(year=YEAR, month=MONTH, day=15),
        date_type(year=YEAR, month=MONTH, day=16),
        date_type(year=YEAR, month=MONTH, day=17),
        date_type(year=YEAR, month=MONTH, day=19),
        date_type(year=YEAR, month=MONTH, day=20),
        date_type(year=YEAR, month=MONTH, day=21)
    ])

    assert test_function(MONTH, YEAR, '5-17', '19-21', '23') == set([
        date_type(year=YEAR, month=MONTH, day=5),
        date_type(year=YEAR, month=MONTH, day=6),
        date_type(year=YEAR, month=MONTH, day=7),
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=9),
        date_type(year=YEAR, month=MONTH, day=10),
        date_type(year=YEAR, month=MONTH, day=11),
        date_type(year=YEAR, month=MONTH, day=12),
        date_type(year=YEAR, month=MONTH, day=13),
        date_type(year=YEAR, month=MONTH, day=14),
        date_type(year=YEAR, month=MONTH, day=15),
        date_type(year=YEAR, month=MONTH, day=16),
        date_type(year=YEAR, month=MONTH, day=17),
        date_type(year=YEAR, month=MONTH, day=19),
        date_type(year=YEAR, month=MONTH, day=20),
        date_type(year=YEAR, month=MONTH, day=21),
        date_type(year=YEAR, month=MONTH, day=23)
    ])

    assert test_function(MONTH, YEAR, 'mondays') == set([
        date_type(year=YEAR, month=MONTH, day=1),
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=15),
        date_type(year=YEAR, month=MONTH, day=22),
        date_type(year=YEAR, month=MONTH, day=29)
    ])

    assert test_function(MONTH, YEAR, 'mondays', 'wednesdays') == set([
        date_type(year=YEAR, month=MONTH, day=1),
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=15),
        date_type(year=YEAR, month=MONTH, day=22),
        date_type(year=YEAR, month=MONTH, day=29),
        date_type(year=YEAR, month=MONTH, day=3),
        date_type(year=YEAR, month=MONTH, day=10),
        date_type(year=YEAR, month=MONTH, day=17),
        date_type(year=YEAR, month=MONTH, day=24),
        date_type(year=YEAR, month=MONTH, day=31)
    ])

    assert test_function(MONTH, YEAR, '2-monday') == set([
        date_type(year=YEAR, month=MONTH, day=8)
    ])

    assert test_function(MONTH, YEAR, '2-monday', '3-wednesday') == set([
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=17)
    ])


def test_calculating_cost_of_one_paper():
    DAYS_PER_WEEK = [5, 4, 4, 4, 4, 5, 5]

    COST_AND_DELIVERY_DATA = (
        array([0, 0, 2, 2, 5, 0, 1]),
        array([False, False,  True,  True,  True, False,  True])
    )

    test_function = npbc_core.calculate_cost_of_one_paper

    assert test_function(
        DAYS_PER_WEEK,
        set([]),
        *COST_AND_DELIVERY_DATA
    ) == 41

    assert test_function(
        DAYS_PER_WEEK,
        set([]),
        array([0, 0, 2, 2, 5, 0, 1]),
        array([False, False,  True,  True,  True, False, False])
    ) == 36

    assert test_function(
        DAYS_PER_WEEK,
        set([
            date_type(year=2022, month=1, day=8)
        ]),
        *COST_AND_DELIVERY_DATA
    ) == 41

    assert test_function(
        DAYS_PER_WEEK,
        set([
            date_type(year=2022, month=1, day=8),
            date_type(year=2022, month=1, day=8)
        ]),
        *COST_AND_DELIVERY_DATA
    ) == 41

    assert test_function(
        DAYS_PER_WEEK,
        set([
            date_type(year=2022, month=1, day=8),
            date_type(year=2022, month=1, day=17)
        ]),
        *COST_AND_DELIVERY_DATA
    ) == 41

    assert test_function(
        DAYS_PER_WEEK,
        set([
            date_type(year=2022, month=1, day=2)
        ]),
        *COST_AND_DELIVERY_DATA
    ) == 40

    assert test_function(
        DAYS_PER_WEEK,
        set([
            date_type(year=2022, month=1, day=2),
            date_type(year=2022, month=1, day=2)
        ]),
        *COST_AND_DELIVERY_DATA
    ) == 40

    assert test_function(
        DAYS_PER_WEEK,
        set([
            date_type(year=2022, month=1, day=6),
            date_type(year=2022, month=1, day=7)
        ]),
        *COST_AND_DELIVERY_DATA
    ) == 34

    assert test_function(
        DAYS_PER_WEEK,
        set([
            date_type(year=2022, month=1, day=6),
            date_type(year=2022, month=1, day=7),
            date_type(year=2022, month=1, day=8)
        ]),
        *COST_AND_DELIVERY_DATA
    ) == 34

    assert test_function(
        DAYS_PER_WEEK,
        set([
            date_type(year=2022, month=1, day=6),
            date_type(year=2022, month=1, day=7),
            date_type(year=2022, month=1, day=7),
            date_type(year=2022, month=1, day=7),
            date_type(year=2022, month=1, day=8),
            date_type(year=2022, month=1, day=8),
            date_type(year=2022, month=1, day=8)
        ]),
        *COST_AND_DELIVERY_DATA
    ) == 34


def test_validate_month_and_year():
    test_function = npbc_core.validate_month_and_year

    test_function(1, 2020)
    test_function(12, 2020)
    test_function(1, 2021)
    test_function(12, 2021)
    test_function(1, 2022)
    test_function(12, 2022)

    with raises(InvalidMonthYear):
        test_function(-54, 2020)
        test_function(0, 2020)
        test_function(13, 2020)
        test_function(45, 2020)
        test_function(1, -5)
        test_function(12, -5)
        test_function(1.6, 10) # type: ignore
        test_function(12.6, 10) # type: ignore
        test_function(1, '10') # type: ignore
        test_function(12, '10') # type: ignore

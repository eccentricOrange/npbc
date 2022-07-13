"""
test data-independent functions from the core
- none of these depend on data in the database
"""

from datetime import date

from numpy import array
from pytest import raises

import npbc_core
from npbc_exceptions import InvalidMonthYear, InvalidUndeliveredString


def test_get_number_of_each_weekday():
    assert tuple(npbc_core.get_number_of_each_weekday(1, 2022)) == (5, 4, 4, 4, 4, 5, 5)
    assert tuple(npbc_core.get_number_of_each_weekday(2, 2022)) == (4, 4, 4, 4, 4, 4, 4)
    assert tuple(npbc_core.get_number_of_each_weekday(3, 2022)) == (4, 5, 5 ,5, 4, 4, 4)
    assert tuple(npbc_core.get_number_of_each_weekday(2, 2020)) == (4, 4, 4, 4, 4, 5, 4)
    assert tuple(npbc_core.get_number_of_each_weekday(12, 1954)) == (4, 4, 5, 5, 5, 4, 4)


def test_validate_undelivered_string():
    with raises(InvalidUndeliveredString):
        npbc_core.validate_undelivered_string("a")
        npbc_core.validate_undelivered_string("monday")
        npbc_core.validate_undelivered_string("1-mondays")
        npbc_core.validate_undelivered_string("1monday")
        npbc_core.validate_undelivered_string("1 monday")
        npbc_core.validate_undelivered_string("monday-1")
        npbc_core.validate_undelivered_string("monday-1")

    npbc_core.validate_undelivered_string("")
    npbc_core.validate_undelivered_string("1")
    npbc_core.validate_undelivered_string("6")
    npbc_core.validate_undelivered_string("31")
    npbc_core.validate_undelivered_string("31","")
    npbc_core.validate_undelivered_string("3","1")
    npbc_core.validate_undelivered_string("3","1","")
    npbc_core.validate_undelivered_string("3","1")
    npbc_core.validate_undelivered_string("3","1")
    npbc_core.validate_undelivered_string("3","1")
    npbc_core.validate_undelivered_string("1","2","3-9")
    npbc_core.validate_undelivered_string("1","2","3-9","11","12","13-19")
    npbc_core.validate_undelivered_string("1","2","3-9","11","12","13-19","21","22","23-29")
    npbc_core.validate_undelivered_string("1","2","3-9","11","12","13-19","21","22","23-29","31")
    npbc_core.validate_undelivered_string("1","2","3","4","5","6","7","8","9")
    npbc_core.validate_undelivered_string("mondays")
    npbc_core.validate_undelivered_string("mondays,tuesdays")
    npbc_core.validate_undelivered_string("mondays","tuesdays","wednesdays")
    npbc_core.validate_undelivered_string("mondays","5-21")
    npbc_core.validate_undelivered_string("mondays","5-21","tuesdays","5-21")
    npbc_core.validate_undelivered_string("1-monday")
    npbc_core.validate_undelivered_string("2-monday")
    npbc_core.validate_undelivered_string("all")
    npbc_core.validate_undelivered_string("All")
    npbc_core.validate_undelivered_string("aLl")
    npbc_core.validate_undelivered_string("alL")
    npbc_core.validate_undelivered_string("aLL")
    npbc_core.validate_undelivered_string("ALL")


def test_undelivered_string_parsing():
    MONTH = 5
    YEAR = 2017


    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '') == set(())

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '1') == set((
        date(year=YEAR, month=MONTH, day=1),
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '1-2') == set((
        date(year=YEAR, month=MONTH, day=1),
        date(year=YEAR, month=MONTH, day=2)
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '5-17') == set((
        date(year=YEAR, month=MONTH, day=5),
        date(year=YEAR, month=MONTH, day=6),
        date(year=YEAR, month=MONTH, day=7),
        date(year=YEAR, month=MONTH, day=8),
        date(year=YEAR, month=MONTH, day=9),
        date(year=YEAR, month=MONTH, day=10),
        date(year=YEAR, month=MONTH, day=11),
        date(year=YEAR, month=MONTH, day=12),
        date(year=YEAR, month=MONTH, day=13),
        date(year=YEAR, month=MONTH, day=14),
        date(year=YEAR, month=MONTH, day=15),
        date(year=YEAR, month=MONTH, day=16),
        date(year=YEAR, month=MONTH, day=17)
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '5-17', '19') == set((
        date(year=YEAR, month=MONTH, day=5),
        date(year=YEAR, month=MONTH, day=6),
        date(year=YEAR, month=MONTH, day=7),
        date(year=YEAR, month=MONTH, day=8),
        date(year=YEAR, month=MONTH, day=9),
        date(year=YEAR, month=MONTH, day=10),
        date(year=YEAR, month=MONTH, day=11),
        date(year=YEAR, month=MONTH, day=12),
        date(year=YEAR, month=MONTH, day=13),
        date(year=YEAR, month=MONTH, day=14),
        date(year=YEAR, month=MONTH, day=15),
        date(year=YEAR, month=MONTH, day=16),
        date(year=YEAR, month=MONTH, day=17),
        date(year=YEAR, month=MONTH, day=19)
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '5-17', '19-21') == set((
        date(year=YEAR, month=MONTH, day=5),
        date(year=YEAR, month=MONTH, day=6),
        date(year=YEAR, month=MONTH, day=7),
        date(year=YEAR, month=MONTH, day=8),
        date(year=YEAR, month=MONTH, day=9),
        date(year=YEAR, month=MONTH, day=10),
        date(year=YEAR, month=MONTH, day=11),
        date(year=YEAR, month=MONTH, day=12),
        date(year=YEAR, month=MONTH, day=13),
        date(year=YEAR, month=MONTH, day=14),
        date(year=YEAR, month=MONTH, day=15),
        date(year=YEAR, month=MONTH, day=16),
        date(year=YEAR, month=MONTH, day=17),
        date(year=YEAR, month=MONTH, day=19),
        date(year=YEAR, month=MONTH, day=20),
        date(year=YEAR, month=MONTH, day=21)
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '5-17', '19-21', '23') == set((
        date(year=YEAR, month=MONTH, day=5),
        date(year=YEAR, month=MONTH, day=6),
        date(year=YEAR, month=MONTH, day=7),
        date(year=YEAR, month=MONTH, day=8),
        date(year=YEAR, month=MONTH, day=9),
        date(year=YEAR, month=MONTH, day=10),
        date(year=YEAR, month=MONTH, day=11),
        date(year=YEAR, month=MONTH, day=12),
        date(year=YEAR, month=MONTH, day=13),
        date(year=YEAR, month=MONTH, day=14),
        date(year=YEAR, month=MONTH, day=15),
        date(year=YEAR, month=MONTH, day=16),
        date(year=YEAR, month=MONTH, day=17),
        date(year=YEAR, month=MONTH, day=19),
        date(year=YEAR, month=MONTH, day=20),
        date(year=YEAR, month=MONTH, day=21),
        date(year=YEAR, month=MONTH, day=23)
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, 'mondays') == set((
        date(year=YEAR, month=MONTH, day=1),
        date(year=YEAR, month=MONTH, day=8),
        date(year=YEAR, month=MONTH, day=15),
        date(year=YEAR, month=MONTH, day=22),
        date(year=YEAR, month=MONTH, day=29)
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, 'mondays', 'wednesdays') == set((
        date(year=YEAR, month=MONTH, day=1),
        date(year=YEAR, month=MONTH, day=8),
        date(year=YEAR, month=MONTH, day=15),
        date(year=YEAR, month=MONTH, day=22),
        date(year=YEAR, month=MONTH, day=29),
        date(year=YEAR, month=MONTH, day=3),
        date(year=YEAR, month=MONTH, day=10),
        date(year=YEAR, month=MONTH, day=17),
        date(year=YEAR, month=MONTH, day=24),
        date(year=YEAR, month=MONTH, day=31)
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '2-monday') == set((
        date(year=YEAR, month=MONTH, day=8),
    ))

    assert npbc_core.parse_undelivered_strings(MONTH, YEAR, '2-monday', '3-wednesday') == set((
        date(year=YEAR, month=MONTH, day=8),
        date(year=YEAR, month=MONTH, day=17)
    ))


def test_calculating_cost_of_one_paper():
    DAYS_PER_WEEK = [5, 4, 4, 4, 4, 5, 5]

    COST_AND_DELIVERY_DATA = (
        array((0, 0, 2, 2, 5, 0, 1)),
        array((False, False,  True,  True,  True, False,  True))
    )

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set(()),
        *COST_AND_DELIVERY_DATA
    ) == 41

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set(()),
        array((0, 0, 2, 2, 5, 0, 1)),
        array((False, False,  True,  True,  True, False, False))
    ) == 36

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set((
            date(year=2022, month=1, day=8),
        )),
        *COST_AND_DELIVERY_DATA
    ) == 41

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set((
            date(year=2022, month=1, day=8),
            date(year=2022, month=1, day=8)
        )),
        *COST_AND_DELIVERY_DATA
    ) == 41

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set((
            date(year=2022, month=1, day=8),
            date(year=2022, month=1, day=17)
        )),
        *COST_AND_DELIVERY_DATA
    ) == 41

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set((
            date(year=2022, month=1, day=2),
        )),
        *COST_AND_DELIVERY_DATA
    ) == 40

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set((
            date(year=2022, month=1, day=2),
            date(year=2022, month=1, day=2)
        )),
        *COST_AND_DELIVERY_DATA
    ) == 40

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set((
            date(year=2022, month=1, day=6),
            date(year=2022, month=1, day=7)
        )),
        *COST_AND_DELIVERY_DATA
    ) == 34

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set((
            date(year=2022, month=1, day=6),
            date(year=2022, month=1, day=7),
            date(year=2022, month=1, day=8)
        )),
        *COST_AND_DELIVERY_DATA
    ) == 34

    assert npbc_core.calculate_cost_of_one_paper(
        DAYS_PER_WEEK,
        set((
            date(year=2022, month=1, day=6),
            date(year=2022, month=1, day=7),
            date(year=2022, month=1, day=7),
            date(year=2022, month=1, day=7),
            date(year=2022, month=1, day=8),
            date(year=2022, month=1, day=8),
            date(year=2022, month=1, day=8)
        )),
        *COST_AND_DELIVERY_DATA
    ) == 34


def test_validate_month_and_year():
    npbc_core.validate_month_and_year(1, 2020)
    npbc_core.validate_month_and_year(12, 2020)
    npbc_core.validate_month_and_year(1, 2021)
    npbc_core.validate_month_and_year(12, 2021)
    npbc_core.validate_month_and_year(1, 2022)
    npbc_core.validate_month_and_year(12, 2022)

    with raises(InvalidMonthYear):
        npbc_core.validate_month_and_year(-54, 2020)
        npbc_core.validate_month_and_year(0, 2020)
        npbc_core.validate_month_and_year(13, 2020)
        npbc_core.validate_month_and_year(45, 2020)
        npbc_core.validate_month_and_year(1, -5)
        npbc_core.validate_month_and_year(12, -5)
        npbc_core.validate_month_and_year(1.6, 10) # type: ignore
        npbc_core.validate_month_and_year(12.6, 10) # type: ignore
        npbc_core.validate_month_and_year(1, '10') # type: ignore
        npbc_core.validate_month_and_year(12, '10') # type: ignore

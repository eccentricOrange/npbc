from datetime import date as date_type
import npbc_core

def test_get_number_of_each_weekday():
    test_function = npbc_core.get_number_of_each_weekday

    assert list(test_function(1, 2022)) == [5, 4, 4, 4, 4, 5, 5]
    assert list(test_function(2, 2022)) == [4, 4, 4, 4, 4, 4, 4]
    assert list(test_function(3, 2022)) == [4, 5, 5 ,5, 4, 4, 4]
    assert list(test_function(2, 2020)) == [4, 4, 4, 4, 4, 5, 4]
    assert list(test_function(12, 1954)) == [4, 4, 5, 5, 5, 4, 4]


def test_validate_undelivered_string():
    test_function = npbc_core.validate_undelivered_string

    assert test_function("")
    assert not test_function("a")
    assert not test_function("monday")
    assert not test_function("1-mondays")
    assert not test_function("1monday")
    assert not test_function("1 monday")
    assert not test_function("monday-1")
    assert not test_function("monday-1")
    assert test_function("1")
    assert test_function("6")
    assert test_function("31")
    assert test_function("31","")
    assert test_function("3","1")
    assert test_function("3","1","")
    assert test_function("3","1")
    assert test_function("3","1")
    assert test_function("3","1")
    assert test_function("1","2","3-9")
    assert test_function("1","2","3-9","11","12","13-19")
    assert test_function("1","2","3-9","11","12","13-19","21","22","23-29")
    assert test_function("1","2","3-9","11","12","13-19","21","22","23-29","31")
    assert test_function("1","2","3","4","5","6","7","8","9")
    assert test_function("mondays")
    assert test_function("mondays,tuesdays")
    assert test_function("mondays","tuesdays","wednesdays")
    assert test_function("mondays","5-21")
    assert test_function("mondays","5-21","tuesdays","5-21")
    assert test_function("1-monday")
    assert test_function("2-monday")
    assert test_function("all")
    assert test_function("All")
    assert test_function("aLl")
    assert test_function("alL")
    assert test_function("aLL")
    assert test_function("ALL")


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
import npbc_core
from datetime import date as date_type


def test_regex_number():
    assert npbc_core.VALIDATE_REGEX['number'].match('') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('1') is not None
    assert npbc_core.VALIDATE_REGEX['number'].match('1 2') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('1-2') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('11') is not None
    assert npbc_core.VALIDATE_REGEX['number'].match('11-12') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('11-12,13') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('11-12,13-14') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('111') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('a') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('1a') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('1a2') is None
    assert npbc_core.VALIDATE_REGEX['number'].match('12b') is None

def test_regex_range():
    assert npbc_core.VALIDATE_REGEX['range'].match('') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('1') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('1 2') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('1-2') is not None
    assert npbc_core.VALIDATE_REGEX['range'].match('11') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('11-') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('11-12') is not None
    assert npbc_core.VALIDATE_REGEX['range'].match('11-12-1') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('11 -12') is not None
    assert npbc_core.VALIDATE_REGEX['range'].match('11 - 12') is not None
    assert npbc_core.VALIDATE_REGEX['range'].match('11- 12') is not None
    assert npbc_core.VALIDATE_REGEX['range'].match('11-2') is not None
    assert npbc_core.VALIDATE_REGEX['range'].match('11-12,13') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('11-12,13-14') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('111') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('a') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('1a') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('1a2') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('12b') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('11-a') is None
    assert npbc_core.VALIDATE_REGEX['range'].match('11-12a') is None

def test_regex_CSVs():
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('') is None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('1') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('a') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('adcef') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('-') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match(' ') is None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('1,2') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('1-3') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('monday') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('monday,tuesday') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('mondays') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('tuesdays') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('1,2,3') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('1-3') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('monday,tuesday') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('mondays,tuesdays') is not None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match(';') is None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match(':') is None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match(':') is None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('!') is None
    assert npbc_core.VALIDATE_REGEX['CSVs'].match('1,2,3,4') is not None

def test_regex_days():
    assert npbc_core.VALIDATE_REGEX['days'].match('') is None
    assert npbc_core.VALIDATE_REGEX['days'].match('1') is None
    assert npbc_core.VALIDATE_REGEX['days'].match('1,2') is None
    assert npbc_core.VALIDATE_REGEX['days'].match('1-3') is None
    assert npbc_core.VALIDATE_REGEX['days'].match('monday') is None
    assert npbc_core.VALIDATE_REGEX['days'].match('monday,tuesday') is None
    assert npbc_core.VALIDATE_REGEX['days'].match('mondays') is not None
    assert npbc_core.VALIDATE_REGEX['days'].match('tuesdays') is not None

def test_regex_n_days():
    assert npbc_core.VALIDATE_REGEX['n-day'].match('') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('1') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('1-') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('1,2') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('1-3') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('monday') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('monday,tuesday') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('mondays') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('1-tuesday') is not None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('11-tuesday') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('111-tuesday') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('11-tuesdays') is None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('1 -tuesday') is not None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('1- tuesday') is not None
    assert npbc_core.VALIDATE_REGEX['n-day'].match('1 - tuesday') is not None

def test_regex_hyphen():
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1-2') == ['1', '2']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1-2-3') == ['1', '2', '3']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1 -2-3') == ['1', '2', '3']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1 - 2-3') == ['1', '2', '3']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1- 2-3') == ['1', '2', '3']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1') == ['1']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1-') == ['1', '']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1-2-') == ['1', '2', '']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1-2-3-') == ['1', '2', '3', '']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1,2-3') == ['1,2', '3']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1,2-3-') == ['1,2', '3', '']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('1,2, 3,') == ['1,2, 3,']
    assert npbc_core.SPLIT_REGEX['hyphen'].split('') == ['']

def test_regex_comma():
    assert npbc_core.SPLIT_REGEX['comma'].split('1,2') == ['1', '2']
    assert npbc_core.SPLIT_REGEX['comma'].split('1,2,3') == ['1', '2', '3']
    assert npbc_core.SPLIT_REGEX['comma'].split('1 ,2,3') == ['1', '2', '3']
    assert npbc_core.SPLIT_REGEX['comma'].split('1 , 2,3') == ['1', '2', '3']
    assert npbc_core.SPLIT_REGEX['comma'].split('1, 2,3') == ['1', '2', '3']
    assert npbc_core.SPLIT_REGEX['comma'].split('1') == ['1']
    assert npbc_core.SPLIT_REGEX['comma'].split('1,') == ['1', '']
    assert npbc_core.SPLIT_REGEX['comma'].split('1, ') == ['1', '']
    assert npbc_core.SPLIT_REGEX['comma'].split('1,2,') == ['1', '2', '']
    assert npbc_core.SPLIT_REGEX['comma'].split('1,2,3,') == ['1', '2', '3', '']
    assert npbc_core.SPLIT_REGEX['comma'].split('1-2,3') == ['1-2', '3']
    assert npbc_core.SPLIT_REGEX['comma'].split('1-2,3,') == ['1-2', '3', '']
    assert npbc_core.SPLIT_REGEX['comma'].split('1-2-3') == ['1-2-3']
    assert npbc_core.SPLIT_REGEX['comma'].split('1-2- 3') == ['1-2- 3']
    assert npbc_core.SPLIT_REGEX['comma'].split('') == ['']

def test_undelivered_string_parsing():
    MONTH = 5
    YEAR = 2017


    assert npbc_core.parse_undelivered_string('', MONTH, YEAR) == set([])

    assert npbc_core.parse_undelivered_string('1', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=1)
    ])

    assert npbc_core.parse_undelivered_string('1-2', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=1),
        date_type(year=YEAR, month=MONTH, day=2)
    ])

    assert npbc_core.parse_undelivered_string('5-17', MONTH, YEAR) == set([
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

    assert npbc_core.parse_undelivered_string('5-17,19', MONTH, YEAR) == set([
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

    assert npbc_core.parse_undelivered_string('5-17,19-21', MONTH, YEAR) == set([
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

    assert npbc_core.parse_undelivered_string('5-17,19-21,23', MONTH, YEAR) == set([
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

    assert npbc_core.parse_undelivered_string('mondays', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=1),
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=15),
        date_type(year=YEAR, month=MONTH, day=22),
        date_type(year=YEAR, month=MONTH, day=29)
    ])

    assert npbc_core.parse_undelivered_string('mondays, wednesdays', MONTH, YEAR) == set([
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

    assert npbc_core.parse_undelivered_string('2-monday', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=8)
    ])

    assert npbc_core.parse_undelivered_string('2-monday, 3-wednesday', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=17)
    ])
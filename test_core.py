from npbc_core import VALIDATE_REGEX, SPLIT_REGEX, generate_sql_query, get_number_of_days_per_week, parse_undelivered_string
from datetime import date as date_type


def test_regex_number():
    assert VALIDATE_REGEX['number'].match('') is None
    assert VALIDATE_REGEX['number'].match('1') is not None
    assert VALIDATE_REGEX['number'].match('1 2') is None
    assert VALIDATE_REGEX['number'].match('1-2') is None
    assert VALIDATE_REGEX['number'].match('11') is not None
    assert VALIDATE_REGEX['number'].match('11-12') is None
    assert VALIDATE_REGEX['number'].match('11-12,13') is None
    assert VALIDATE_REGEX['number'].match('11-12,13-14') is None
    assert VALIDATE_REGEX['number'].match('111') is None
    assert VALIDATE_REGEX['number'].match('a') is None
    assert VALIDATE_REGEX['number'].match('1a') is None
    assert VALIDATE_REGEX['number'].match('1a2') is None
    assert VALIDATE_REGEX['number'].match('12b') is None

def test_regex_range():
    assert VALIDATE_REGEX['range'].match('') is None
    assert VALIDATE_REGEX['range'].match('1') is None
    assert VALIDATE_REGEX['range'].match('1 2') is None
    assert VALIDATE_REGEX['range'].match('1-2') is not None
    assert VALIDATE_REGEX['range'].match('11') is None
    assert VALIDATE_REGEX['range'].match('11-') is None
    assert VALIDATE_REGEX['range'].match('11-12') is not None
    assert VALIDATE_REGEX['range'].match('11-12-1') is None
    assert VALIDATE_REGEX['range'].match('11 -12') is not None
    assert VALIDATE_REGEX['range'].match('11 - 12') is not None
    assert VALIDATE_REGEX['range'].match('11- 12') is not None
    assert VALIDATE_REGEX['range'].match('11-2') is not None
    assert VALIDATE_REGEX['range'].match('11-12,13') is None
    assert VALIDATE_REGEX['range'].match('11-12,13-14') is None
    assert VALIDATE_REGEX['range'].match('111') is None
    assert VALIDATE_REGEX['range'].match('a') is None
    assert VALIDATE_REGEX['range'].match('1a') is None
    assert VALIDATE_REGEX['range'].match('1a2') is None
    assert VALIDATE_REGEX['range'].match('12b') is None
    assert VALIDATE_REGEX['range'].match('11-a') is None
    assert VALIDATE_REGEX['range'].match('11-12a') is None

def test_regex_CSVs():
    assert VALIDATE_REGEX['CSVs'].match('') is None
    assert VALIDATE_REGEX['CSVs'].match('1') is not None
    assert VALIDATE_REGEX['CSVs'].match('a') is not None
    assert VALIDATE_REGEX['CSVs'].match('adcef') is not None
    assert VALIDATE_REGEX['CSVs'].match('-') is not None
    assert VALIDATE_REGEX['CSVs'].match(' ') is None
    assert VALIDATE_REGEX['CSVs'].match('1,2') is not None
    assert VALIDATE_REGEX['CSVs'].match('1-3') is not None
    assert VALIDATE_REGEX['CSVs'].match('monday') is not None
    assert VALIDATE_REGEX['CSVs'].match('monday,tuesday') is not None
    assert VALIDATE_REGEX['CSVs'].match('mondays') is not None
    assert VALIDATE_REGEX['CSVs'].match('tuesdays') is not None
    assert VALIDATE_REGEX['CSVs'].match('1,2,3') is not None
    assert VALIDATE_REGEX['CSVs'].match('1-3') is not None
    assert VALIDATE_REGEX['CSVs'].match('monday,tuesday') is not None
    assert VALIDATE_REGEX['CSVs'].match('mondays,tuesdays') is not None
    assert VALIDATE_REGEX['CSVs'].match(';') is None
    assert VALIDATE_REGEX['CSVs'].match(':') is None
    assert VALIDATE_REGEX['CSVs'].match(':') is None
    assert VALIDATE_REGEX['CSVs'].match('!') is None
    assert VALIDATE_REGEX['CSVs'].match('1,2,3,4') is not None

def test_regex_days():
    assert VALIDATE_REGEX['days'].match('') is None
    assert VALIDATE_REGEX['days'].match('1') is None
    assert VALIDATE_REGEX['days'].match('1,2') is None
    assert VALIDATE_REGEX['days'].match('1-3') is None
    assert VALIDATE_REGEX['days'].match('monday') is None
    assert VALIDATE_REGEX['days'].match('monday,tuesday') is None
    assert VALIDATE_REGEX['days'].match('mondays') is not None
    assert VALIDATE_REGEX['days'].match('tuesdays') is not None

def test_regex_n_days():
    assert VALIDATE_REGEX['n-day'].match('') is None
    assert VALIDATE_REGEX['n-day'].match('1') is None
    assert VALIDATE_REGEX['n-day'].match('1-') is None
    assert VALIDATE_REGEX['n-day'].match('1,2') is None
    assert VALIDATE_REGEX['n-day'].match('1-3') is None
    assert VALIDATE_REGEX['n-day'].match('monday') is None
    assert VALIDATE_REGEX['n-day'].match('monday,tuesday') is None
    assert VALIDATE_REGEX['n-day'].match('mondays') is None
    assert VALIDATE_REGEX['n-day'].match('1-tuesday') is not None
    assert VALIDATE_REGEX['n-day'].match('11-tuesday') is None
    assert VALIDATE_REGEX['n-day'].match('111-tuesday') is None
    assert VALIDATE_REGEX['n-day'].match('11-tuesdays') is None
    assert VALIDATE_REGEX['n-day'].match('1 -tuesday') is not None
    assert VALIDATE_REGEX['n-day'].match('1- tuesday') is not None
    assert VALIDATE_REGEX['n-day'].match('1 - tuesday') is not None

def test_regex_costs():
    assert VALIDATE_REGEX['costs'].match('') is None
    assert VALIDATE_REGEX['costs'].match('a') is None
    assert VALIDATE_REGEX['costs'].match('1') is not None
    assert VALIDATE_REGEX['costs'].match('1.') is None
    assert VALIDATE_REGEX['costs'].match('1.5') is not None
    assert VALIDATE_REGEX['costs'].match('1.0') is not None
    assert VALIDATE_REGEX['costs'].match('16.0') is not None
    assert VALIDATE_REGEX['costs'].match('16.06') is not None
    assert VALIDATE_REGEX['costs'].match('1;2') is not None
    assert VALIDATE_REGEX['costs'].match('1 ;2') is not None
    assert VALIDATE_REGEX['costs'].match('1; 2') is not None
    assert VALIDATE_REGEX['costs'].match('1 ; 2') is not None
    assert VALIDATE_REGEX['costs'].match('1;2;') is not None
    assert VALIDATE_REGEX['costs'].match('1;2 ;') is not None
    assert VALIDATE_REGEX['costs'].match('1:2') is None
    assert VALIDATE_REGEX['costs'].match('1,2') is None
    assert VALIDATE_REGEX['costs'].match('1-2') is None
    assert VALIDATE_REGEX['costs'].match('1;2;3') is not None
    assert VALIDATE_REGEX['costs'].match('1;2;3;4') is not None
    assert VALIDATE_REGEX['costs'].match('1;2;3;4;5') is not None
    assert VALIDATE_REGEX['costs'].match('1;2;3;4;5;6') is not None
    assert VALIDATE_REGEX['costs'].match('1;2;3;4;5;6;7;') is not None
    assert VALIDATE_REGEX['costs'].match('1;2;3;4;5;6;7') is not None
    assert VALIDATE_REGEX['costs'].match('1;2;3;4;5;6;7;8') is None

def test_delivery_regex():
    assert VALIDATE_REGEX['delivery'].match('') is None
    assert VALIDATE_REGEX['delivery'].match('a') is None
    assert VALIDATE_REGEX['delivery'].match('1') is None
    assert VALIDATE_REGEX['delivery'].match('1.') is None
    assert VALIDATE_REGEX['delivery'].match('1.5') is None
    assert VALIDATE_REGEX['delivery'].match('1,2') is None
    assert VALIDATE_REGEX['delivery'].match('1-2') is None
    assert VALIDATE_REGEX['delivery'].match('1;2') is None
    assert VALIDATE_REGEX['delivery'].match('1:2') is None
    assert VALIDATE_REGEX['delivery'].match('1,2,3') is None
    assert VALIDATE_REGEX['delivery'].match('Y') is None
    assert VALIDATE_REGEX['delivery'].match('N') is None
    assert VALIDATE_REGEX['delivery'].match('YY') is None
    assert VALIDATE_REGEX['delivery'].match('YYY') is None
    assert VALIDATE_REGEX['delivery'].match('YYYY') is None
    assert VALIDATE_REGEX['delivery'].match('YYYYY') is None
    assert VALIDATE_REGEX['delivery'].match('YYYYYY') is None
    assert VALIDATE_REGEX['delivery'].match('YYYYYYY') is not None
    assert VALIDATE_REGEX['delivery'].match('YYYYYYYY') is None
    assert VALIDATE_REGEX['delivery'].match('NNNNNNN') is not None
    assert VALIDATE_REGEX['delivery'].match('NYNNNNN') is not None
    assert VALIDATE_REGEX['delivery'].match('NYYYYNN') is not None
    assert VALIDATE_REGEX['delivery'].match('NYYYYYY') is not None
    assert VALIDATE_REGEX['delivery'].match('NYYYYYYY') is None
    assert VALIDATE_REGEX['delivery'].match('N,N,N,N,N,N,N') is None
    assert VALIDATE_REGEX['delivery'].match('N;N;N;N;N;N;N') is None
    assert VALIDATE_REGEX['delivery'].match('N-N-N-N-N-N-N') is None
    assert VALIDATE_REGEX['delivery'].match('N N N N N N N') is None
    assert VALIDATE_REGEX['delivery'].match('YYYYYYy') is None
    assert VALIDATE_REGEX['delivery'].match('YYYYYYn') is None



def test_regex_hyphen():
    assert SPLIT_REGEX['hyphen'].split('1-2') == ['1', '2']
    assert SPLIT_REGEX['hyphen'].split('1-2-3') == ['1', '2', '3']
    assert SPLIT_REGEX['hyphen'].split('1 -2-3') == ['1', '2', '3']
    assert SPLIT_REGEX['hyphen'].split('1 - 2-3') == ['1', '2', '3']
    assert SPLIT_REGEX['hyphen'].split('1- 2-3') == ['1', '2', '3']
    assert SPLIT_REGEX['hyphen'].split('1') == ['1']
    assert SPLIT_REGEX['hyphen'].split('1-') == ['1', '']
    assert SPLIT_REGEX['hyphen'].split('1-2-') == ['1', '2', '']
    assert SPLIT_REGEX['hyphen'].split('1-2-3-') == ['1', '2', '3', '']
    assert SPLIT_REGEX['hyphen'].split('1,2-3') == ['1,2', '3']
    assert SPLIT_REGEX['hyphen'].split('1,2-3-') == ['1,2', '3', '']
    assert SPLIT_REGEX['hyphen'].split('1,2, 3,') == ['1,2, 3,']
    assert SPLIT_REGEX['hyphen'].split('') == ['']

def test_regex_comma():
    assert SPLIT_REGEX['comma'].split('1,2') == ['1', '2']
    assert SPLIT_REGEX['comma'].split('1,2,3') == ['1', '2', '3']
    assert SPLIT_REGEX['comma'].split('1 ,2,3') == ['1', '2', '3']
    assert SPLIT_REGEX['comma'].split('1 , 2,3') == ['1', '2', '3']
    assert SPLIT_REGEX['comma'].split('1, 2,3') == ['1', '2', '3']
    assert SPLIT_REGEX['comma'].split('1') == ['1']
    assert SPLIT_REGEX['comma'].split('1,') == ['1', '']
    assert SPLIT_REGEX['comma'].split('1, ') == ['1', '']
    assert SPLIT_REGEX['comma'].split('1,2,') == ['1', '2', '']
    assert SPLIT_REGEX['comma'].split('1,2,3,') == ['1', '2', '3', '']
    assert SPLIT_REGEX['comma'].split('1-2,3') == ['1-2', '3']
    assert SPLIT_REGEX['comma'].split('1-2,3,') == ['1-2', '3', '']
    assert SPLIT_REGEX['comma'].split('1-2-3') == ['1-2-3']
    assert SPLIT_REGEX['comma'].split('1-2- 3') == ['1-2- 3']
    assert SPLIT_REGEX['comma'].split('') == ['']

def test_regex_semicolon():
    assert SPLIT_REGEX['semicolon'].split('1;2') == ['1', '2']
    assert SPLIT_REGEX['semicolon'].split('1;2;3') == ['1', '2', '3']
    assert SPLIT_REGEX['semicolon'].split('1 ;2;3') == ['1', '2', '3']
    assert SPLIT_REGEX['semicolon'].split('1 ; 2;3') == ['1', '2', '3']
    assert SPLIT_REGEX['semicolon'].split('1; 2;3') == ['1', '2', '3']
    assert SPLIT_REGEX['semicolon'].split('1') == ['1']
    assert SPLIT_REGEX['semicolon'].split('1;') == ['1', '']
    assert SPLIT_REGEX['semicolon'].split('1; ') == ['1', '']
    assert SPLIT_REGEX['semicolon'].split('1;2;') == ['1', '2', '']
    assert SPLIT_REGEX['semicolon'].split('1;2;3;') == ['1', '2', '3', '']
    assert SPLIT_REGEX['semicolon'].split('1-2;3') == ['1-2', '3']
    assert SPLIT_REGEX['semicolon'].split('1-2;3;') == ['1-2', '3', '']
    assert SPLIT_REGEX['semicolon'].split('1-2-3') == ['1-2-3']
    assert SPLIT_REGEX['semicolon'].split('1-2- 3') == ['1-2- 3']
    assert SPLIT_REGEX['semicolon'].split('') == ['']


def test_undelivered_string_parsing():
    MONTH = 5
    YEAR = 2017


    assert parse_undelivered_string('', MONTH, YEAR) == set([])

    assert parse_undelivered_string('1', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=1)
    ])

    assert parse_undelivered_string('1-2', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=1),
        date_type(year=YEAR, month=MONTH, day=2)
    ])

    assert parse_undelivered_string('5-17', MONTH, YEAR) == set([
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

    assert parse_undelivered_string('5-17,19', MONTH, YEAR) == set([
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

    assert parse_undelivered_string('5-17,19-21', MONTH, YEAR) == set([
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

    assert parse_undelivered_string('5-17,19-21,23', MONTH, YEAR) == set([
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

    assert parse_undelivered_string('mondays', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=1),
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=15),
        date_type(year=YEAR, month=MONTH, day=22),
        date_type(year=YEAR, month=MONTH, day=29)
    ])

    assert parse_undelivered_string('mondays, wednesdays', MONTH, YEAR) == set([
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

    assert parse_undelivered_string('2-monday', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=8)
    ])

    assert parse_undelivered_string('2-monday, 3-wednesday', MONTH, YEAR) == set([
        date_type(year=YEAR, month=MONTH, day=8),
        date_type(year=YEAR, month=MONTH, day=17)
    ])


def test_sql_query():
    assert generate_sql_query(
        'test'
    ) == "SELECT * FROM test;"

    assert generate_sql_query(
        'test',
        columns=['a']
    ) == "SELECT a FROM test;"

    assert generate_sql_query(
        'test',
        columns=['a', 'b']
    ) == "SELECT a, b FROM test;"

    assert generate_sql_query(
        'test',
        conditions={'a': '\"b\"'}
    ) == "SELECT * FROM test WHERE a = \"b\";"

    assert generate_sql_query(
        'test',
        conditions={
            'a': '\"b\"',
            'c': '\"d\"'
        }
    ) == "SELECT * FROM test WHERE a = \"b\" AND c = \"d\";"

    assert generate_sql_query(
        'test',
        conditions={
            'a': '\"b\"',
            'c': '\"d\"'
        },
        columns=['a', 'b']
    ) == "SELECT a, b FROM test WHERE a = \"b\" AND c = \"d\";"


def test_number_of_days_per_week():
    assert get_number_of_days_per_week(1, 2022) == [5, 4, 4, 4, 4, 5, 5]
    assert get_number_of_days_per_week(2, 2022) == [4, 4, 4, 4, 4, 4, 4]
    assert get_number_of_days_per_week(3, 2022) == [4, 5, 5 ,5, 4, 4, 4]
    assert get_number_of_days_per_week(2, 2020) == [4, 4, 4, 4, 4, 5, 4]
    assert get_number_of_days_per_week(12, 1954) == [4, 4, 5, 5, 5, 4, 4]
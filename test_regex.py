import npbc_regex

def test_regex_number():
    assert npbc_regex.NUMBER_MATCH_REGEX.match('') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('1') is not None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('1 2') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('1-2') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('11') is not None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('11-12') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('11-12,13') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('11-12,13-14') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('111') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('a') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('1a') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('1a2') is None
    assert npbc_regex.NUMBER_MATCH_REGEX.match('12b') is None

def test_regex_range():
    assert npbc_regex.RANGE_MATCH_REGEX.match('') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('1') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('1 2') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('1-2') is not None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11-') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11-12') is not None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11-12-1') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11 -12') is not None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11 - 12') is not None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11- 12') is not None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11-2') is not None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11-12,13') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11-12,13-14') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('111') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('a') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('1a') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('1a2') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('12b') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11-a') is None
    assert npbc_regex.RANGE_MATCH_REGEX.match('11-12a') is None

def test_regex_CSVs():
    assert npbc_regex.CSV_MATCH_REGEX.match('') is None
    assert npbc_regex.CSV_MATCH_REGEX.match('1') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('a') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('adcef') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('-') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match(' ') is None
    assert npbc_regex.CSV_MATCH_REGEX.match('1,2') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('1-3') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('monday') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('monday,tuesday') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('mondays') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('tuesdays') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('1,2,3') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('1-3') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('monday,tuesday') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match('mondays,tuesdays') is not None
    assert npbc_regex.CSV_MATCH_REGEX.match(';') is None
    assert npbc_regex.CSV_MATCH_REGEX.match(':') is None
    assert npbc_regex.CSV_MATCH_REGEX.match(':') is None
    assert npbc_regex.CSV_MATCH_REGEX.match('!') is None
    assert npbc_regex.CSV_MATCH_REGEX.match('1,2,3,4') is not None

def test_regex_days():
    assert npbc_regex.DAYS_MATCH_REGEX.match('') is None
    assert npbc_regex.DAYS_MATCH_REGEX.match('1') is None
    assert npbc_regex.DAYS_MATCH_REGEX.match('1,2') is None
    assert npbc_regex.DAYS_MATCH_REGEX.match('1-3') is None
    assert npbc_regex.DAYS_MATCH_REGEX.match('monday') is None
    assert npbc_regex.DAYS_MATCH_REGEX.match('monday,tuesday') is None
    assert npbc_regex.DAYS_MATCH_REGEX.match('mondays') is not None
    assert npbc_regex.DAYS_MATCH_REGEX.match('tuesdays') is not None

def test_regex_n_days():
    assert npbc_regex.N_DAY_MATCH_REGEX.match('') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('1') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('1-') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('1,2') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('1-3') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('monday') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('monday,tuesday') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('mondays') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('1-tuesday') is not None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('11-tuesday') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('111-tuesday') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('11-tuesdays') is None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('1 -tuesday') is not None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('1- tuesday') is not None
    assert npbc_regex.N_DAY_MATCH_REGEX.match('1 - tuesday') is not None

def test_regex_all_text():
    assert npbc_regex.ALL_MATCH_REGEX.match('') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('1') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('1-') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('1,2') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('1-3') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('monday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('monday,tuesday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('mondays') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('tuesdays') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('1-tuesday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('11-tuesday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('111-tuesday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('11-tuesdays') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('1 -tuesday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('1- tuesday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('1 - tuesday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('all') is not None
    assert npbc_regex.ALL_MATCH_REGEX.match('all,tuesday') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('all,tuesdays') is None
    assert npbc_regex.ALL_MATCH_REGEX.match('All') is not None
    assert npbc_regex.ALL_MATCH_REGEX.match('AlL') is not None
    assert npbc_regex.ALL_MATCH_REGEX.match('ALL') is not None

def test_delivery_regex():
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('a') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('1') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('1.') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('1.5') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('1,2') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('1-2') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('1;2') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('1:2') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('1,2,3') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('Y') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('N') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YY') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YYY') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YYYY') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YYYYY') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YYYYYY') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YYYYYYY') is not None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YYYYYYYY') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('NNNNNNN') is not None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('NYNNNNN') is not None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('NYYYYNN') is not None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('NYYYYYY') is not None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('NYYYYYYY') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('N,N,N,N,N,N,N') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('N;N;N;N;N;N;N') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('N-N-N-N-N-N-N') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('N N N N N N N') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YYYYYYy') is None
    assert npbc_regex.DELIVERY_MATCH_REGEX.match('YYYYYYn') is None



def test_regex_hyphen():
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1-2') == ['1', '2']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1-2-3') == ['1', '2', '3']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1 -2-3') == ['1', '2', '3']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1 - 2-3') == ['1', '2', '3']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1- 2-3') == ['1', '2', '3']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1') == ['1']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1-') == ['1', '']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1-2-') == ['1', '2', '']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1-2-3-') == ['1', '2', '3', '']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1,2-3') == ['1,2', '3']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1,2-3-') == ['1,2', '3', '']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('1,2, 3,') == ['1,2, 3,']
    assert npbc_regex.HYPHEN_SPLIT_REGEX.split('') == ['']

def test_regex_comma():
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1,2') == ['1', '2']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1,2,3') == ['1', '2', '3']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1 ,2,3') == ['1', '2', '3']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1 , 2,3') == ['1', '2', '3']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1, 2,3') == ['1', '2', '3']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1') == ['1']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1,') == ['1', '']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1, ') == ['1', '']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1,2,') == ['1', '2', '']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1,2,3,') == ['1', '2', '3', '']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1-2,3') == ['1-2', '3']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1-2,3,') == ['1-2', '3', '']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1-2-3') == ['1-2-3']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('1-2- 3') == ['1-2- 3']
    assert npbc_regex.COMMA_SPLIT_REGEX.split('') == ['']

def test_regex_semicolon():
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1;2') == ['1', '2']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1;2;3') == ['1', '2', '3']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1 ;2;3') == ['1', '2', '3']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1 ; 2;3') == ['1', '2', '3']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1; 2;3') == ['1', '2', '3']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1') == ['1']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1;') == ['1', '']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1; ') == ['1', '']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1;2;') == ['1', '2', '']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1;2;3;') == ['1', '2', '3', '']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1-2;3') == ['1-2', '3']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1-2;3;') == ['1-2', '3', '']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1-2-3') == ['1-2-3']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('1-2- 3') == ['1-2- 3']
    assert npbc_regex.SEMICOLON_SPLIT_REGEX.split('') == ['']
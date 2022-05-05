from calendar import day_name as WEEKDAY_NAMES_ITERABLE
from re import compile as compile_regex, match


## regex used to match against strings

# match for a list of comma separated values. each value must be/contain digits, or letters, or hyphens. spaces are allowed between values and commas. any number of values are allowed, but at least one must be present.
CSV_MATCH_REGEX = compile_regex(r'^[-\w]+( *, *[-\w]+)*( *,)?$')

# match for a single number. must be one or two digits
NUMBER_MATCH_REGEX = compile_regex(r'^[\d]{1,2}?$')

# match for a range of numbers. each number must be one or two digits. numbers are separated by a hyphen. spaces are allowed between numbers and the hyphen.
RANGE_MATCH_REGEX = compile_regex(r'^\d{1,2} *- *\d{1,2}$')

# match for weekday name. day must appear as "daynames" (example = "mondays"). all lowercase.
DAYS_MATCH_REGEX = compile_regex(f"^{'|'.join([day_name.lower() + 's' for day_name in WEEKDAY_NAMES_ITERABLE])}$")

# match for nth weekday name. day must appear as "n-dayname" (example = "1-monday"). all lowercase. must be one digit.
N_DAY_MATCH_REGEX = compile_regex(f"^\\d *- *({'|'.join([day_name.lower() for day_name in WEEKDAY_NAMES_ITERABLE])})$")

# match for the text "all" in any case.
ALL_MATCH_REGEX = compile_regex(r'^[aA][lL]{2}$')

# match for real values, delimited by semicolons. each value must be either an integer or a float with a decimal point. spaces are allowed between values and semicolons, and up to 7 (but at least 1) values are allowed.
COSTS_MATCH_REGEX = compile_regex(r'^\d+(\.\d+)?( *; *\d+(\.\d+)?){0,6} *;?$')

# match for seven values, each of which must be a 'Y' or an 'N'. there are no delimiters.
DELIVERY_MATCH_REGEX = compile_regex(r'^[YN]{7}$')


## regex used to split strings

# split on hyphens. spaces are allowed between hyphens and values.
HYPHEN_SPLIT_REGEX = compile_regex(r' *- *')

# split on semicolons. spaces are allowed between hyphens and values.
SEMICOLON_SPLIT_REGEX = compile_regex(r' *; *')

# split on commas. spaces are allowed between commas and values.
COMMA_SPLIT_REGEX = compile_regex(r' *, *')
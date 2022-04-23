from sqlite3 import connect
from calendar import day_name as weekday_names_iterable
from calendar import monthrange, monthcalendar
from datetime import date as date_type, datetime, timedelta
from pathlib import Path
from re import compile as compile_regex

DATABASE_DIR = Path().home() / '.npbc'
DATABASE_DIR = Path('data')

DATABASE_PATH = DATABASE_DIR / 'npbc.db'

SCHEMA_PATH = Path(__file__).parent / 'schema.sql'
SCHEMA_PATH = DATABASE_DIR / 'schema.sql'

WEEKDAY_NAMES = list(weekday_names_iterable)

VALIDATE_REGEX = {
    # match for a list of comma separated values. each value must be/contain digits, or letters, or hyphens. spaces are allowed between values and commas.
    'CSVs': compile_regex(r'^[-\w]+( *, *[-\w]+)*( *,)?$'),

    # match for a single number. must be one or two digits
    'number': compile_regex(r'^[\d]{1,2}?$'),

    # match for a range of numbers. each number must be one or two digits. numbers are separated by a hyphen. spaces are allowed between numbers and the hyphen.
    'range': compile_regex(r'^\d{1,2} *- *\d{1,2}$'),

    # match for weekday name. day must appear as "daynames" (example: "mondays"). all lowercase.
    'days': compile_regex(f"^{'|'.join([day_name.lower() + 's' for day_name in WEEKDAY_NAMES])}$"),

    # match for nth weekday name. day must appear as "n-dayname" (example: "1-monday"). all lowercase. must be one digit.
    'n-day': compile_regex(f"^\\d *- *({'|'.join([day_name.lower() for day_name in WEEKDAY_NAMES])})$")
}

SPLIT_REGEX = {
    # split on hyphens. spaces are allowed between hyphens and values.
    'hyphen': compile_regex(r' *- *'),

    # split on commas. spaces are allowed between commas and values.
    'comma': compile_regex(r' *, *')
}


def setup_and_connect_DB() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.touch(exist_ok=True)

    with connect(DATABASE_PATH) as connection:
        connection.executescript(SCHEMA_PATH.read_text())
        connection.commit()

def generate_sql_query(table_name: str, parameters: dict[str, int | str] | None = None) -> str:
    sql_query = f"SELECT * FROM {table_name}"

    if parameters:
        conditions = ' AND '.join([
            f"{parameter_name} = {parameter_value}"
            for parameter_name, parameter_value in parameters.items()
        ])
        
        sql_query += f" WHERE {conditions};"

    return f"{sql_query};"

def get_number_of_days_per_week(month: int, year: int) -> list[int]:
    return [
        7 - week.count(0)
        for week in monthcalendar(year, month)
    ]

def validate_undelivered_string(string: str) -> bool:
    if VALIDATE_REGEX['CSVs'].match(string):
        
        for section in SPLIT_REGEX['comma'].split(string):
            section_validity = False

            for pattern, regex in VALIDATE_REGEX.items():
                if (pattern != "CSVs") and (regex.match(section)):
                    if not section_validity:
                        section_validity = True

            if not section_validity:
                return False
        
        return True
    
    return False

def parse_undelivered_string(string: str, month: int, year: int) -> set[date_type]:
    dates = set()

    for section in SPLIT_REGEX['comma'].split(string):
        if VALIDATE_REGEX['number'].match(section):
            print(f"{section} is a number")
            date = int(section)

            if date > 0 and date <= monthrange(year, month)[1]:
                dates.add(date_type(year, month, date))

        elif VALIDATE_REGEX['range'].match(section):
            start, end = [int(date) for date in SPLIT_REGEX['hyphen'].split(section)]

            if 0 < start <= end <= monthrange(year, month)[1]:
                dates.update(
                    date_type(year, month, day)
                    for day in range(start, end + 1)
                )

        elif VALIDATE_REGEX['days'].match(section):
            weekday = WEEKDAY_NAMES.index(section.capitalize().rstrip('s'))

            dates.update(
                date_type(year, month, day)
                for day in range(1, monthrange(year, month)[1] + 1)
                if date_type(year, month, day).weekday() == weekday
            )

        elif VALIDATE_REGEX['n-day'].match(section):
            n, weekday = SPLIT_REGEX['hyphen'].split(section)

            n = int(n)

            if n > 0 and n <= len(get_number_of_days_per_week(month, year)):
                weekday = WEEKDAY_NAMES.index(weekday.capitalize())

                valid_dates = [
                    date_type(year, month, day)
                    for day in range(1, monthrange(year, month)[1] + 1)
                    if date_type(year, month, day).weekday() == weekday
                ]

                dates.add(valid_dates[n - 1])

        else:
            print("Congratulations! You broke the program!")
            print("You managed to write a string that the program considers valid, but isn't actually.")
            print("Please report it to the developer.")
            print(f"\nThe string you wrote was: {string}")

    return dates

def main():
    MONTH = 5
    YEAR = 2017
    print(parse_undelivered_string('Mondays', MONTH, YEAR))

if __name__ == '__main__':
    main()
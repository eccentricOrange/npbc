from pathlib import Path
from calendar import day_name as weekday_names_iterable, monthcalendar
from sqlite3 import connect
from typing import Generator


## paths for the folder containing schema and database files
 # during normal use, the DB will be in ~/.npbc (where ~ is the user's home directory) and the schema will be bundled with the executable
 # during development, the DB and schema will both be in "data"

DATABASE_DIR = Path().home() / '.npbc'  # normal use path
# DATABASE_DIR = Path('data')  # development path

DATABASE_PATH = DATABASE_DIR / 'npbc.db'

SCHEMA_PATH = Path(__file__).parent / 'schema.sql'  # normal use path
# SCHEMA_PATH = DATABASE_DIR / 'schema.sql'  # development path


## list constant for names of weekdays
WEEKDAY_NAMES = list(weekday_names_iterable)


## ensure DB exists and it's set up with the schema
def setup_and_connect_DB() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.touch(exist_ok=True)

    with connect(DATABASE_PATH) as connection:
        connection.executescript(SCHEMA_PATH.read_text())
        connection.commit()


## generate a list of number of times each weekday occurs in a given month (return a generator)
 # the list will be in the same order as WEEKDAY_NAMES (so the first day should be Monday)
def get_number_of_each_weekday(month: int, year: int) -> Generator[int, None, None]:
    main_calendar = monthcalendar(year, month)
    number_of_weeks = len(main_calendar)

    for i, _ in enumerate(WEEKDAY_NAMES):
        number_of_weekday: int = number_of_weeks

        if main_calendar[0][i] == 0:
            number_of_weekday -= 1
        
        if main_calendar[-1][i] == 0:
            number_of_weekday -= 1

        yield number_of_weekday



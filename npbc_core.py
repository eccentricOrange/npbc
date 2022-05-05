from datetime import date as date_type, datetime, timedelta
from pathlib import Path
from calendar import day_name as weekday_names_iterable, monthcalendar, monthrange
from sqlite3 import Connection, connect
from textwrap import indent
from typing import Generator
import npbc_regex
from json import dumps


## paths for the folder containing schema and database files
 # during normal use, the DB will be in ~/.npbc (where ~ is the user's home directory) and the schema will be bundled with the executable
 # during development, the DB and schema will both be in "data"

DATABASE_DIR = Path().home() / '.npbc'  # normal use path
DATABASE_DIR = Path('data')  # development path

DATABASE_PATH = DATABASE_DIR / 'npbc.db'

SCHEMA_PATH = Path(__file__).parent / 'schema.sql'  # normal use path
SCHEMA_PATH = DATABASE_DIR / 'schema.sql'  # development path


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


## validate a string that specifies when a given paper was not delivered
# first check to see that it meets the comma-separated requirements
# then check against each of the other acceptable patterns in the regex dictionary
def validate_undelivered_string(*strings: str) -> bool:
    # check that the string matches one of the acceptable patterns
    for string in strings:
        if string and not (
            npbc_regex.NUMBER_MATCH_REGEX.match(string) or
            npbc_regex.RANGE_MATCH_REGEX.match(string) or
            npbc_regex.DAYS_MATCH_REGEX.match(string) or
            npbc_regex.N_DAY_MATCH_REGEX.match(string) or
            npbc_regex.ALL_MATCH_REGEX.match(string)
        ):

            return False

    # if we get here, all strings passed the regex check
    return True

## if the date is simply a number, it's a single day. so we just identify that date
def extract_number(string: str, month: int, year: int) -> date_type | None:
    date = int(string)

    if date > 0 and date <= monthrange(year, month)[1]:
        return date_type(year, month, date)


## if the date is a range of numbers, it's a range of days. we identify all the dates in that range, bounds inclusive
def extract_range(string: str, month: int, year: int) -> Generator[date_type, None, None]:
    start, end = [int(date) for date in npbc_regex.HYPHEN_SPLIT_REGEX.split(string)]

    if 0 < start <= end <= monthrange(year, month)[1]:
        for date in range(start, end + 1):
            yield date_type(year, month, date)


## if the date is the plural of a weekday name, we identify all dates in that month which are the given weekday
def extract_weekday(string: str, month: int, year: int) -> Generator[date_type, None, None]:
    weekday = WEEKDAY_NAMES.index(string.capitalize().rstrip('s'))

    for day in range(1, monthrange(year, month)[1] + 1):
        if date_type(year, month, day).weekday() == weekday:
            yield date_type(year, month, day)


## if the date is a number and a weekday name (singular), we identify the date that is the nth occurrence of the given weekday in the month
def extract_nth_weekday(string: str, month: int, year: int) -> date_type | None:
    n, weekday_name = npbc_regex.HYPHEN_SPLIT_REGEX.split(string)

    n = int(n)

    if n > 0 and n <= list(get_number_of_each_weekday(month, year))[WEEKDAY_NAMES.index(weekday_name.capitalize())]:
        weekday = WEEKDAY_NAMES.index(weekday_name.capitalize())

        valid_dates = [
            date_type(year, month, day)
            for day in range(1, monthrange(year, month)[1] + 1)
            if date_type(year, month, day).weekday() == weekday
        ]

        return valid_dates[n - 1]


## if the text is "all", we identify all the dates in the month
def extract_all(month: int, year: int) -> Generator[date_type, None, None]:
    for day in range(1, monthrange(year, month)[1] + 1):
        yield date_type(year, month, day)


## parse a section of the strings
 # each section is a string that specifies a set of dates
 # this function will return a set of dates that uniquely identifies each date mentioned across the string
def parse_undelivered_string(month: int, year: int, string: str) -> set[date_type]:
    # initialize the set of dates
    dates = set()

    # check for each of the patterns
    if npbc_regex.NUMBER_MATCH_REGEX.match(string):
        number_date = extract_number(string, month, year)

        if number_date:
            dates.add(number_date)

    elif npbc_regex.RANGE_MATCH_REGEX.match(string):
        dates.update(extract_range(string, month, year))

    elif npbc_regex.DAYS_MATCH_REGEX.match(string):
        dates.update(extract_weekday(string, month, year))

    elif npbc_regex.N_DAY_MATCH_REGEX.match(string):
        n_day_date = extract_nth_weekday(string, month, year)

        if n_day_date:
            dates.add(n_day_date)

    elif npbc_regex.ALL_MATCH_REGEX.match(string):
        dates.update(extract_all(month, year))

    else:
        raise ValueError

    return dates

    
## parse a string that specifies when a given paper was not delivered
 # each section states some set of dates
 # this function will return a set of dates that uniquely identifies each date mentioned across all the strings
def parse_undelivered_strings(month: int, year: int, *strings: str) -> set[date_type]:
    # initialize the set of dates
    dates = set()

    # check for each of the patterns
    for string in strings:
        try:
            dates.update(parse_undelivered_string(month, year, string))

        except ValueError:
            print(
                f"""Congratulations! You broke the program!
                You managed to write a string that the program considers valid, but isn't actually.
                Please report it to the developer.
                \nThe string you wrote was: {string}
                This data has not been counted."""
            )

    return dates


## get the cost and delivery data for a given paper from the DB
 # each of them are converted to a dictionary, whose index is the day_id
 # the two dictionaries are then returned as a tuple
def get_cost_and_delivery_data(paper_id: int, connection: Connection) -> tuple[dict[int, float], dict[int, bool]]:
    query = """
        SELECT papers_days.day_id, papers_days_delivered.delivered, papers_days_cost.cost
        FROM papers_days
        LEFT JOIN papers_days_delivered
        ON papers_days.paper_day_id = papers_days_delivered.paper_day_id
        LEFT JOIN papers_days_cost
        ON papers_days.paper_day_id = papers_days_cost.paper_day_id
        WHERE papers_days.paper_id = ?
    """

    retrieved_data = connection.execute(query, (paper_id, )).fetchall()
    
    cost_dict = {
        row[0]: row[2]
        for row in retrieved_data
    }

    delivered_dict = {
        row[0]: bool(row[1])
        for row in retrieved_data
    }

    return cost_dict, delivered_dict


## calculate the cost of one paper for the full month
 # any dates when it was not delivered will be removed
def calculate_cost_of_one_paper(number_of_each_weekday: list[int], undelivered_dates: set[date_type], cost_and_delivered_data: tuple[dict[int, float], dict[int, bool]]) -> float:
    cost_data, delivered_data = cost_and_delivered_data
    
    # initialize counters corresponding to each weekday when the paper was not delivered
    number_of_days_per_weekday_not_received = [0] * len(number_of_each_weekday)

    # for each date that the paper was not delivered, we increment the counter for the corresponding weekday
    for date in undelivered_dates:
        number_of_days_per_weekday_not_received[date.weekday()] += 1
    
    # calculate the total number of each weekday the paper was delivered (if it is supposed to be delivered)
    number_of_days_delivered = [
        number_of_each_weekday[day_id] - number_of_days_per_weekday_not_received[day_id] if delivered else 0
        for day_id, delivered in delivered_data.items()
    ]

    # calculate the total cost of the paper for the month
    return sum(
        cost * number_of_days_delivered[day_id]
        for day_id, cost in cost_data.items()
    )


## calculate the cost of all papers for the full month
 # return data about the cost of each paper, the total cost, and dates when each paper was not delivered
def calculate_cost_of_all_papers(undelivered_strings: dict[int, list[str]], month: int, year: int) -> tuple[dict[int, float], float, dict[int, set[date_type]]]:
    NUMBER_OF_EACH_WEEKDAY = list(get_number_of_each_weekday(month, year))
    cost_and_delivery_data = []

    # get the IDs of papers that exist
    with connect(DATABASE_PATH) as connection:
        papers = connection.execute("SELECT paper_id FROM papers;").fetchall()

        # get the data about cost and delivery for each paper
        cost_and_delivery_data = [
            get_cost_and_delivery_data(paper_id, connection)
            for paper_id, in papers # type: ignore
        ]

    # initialize a "blank" dictionary that will eventually contain any dates when a paper was not delivered
    undelivered_dates: dict[int, set[date_type]] = {
        paper_id: set()
        for paper_id, in papers # type: ignore
    }

    # calculate the undelivered dates for each paper
    for paper_id, strings in undelivered_strings.items():
        undelivered_dates[paper_id].update(
            parse_undelivered_strings(month, year, *strings)
        )

    # calculate the cost of each paper
    costs = {
        paper_id: calculate_cost_of_one_paper(
            NUMBER_OF_EACH_WEEKDAY,
            undelivered_dates[paper_id],
            cost_and_delivery_data[index]
        )
        for index, (paper_id,) in enumerate(papers) # type: ignore
    }

    # calculate the total cost of all papers
    total = sum(costs.values())

    return costs, total, undelivered_dates


## save the results of undelivered dates to the DB
 # save the dates any paper was not delivered
def save_results(costs: dict[int, float], undelivered_dates: dict[int, set[date_type]], month: int, year: int) -> None:
    timestamp = datetime.now().strftime(r'%d/%m/%Y %I:%M:%S %p')

    with connect(DATABASE_PATH) as connection:

        # create log entries for each paper
        log_ids = {
            paper_id: connection.execute(
                """
                INSERT INTO logs (paper_id, month, year, timestamp)
                VALUES (?, ?, ?, ?)
                RETURNING log_id;
                """,
                (paper_id, month, year, timestamp)
            ).fetchone()
            for paper_id in costs.keys()
        }

        # create cost entries for each paper
        for paper_id, log_id in log_ids.items():
            connection.execute(
                """
                INSERT INTO cost_logs (log_id, cost)
                VALUES (?, ?);
                """,
                (log_id, costs[paper_id])
            )

        # create undelivered entries for each paper
        for paper_id, dates in undelivered_dates.items():
            for date in dates:
                connection.execute(
                    """
                    INSERT INTO undelivered_logs (log_id, day_id)
                    VALUES (?, ?);
                    """,
                    (log_ids[paper_id], date.strftime("%Y-%m-%d"))
                )



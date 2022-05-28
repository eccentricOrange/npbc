"""
provides the core functionality
- sets up and communicates with the DB
- adds, deletes, edits, or retrieves data from the DB (such as undelivered strings, paper data, logs)
- performs the main calculations
- handles validation and parsing of many values (such as undelivered strings)
"""

from calendar import day_name as weekday_names_iterable
from calendar import monthcalendar, monthrange
from datetime import date as date_type
from datetime import datetime, timedelta
from os import environ
from pathlib import Path
from sqlite3 import Connection, connect
from typing import Generator

import npbc_exceptions
import npbc_regex

## paths for the folder containing schema and database files
# during normal use, the DB will be in ~/.npbc (where ~ is the user's home directory) and the schema will be bundled with the executable
# during development, the DB and schema will both be in "data"

# default to PRODUCTION
DATABASE_DIR = Path.home() / '.npbc'
SCHEMA_PATH = Path(__file__).parent / 'schema.sql'

# if in a development environment, set the paths to the data folder
if environ.get('NPBC_DEVELOPMENT') or environ.get('CI'):
    DATABASE_DIR = Path('data')
    SCHEMA_PATH = Path('data') / 'schema.sql'

DATABASE_PATH = DATABASE_DIR / 'npbc.db'

## list constant for names of weekdays
WEEKDAY_NAMES = list(weekday_names_iterable)

def setup_and_connect_DB() -> None:
    """ensure DB exists and it's set up with the schema"""

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.touch(exist_ok=True)

    with connect(DATABASE_PATH) as connection:
        connection.executescript(SCHEMA_PATH.read_text())

    connection.close()


def get_number_of_each_weekday(month: int, year: int) -> Generator[int, None, None]:
    """generate a list of number of times each weekday occurs in a given month (return a generator)
    - the list will be in the same order as WEEKDAY_NAMES (so the first day should be Monday)"""

    # get the calendar for the month
    main_calendar = monthcalendar(year, month)

    # get the number of weeks in that month from the calendar
    number_of_weeks = len(main_calendar)

    # iterate over each possible weekday
    for i, _ in enumerate(WEEKDAY_NAMES):

        # assume that the weekday occurs once per week in the month
        number_of_weekday: int = number_of_weeks

        # if the first week doesn't have the weekday, decrement its count
        if main_calendar[0][i] == 0:
            number_of_weekday -= 1
        
        # if the last week doesn't have the weekday, decrement its count
        if main_calendar[-1][i] == 0:
            number_of_weekday -= 1

        yield number_of_weekday


def validate_undelivered_string(*strings: str) -> None:
    """validate a string that specifies when a given paper was not delivered
    - first check to see that it meets the comma-separated requirements
    - then check against each of the other acceptable patterns in the regex dictionary"""

    # check that the string matches one of the acceptable patterns
    for string in strings:
        if string and not (
            npbc_regex.NUMBER_MATCH_REGEX.match(string) or
            npbc_regex.RANGE_MATCH_REGEX.match(string) or
            npbc_regex.DAYS_MATCH_REGEX.match(string) or
            npbc_regex.N_DAY_MATCH_REGEX.match(string) or
            npbc_regex.ALL_MATCH_REGEX.match(string)
        ):

            raise npbc_exceptions.InvalidUndeliveredString(f'{string} is not a valid undelivered string.')

    # if we get here, all strings passed the regex check

def extract_number(string: str, month: int, year: int) -> date_type | None:
    """if the date is simply a number, it's a single day. so we just identify that date"""

    date = int(string)

    # if the date is valid for the given month
    if date > 0 and date <= monthrange(year, month)[1]:
        return date_type(year, month, date)


def extract_range(string: str, month: int, year: int) -> Generator[date_type, None, None]:
    """if the date is a range of numbers, it's a range of days. we identify all the dates in that range, bounds inclusive"""

    start, end = map(int, npbc_regex.HYPHEN_SPLIT_REGEX.split(string))

    # if the range is valid for the given month
    if 0 < start <= end <= monthrange(year, month)[1]:
        for date in range(start, end + 1):
            yield date_type(year, month, date)


def extract_weekday(string: str, month: int, year: int) -> Generator[date_type, None, None]:
    """if the date is the plural of a weekday name, we identify all dates in that month which are the given weekday"""

    weekday = WEEKDAY_NAMES.index(string.capitalize().rstrip('s'))

    for day in range(1, monthrange(year, month)[1] + 1):
        if date_type(year, month, day).weekday() == weekday:
            yield date_type(year, month, day)


def extract_nth_weekday(string: str, month: int, year: int) -> date_type | None:
    """if the date is a number and a weekday name (singular), we identify the date that is the nth occurrence of the given weekday in the month"""

    n, weekday_name = npbc_regex.HYPHEN_SPLIT_REGEX.split(string)

    n = int(n)

    # if the day is valid for the given month
    if n > 0 and n <= list(get_number_of_each_weekday(month, year))[WEEKDAY_NAMES.index(weekday_name.capitalize())]:
        
        # record the "day_id" corresponding to the given weekday name
        weekday = WEEKDAY_NAMES.index(weekday_name.capitalize())

        # store all dates when the given weekday occurs in the given month
        valid_dates = [
            date_type(year, month, day)
            for day in range(1, monthrange(year, month)[1] + 1)
            if date_type(year, month, day).weekday() == weekday
        ]

        # return the date that is the nth occurrence of the given weekday in the month
        return valid_dates[n - 1]


def extract_all(month: int, year: int) -> Generator[date_type, None, None]:
    """if the text is "all", we identify all the dates in the month"""

    for day in range(1, monthrange(year, month)[1] + 1):
        yield date_type(year, month, day)


def parse_undelivered_string(month: int, year: int, string: str) -> set[date_type]:
    """parse a section of the strings
    - each section is a string that specifies a set of dates
    - this function will return a set of dates that uniquely identifies each date mentioned across the string"""

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
        raise npbc_exceptions.InvalidUndeliveredString(f'{string} is not a valid undelivered string.')

    return dates

    
def parse_undelivered_strings(month: int, year: int, *strings: str) -> set[date_type]:
    """parse a string that specifies when a given paper was not delivered
    - each section states some set of dates
    - this function will return a set of dates that uniquely identifies each date mentioned across all the strings"""
    
    # initialize the set of dates
    dates = set()

    # check for each of the patterns
    for string in strings:
        try:
            dates.update(parse_undelivered_string(month, year, string))

        except npbc_exceptions.InvalidUndeliveredString:
            print(
                f"""Congratulations! You broke the program!
                You managed to write a string that the program considers valid, but isn't actually.
                Please report it to the developer.
                \nThe string you wrote was: {string}
                This data has not been counted."""
            )

    return dates


def get_cost_and_delivery_data(paper_id: int, connection: Connection) -> list[tuple[bool, float]]:
    """get the cost and delivery data for a given paper from the DB"""
    
    query = """
        SELECT delivered, cost FROM cost_and_delivery_data
        WHERE paper_id = ?
        ORDER BY day_id;
    """

    # return a list but convert the delivery data to Booleans because SQLite won't do it
    return list(map(
        lambda row: (bool(row[0]), row[1]),
        connection.execute(query, (paper_id,)).fetchall()
    ))


def calculate_cost_of_one_paper(
        number_of_each_weekday: list[int],
        undelivered_dates: set[date_type],
        cost_and_delivered_data: list[tuple[bool, float]]
    ) -> float:
    """calculate the cost of one paper for the full month
    - any dates when it was not delivered will be removed"""
    
    # initialize counters corresponding to each weekday when the paper was not delivered
    number_of_days_per_weekday_not_received = [0] * len(number_of_each_weekday)
    
    # for each date that the paper was not delivered, we increment the counter for the corresponding weekday
    for date in undelivered_dates:
        number_of_days_per_weekday_not_received[date.weekday()] += 1

    # calculate the total number of each weekday the paper was delivered (if it is supposed to be delivered)
    # multiply this number by the cost of each day
    # add all the costs together and return the result
    return sum([
        (number_of_each_weekday[day_id] - number_of_days_per_weekday_not_received[day_id]) * cost
        if delivered else 0
        for day_id, (delivered, cost) in enumerate(cost_and_delivered_data)
    ])


def calculate_cost_of_all_papers(undelivered_strings: dict[int, list[str]], month: int, year: int) -> tuple[
    dict[int, float],
    float,
    dict[int, set[date_type]]
]:
    """calculate the cost of all papers for the full month
    - return data about the cost of each paper, the total cost, and dates when each paper was not delivered"""

    NUMBER_OF_EACH_WEEKDAY = list(get_number_of_each_weekday(month, year))
    cost_and_delivery_data = {}

    # get the IDs of papers that exist
    with connect(DATABASE_PATH) as connection:
        papers = connection.execute("SELECT paper_id FROM papers;").fetchall()

        # get the data about cost and delivery for each paper
        cost_and_delivery_data = [
            get_cost_and_delivery_data(paper_id, connection)
            for paper_id, in papers # type: ignore
        ]

    connection.close()

    # initialize a "blank" dictionary that will eventually contain any dates when a paper was not delivered
    undelivered_dates: dict[int, set[date_type]] = {
        int(paper_id): set()
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


def save_results(
    costs: dict[int, float],
    undelivered_dates: dict[int, set[date_type]],
    month: int,
    year: int,
    custom_timestamp: datetime | None = None
) -> None:
    """save the results of undelivered dates to the DB
    - save the dates any paper was not delivered
    - save the final cost of each paper"""

    timestamp = (custom_timestamp if custom_timestamp else datetime.now()).strftime(r'%d/%m/%Y %I:%M:%S %p')

    with connect(DATABASE_PATH) as connection:

        # create log entries for each paper
        log_ids = {
            paper_id: connection.execute(
                """
                INSERT INTO logs (paper_id, month, year, timestamp)
                VALUES (?, ?, ?, ?)
                RETURNING logs.log_id;
                """,
                (paper_id, month, year, timestamp)
            ).fetchone()[0]
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

        # create undelivered date entries for each paper
        for paper_id, dates in undelivered_dates.items():
            for date in dates:
                connection.execute(
                    """
                    INSERT INTO undelivered_dates_logs (log_id, date_not_delivered)
                    VALUES (?, ?);
                    """,
                    (log_ids[paper_id], date.strftime("%Y-%m-%d"))
                )

    connection.close()


def format_output(costs: dict[int, float], total: float, month: int, year: int) -> Generator[str, None, None]:
    """format the output of calculating the cost of all papers"""
    
    # output the name of the month for which the total cost was calculated
    yield f"For {date_type(year=year, month=month, day=1).strftime(r'%B %Y')},\n"

    # output the total cost of all papers
    yield f"*TOTAL*: {total:.2f}"

    # output the cost of each paper with its name
    with connect(DATABASE_PATH) as connection:
        papers = dict(connection.execute("SELECT paper_id, name FROM papers;").fetchall())

        for paper_id, cost in costs.items():
            yield f"{papers[paper_id]}: {cost:.2f}"

    connection.close()


def add_new_paper(name: str, days_delivered: list[bool], days_cost: list[float]) -> None:
    """add a new paper
    - do not allow if the paper already exists"""

    with connect(DATABASE_PATH) as connection:
        
        # check if the paper already exists
        if connection.execute(
            "SELECT EXISTS (SELECT 1 FROM papers WHERE name = ?);",
            (name,)).fetchone()[0]:
            raise npbc_exceptions.PaperAlreadyExists(f"Paper \"{name}\" already exists."
        )

        # insert the paper
        paper_id = connection.execute(
            "INSERT INTO papers (name) VALUES (?) RETURNING papers.paper_id;",
            (name,)
        ).fetchone()[0]

        # create cost and delivered entries for each day
        for day_id, (delivered, cost) in enumerate(zip(days_delivered, days_cost)):
            connection.execute(
                "INSERT INTO cost_and_delivery_data (paper_id, day_id, delivered, cost) VALUES (?, ?, ?, ?);",
                (paper_id, day_id, delivered, cost)
            )

    connection.close()


def edit_existing_paper(
    paper_id: int,
    name: str | None = None,
    days_delivered: list[bool] | None = None,
    days_cost: list[float] | None = None
) -> None:
    """edit an existing paper
    do not allow if the paper does not exist"""

    with connect(DATABASE_PATH) as connection:
        
        # check if the paper exists
        if not connection.execute(
            "SELECT EXISTS (SELECT 1 FROM papers WHERE paper_id = ?);",
            (paper_id,)).fetchone()[0]:
            raise npbc_exceptions.PaperNotExists(f"Paper with ID {paper_id} does not exist."
        )

        # update the paper name
        if name is not None:
            connection.execute(
                "UPDATE papers SET name = ? WHERE paper_id = ?;",
                (name, paper_id)
            )

        # update the costs of each day
        if days_cost is not None:
            for day_id, cost in enumerate(days_cost):
                connection.execute(
                    "UPDATE cost_and_delivery_data SET cost = ? WHERE paper_id = ? AND day_id = ?;",
                    (cost, paper_id, day_id)
                )

        # update the delivered status of each day
        if days_delivered is not None:
            for day_id, delivered in enumerate(days_delivered):
                connection.execute(
                    "UPDATE cost_and_delivery_data SET delivered = ? WHERE paper_id = ? AND day_id = ?;",
                    (delivered, paper_id, day_id)
                )

    connection.close()


def delete_existing_paper(paper_id: int) -> None:
    """delete an existing paper
    - do not allow if the paper does not exist"""

    with connect(DATABASE_PATH) as connection:
        
        # check if the paper exists
        if not connection.execute(
            "SELECT EXISTS (SELECT 1 FROM papers WHERE paper_id = ?);",
            (paper_id,)).fetchone()[0]:
            raise npbc_exceptions.PaperNotExists(f"Paper with ID {paper_id} does not exist."
        )

        # delete the paper
        connection.execute(
            "DELETE FROM papers WHERE paper_id = ?;",
            (paper_id,)
        )

        # delete the costs and delivery data for the paper
        connection.execute(
            "DELETE FROM cost_and_delivery_data WHERE paper_id = ?;",
            (paper_id,)
        )

    connection.close()


def add_undelivered_string(month: int, year: int, paper_id: int | None = None, *undelivered_strings: str) -> None:
    """record strings for date(s) paper(s) were not delivered
    - if no paper ID is specified, all papers are assumed"""

    # validate the strings
    validate_undelivered_string(*undelivered_strings)

    # if a paper ID is given
    if paper_id:

        # check that specified paper exists in the database
        with connect(DATABASE_PATH) as connection:
            if not connection.execute(
                "SELECT EXISTS (SELECT 1 FROM papers WHERE paper_id = ?);",
                (paper_id,)).fetchone()[0]:
                raise npbc_exceptions.PaperNotExists(f"Paper with ID {paper_id} does not exist."
            )
        
            # add the string(s)
            params = [
                (month, year, paper_id, string)
                for string in undelivered_strings
            ]

            connection.executemany("INSERT INTO undelivered_strings (month, year, paper_id, string) VALUES (?, ?, ?, ?);", params)

        connection.close()

    # if no paper ID is given
    else:

        # get the IDs of all papers
        with connect(DATABASE_PATH) as connection:
            paper_ids = [
                row[0]
                for row in connection.execute(
                    "SELECT paper_id FROM papers;"
                )
            ]

            # add the string(s)
            params = [
                (month, year, paper_id, string)
                for paper_id in paper_ids
                for string in undelivered_strings
            ]

            connection.executemany("INSERT INTO undelivered_strings (month, year, paper_id, string) VALUES (?, ?, ?, ?);", params)

        connection.close()


def delete_undelivered_string(
    string_id: int | None = None,
    string: str | None = None,
    paper_id: int | None = None,
    month: int | None = None,
    year: int | None = None
) -> None:
    """delete an existing undelivered string
    - do not allow if the string does not exist"""

    # initialize parameters for the WHERE clause of the SQL query
    parameters = []
    values = []

    # check each parameter and add it to the WHERE clause if it is given
    if string_id:
        parameters.append("string_id")
        values.append(string_id)

    if string:
        parameters.append("string")
        values.append(string)

    if paper_id:
        parameters.append("paper_id")
        values.append(paper_id)

    if month:
        parameters.append("month")
        values.append(month)

    if year:
        parameters.append("year")
        values.append(year)

    # if no parameters are given, raise an error
    if not parameters:
        raise npbc_exceptions.NoParameters("No parameters given.")

    with connect(DATABASE_PATH) as connection:

        # check if the string exists
        check_query = "SELECT EXISTS (SELECT 1 FROM undelivered_strings"

        conditions = ' AND '.join(
            f"{parameter} = ?"
            for parameter in parameters
        )

        if (1,) not in connection.execute(f"{check_query} WHERE {conditions});", values).fetchall():
            raise npbc_exceptions.StringNotExists("String with given parameters does not exist.")

        # if the string did exist, delete it
        delete_query = "DELETE FROM undelivered_strings"

        connection.execute(f"{delete_query} WHERE {conditions};", values)

    connection.close()


def get_papers() -> list[tuple[int, str, int, int, float]]:
    """get all papers
    - returns a list of tuples containing the following fields:
      paper_id, paper_name, day_id, paper_delivered, paper_cost"""

    raw_data = []

    query = """
        SELECT papers.paper_id, papers.name, cost_and_delivery_data.day_id, cost_and_delivery_data.delivered, cost_and_delivery_data.cost
        FROM papers
        INNER JOIN cost_and_delivery_data ON papers.paper_id = cost_and_delivery_data.paper_id
        ORDER BY papers.paper_id, cost_and_delivery_data.day_id;
    """

    with connect(DATABASE_PATH) as connection:
        raw_data = connection.execute(query).fetchall()

    connection.close()

    return raw_data


def get_undelivered_strings(
    string_id: int | None = None,
    month: int | None = None,
    year: int | None = None,
    paper_id: int | None = None,
    string: str | None = None
) -> list[tuple[int, int, int, int, str]]:
    """get undelivered strings
    - the user may specify as many as they want parameters
    - available parameters: string_id, month, year, paper_id, string
    - returns a list of tuples containing the following fields:
      string_id, paper_id, year, month, string"""

    # initialize parameters for the WHERE clause of the SQL query
    parameters = []
    values = []
    data = []

    # check each parameter and add it to the WHERE clause if it is given
    if string_id:
        parameters.append("string_id")
        values.append(string_id)

    if month:
        parameters.append("month")
        values.append(month)

    if year:
        parameters.append("year")
        values.append(year)

    if paper_id:
        parameters.append("paper_id")
        values.append(paper_id)

    if string:
        parameters.append("string")
        values.append(string)


    with connect(DATABASE_PATH) as connection:

        # generate the SQL query
        main_query = "SELECT string_id, paper_id, year, month, string FROM undelivered_strings"
        
        if not parameters:
            query = f"{main_query};"

        else:
            conditions = ' AND '.join(
                f"{parameter} = ?"
                for parameter in parameters
            )

            query = f"{main_query} WHERE {conditions};"

        data = connection.execute(query, values).fetchall()
    connection.close()

    # if no data was found, raise an error
    if not data:
        raise npbc_exceptions.StringNotExists("String with given parameters does not exist.")

    return data


def get_logged_data(
    query_paper_id: int | None = None,
    query_log_id: int | None = None,
    query_month: int | None = None,
    query_year: int | None = None,
    query_timestamp: date_type | None = None
) -> Generator[tuple[int, int, int, int, str, str | float], None, None]:
    """get logged data
    - the user may specify as parameters many as they want
    - available parameters: paper_id, log_id, month, year, timestamp
    - yields: tuples containing the following fields:
      log_id, paper_id, month, year, timestamp, date | cost."""

    # initialize parameters for the WHERE clause of the SQL query
    parameters = []
    values = ()

    # check each parameter and add it to the WHERE clause if it is given
    if query_paper_id:
        parameters.append("paper_id")
        values += (query_paper_id,)

    if query_log_id:
        parameters.append("log_id")
        values += (query_log_id,)

    if query_month:
        parameters.append("month")
        values += (query_month,)

    if query_year:
        parameters.append("year")
        values += (query_year,)

    if query_timestamp:
        parameters.append("timestamp")
        values += (query_timestamp.strftime(r'%d/%m/%Y %I:%M:%S %p'),)

    # generate the SQL query
    logs_base_query = """
        SELECT log_id, paper_id, timestamp, month, year
        FROM logs
        ORDER BY log_id, paper_id   
    """

    if parameters:
        conditions = ' AND '.join(
            f"{parameter} = ?"
            for parameter in parameters
        )

        logs_query = f"{logs_base_query} WHERE {conditions};"

    else:
        logs_query = f"{logs_base_query};"

    dates_query = "SELECT log_id, date_not_delivered FROM undelivered_dates_logs;"
    costs_query = "SELECT log_id, cost FROM cost_logs;"

    with connect(DATABASE_PATH) as connection:
        logs = {
            log_id: [paper_id, month, year, timestamp]
            for log_id, paper_id, timestamp, month, year in connection.execute(logs_query, values).fetchall()
        }

        dates = connection.execute(dates_query).fetchall()
        costs = connection.execute(costs_query).fetchall()

        for log_id, date in dates:
            yield tuple(logs[log_id] + [date])

        for log_id, cost in costs:
            yield tuple(logs[log_id] + [float(cost)])
        
    connection.close()



def get_previous_month() -> date_type:
    """get the previous month, by looking at 1 day before the first day of the current month (duh)"""

    return (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1)


def validate_month_and_year(month: int | None = None, year: int | None = None) -> None:
    """validate month and year
    - month must be an integer between 1 and 12 inclusive
    - year must be an integer greater than 0"""
    
    if isinstance(month, int) and not (1 <= month <= 12):
        raise npbc_exceptions.InvalidMonthYear("Month must be between 1 and 12.")

    if isinstance(year, int) and (year <= 0):
        raise npbc_exceptions.InvalidMonthYear("Year must be greater than 0.")

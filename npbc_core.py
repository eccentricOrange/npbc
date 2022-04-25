from sqlite3 import connect
from calendar import day_name as weekday_names_iterable
from calendar import monthrange, monthcalendar
from datetime import date as date_type, datetime, timedelta
from pathlib import Path
from re import compile as compile_regex

DATABASE_DIR = Path().home() / '.npbc'
# DATABASE_DIR = Path('data')

DATABASE_PATH = DATABASE_DIR / 'npbc.db'

SCHEMA_PATH = Path(__file__).parent / 'schema.sql'
# SCHEMA_PATH = DATABASE_DIR / 'schema.sql'

WEEKDAY_NAMES = list(weekday_names_iterable)

VALIDATE_REGEX = {
    # match for a list of comma separated values. each value must be/contain digits, or letters, or hyphens. spaces are allowed between values and commas. any number of values are allowed, but at least one must be present.
    'CSVs': compile_regex(r'^[-\w]+( *, *[-\w]+)*( *,)?$'),

    # match for a single number. must be one or two digits
    'number': compile_regex(r'^[\d]{1,2}?$'),

    # match for a range of numbers. each number must be one or two digits. numbers are separated by a hyphen. spaces are allowed between numbers and the hyphen.
    'range': compile_regex(r'^\d{1,2} *- *\d{1,2}$'),

    # match for weekday name. day must appear as "daynames" (example: "mondays"). all lowercase.
    'days': compile_regex(f"^{'|'.join([day_name.lower() + 's' for day_name in WEEKDAY_NAMES])}$"),

    # match for nth weekday name. day must appear as "n-dayname" (example: "1-monday"). all lowercase. must be one digit.
    'n-day': compile_regex(f"^\\d *- *({'|'.join([day_name.lower() for day_name in WEEKDAY_NAMES])})$"),

    # match for real values, delimited by semicolons. each value must be either an integer or a float with a decimal point. spaces are allowed between values and semicolons, and up to 7 (but at least 1) values are allowed.
    'costs': compile_regex(r'^\d+(\.\d+)?( ?; ?\d+(\.\d+)?){0,6} ?;?$'),

    # match for seven values, each of which must be a 'Y' or an 'N'. there are no delimiters.
    'delivery': compile_regex(r'^[YN]{7}$')
}

SPLIT_REGEX = {
    # split on hyphens. spaces are allowed between hyphens and values.
    'hyphen': compile_regex(r' *- *'),
    
    # split on semicolons. spaces are allowed between hyphens and values.
    'semicolon': compile_regex(r' *; *'),

    # split on commas. spaces are allowed between commas and values.
    'comma': compile_regex(r' *, *')
}


def setup_and_connect_DB() -> None:
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_PATH.touch(exist_ok=True)

    with connect(DATABASE_PATH) as connection:
        connection.executescript(SCHEMA_PATH.read_text())
        connection.commit()


def generate_sql_query(table_name: str, conditions: dict[str, int | str] | None = None, columns: list[str] | None = None) -> str:
    sql_query = f"SELECT"
    
    if columns:
        sql_query += f" {', '.join(columns)}"
    
    else:
        sql_query += f" *"
    
    sql_query += f" FROM {table_name}"

    if conditions:
        conditions_segment = ' AND '.join([
            f"{parameter_name} = {parameter_value}"
            for parameter_name, parameter_value in conditions.items()
        ])
        
        sql_query += f" WHERE {conditions_segment}"

    return f"{sql_query};"


def query_database(query: str) -> list[tuple]:
    with connect(DATABASE_PATH) as connection:
        return connection.execute(query).fetchall()
    
    return []


def get_number_of_days_per_week(month: int, year: int) -> list[int]:
    main_calendar = monthcalendar(year, month)
    number_of_weeks = len(main_calendar)
    number_of_weekdays = []

    for i in range(len(WEEKDAY_NAMES)):
        number_of_weekday = number_of_weeks

        if main_calendar[0][i] == 0:
            number_of_weekday -= 1
        
        if main_calendar[-1][i] == 0:
            number_of_weekday -= 1

        number_of_weekdays.append(number_of_weekday)

    return number_of_weekdays


def validate_undelivered_string(string: str) -> bool:
    if VALIDATE_REGEX['CSVs'].match(string):
        
        for section in SPLIT_REGEX['comma'].split(string.rstrip(',')):
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

    for section in SPLIT_REGEX['comma'].split(string.rstrip(',')):
        if VALIDATE_REGEX['number'].match(section):
            date = int(section)

            if date > 0 and date <= monthrange(year, month)[1]:
                dates.add(date_type(year, month, date))

        elif VALIDATE_REGEX['range'].match(section):
            start, end = [int(date) for date in SPLIT_REGEX['hyphen'].split(section.rstrip('-'))]

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
            n, weekday = SPLIT_REGEX['hyphen'].split(section.rstrip('-'))

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
            print("This data has not been counted.")

    return dates


def get_cost_and_delivery_data(paper_id: int) -> tuple[dict[int, float], dict[int, bool]]:
    cost_query = generate_sql_query(
        'papers_days_cost',
        columns=['day_id', 'cost'],
        conditions={'paper_id': paper_id}
    )

    delivery_query = generate_sql_query(
        'papers_days_delivered',
        columns=['day_id', 'delivered'],
        conditions={'paper_id': paper_id}
    )

    with connect(DATABASE_PATH) as connection:
        cost_tuple = connection.execute(cost_query).fetchall()
        delivery_tuple = connection.execute(delivery_query).fetchall()

    cost_dict = {
        day_id: cost
        for day_id, cost in cost_tuple # type: ignore
    }

    delivery_dict = {
        day_id: delivery
        for day_id, delivery in delivery_tuple # type: ignore
    }

    return cost_dict, delivery_dict


def calculate_cost_of_one_paper(number_of_days_per_week: list[int], undelivered_dates: set[date_type], cost_and_delivered_data: tuple[dict[int, float], dict[int, bool]]) -> float:
    number_of_days_per_week_not_received = [0] * len(number_of_days_per_week)
    cost_data, delivered_data = cost_and_delivered_data

    for date in undelivered_dates:
        number_of_days_per_week_not_received[date.weekday()] += 1
    
    number_of_days_delivered = [
        number_of_days_per_week[day_id] - number_of_days_per_week_not_received[day_id] if delivered else 0
        for day_id, delivered in delivered_data.items()
    ]

    return sum(
        cost * number_of_days_delivered[day_id]
        for day_id, cost in cost_data.items()
    )


def calculate_cost_of_all_papers(undelivered_strings: dict[int, str], month: int, year: int) -> tuple[dict[int, float], float, dict[int, set[date_type]]]:
    NUMBER_OF_DAYS_PER_WEEK = get_number_of_days_per_week(month, year)

    with connect(DATABASE_PATH) as connection:
        papers = connection.execute(
            generate_sql_query(
                'papers',
                columns=['paper_id']
            )
        ).fetchall()

    cost_and_delivery_data = [
        get_cost_and_delivery_data(paper_id)
        for paper_id, in papers # type: ignore
    ]

    undelivered_dates: dict[int, set[date_type]] = {
        paper_id: {}
        for paper_id, in papers # type: ignore
    }

    for paper_id, undelivered_string in undelivered_strings.items(): # type: ignore
        undelivered_dates[paper_id] = parse_undelivered_string(undelivered_string, month, year)


    costs = {
        paper_id: calculate_cost_of_one_paper(
            NUMBER_OF_DAYS_PER_WEEK,
            undelivered_dates[paper_id],
            cost_and_delivery_data[index]
        )
        for index, (paper_id,) in enumerate(papers) # type: ignore
    }

    total: float = sum(costs.values())

    return costs, total, undelivered_dates


def save_results(undelivered_dates: dict[int, set[date_type]], month: int, year: int) -> None:
    TIMESTAMP = datetime.now().strftime(r'%d/%m/%Y %I:%M:%S %p')

    with connect(DATABASE_PATH) as connection:
        for paper_id, undelivered_date_instances in undelivered_dates.items():
            connection.execute(
                "INSERT INTO undelivered_dates (timestamp, month, year, paper_id, dates) VALUES (?, ?, ?, ?, ?);",
                (
                    TIMESTAMP,
                    month,
                    year,
                    paper_id,
                    ','.join([
                        undelivered_date_instance.strftime(r'%d')
                        for undelivered_date_instance in undelivered_date_instances
                    ])
                )
            )


def format_output(costs: dict[int, float], total: float, month: int, year: int) -> str:
    papers = {
        paper_id: name
        for paper_id, name in query_database(
            generate_sql_query('papers')
        )
    }


    format_string = f"For {date_type(year=year, month=month, day=1).strftime(r'%B %Y')}\n\n"
    format_string += f"**TOTAL**: {total}\n"

    format_string += '\n'.join([
        f"{papers[paper_id]}: {cost}"  # type: ignore
        for paper_id, cost in costs.items()
    ])

    return f"{format_string}\n"


def add_new_paper(name: str, days_delivered: list[bool], days_cost: list[float]) -> tuple[bool, str]:
    with connect(DATABASE_PATH) as connection:
        q = generate_sql_query('papers', columns=['name'], conditions={'name': f"\"{name}\""})
        paper = connection.execute(
            q
        ).fetchall()

        if paper:
            return False, "Paper already exists. Please try editing the paper instead."
        
        connection.execute(
            "INSERT INTO papers (name) VALUES (?);",
            (name, )
        )

        paper_id = connection.execute(
            "SELECT paper_id FROM papers WHERE name = ?;",
            (name, )
        ).fetchone()[0]

        for day_id, (cost, delivered) in enumerate(zip(days_cost, days_delivered)):
            connection.execute(
                "INSERT INTO papers_days_cost (paper_id, day_id, cost) VALUES (?, ?, ?);",
                (paper_id, day_id, cost)
            )
            connection.execute(
                "INSERT INTO papers_days_delivered (paper_id, day_id, delivered) VALUES (?, ?, ?);",
                (paper_id, day_id, delivered)
            )
        
        connection.commit()

        return True, f"Paper {name} added."

    return False, "Something went wrong."


def edit_existing_paper(paper_id: int, name: str | None = None, days_delivered: list[bool] | None = None, days_cost: list[float] | None = None) -> tuple[bool, str]:
    with connect(DATABASE_PATH) as connection:
        paper = connection.execute(
            generate_sql_query('papers', columns=['paper_id'], conditions={'paper_id': paper_id})
        ).fetchone()

        if not paper:
            return False, f"Paper {paper_id} does not exist. Please try adding it instead."

        if name is not None:
            connection.execute(
                "UPDATE papers SET name = ? WHERE paper_id = ?;",
                (name, paper_id)
            )
        
        if days_delivered is not None:
            for day_id, delivered in enumerate(days_delivered):
                connection.execute(
                    "UPDATE papers_days_delivered SET delivered = ? WHERE paper_id = ? AND day_id = ?;",
                    (delivered, paper_id, day_id)
                )

        if days_cost is not None:
            for day_id, cost in enumerate(days_cost):
                connection.execute(
                    "UPDATE papers_days_cost SET cost = ? WHERE paper_id = ? AND day_id = ?;",
                    (cost, paper_id, day_id)
                )

        connection.commit()

        return True, f"Paper {paper_id} edited."

    return False, "Something went wrong."


def delete_existing_paper(paper_id: int) -> tuple[bool, str]:
    with connect(DATABASE_PATH) as connection:
        paper = connection.execute(
            generate_sql_query('papers', columns=['paper_id'], conditions={'paper_id': paper_id})
        ).fetchone()

        if not paper:
            return False, f"Paper {paper_id} does not exist. Please try adding it instead."

        connection.execute(
            "DELETE FROM papers WHERE paper_id = ?;",
            (paper_id, )
        )

        connection.execute(
            "DELETE FROM papers_days_cost WHERE paper_id = ?;",
            (paper_id, )
        )

        connection.execute(
            "DELETE FROM papers_days_delivered WHERE paper_id = ?;",
            (paper_id, )
        )

        connection.commit()

        return True, f"Paper {paper_id} deleted."

    return False, "Something went wrong."


def add_undelivered_string(paper_id: int, undelivered_string: str, month: int, year: int) -> tuple[bool, str]:
    if validate_undelivered_string(undelivered_string):
        with connect(DATABASE_PATH) as connection:
            existing_string = connection.execute(
                generate_sql_query(
                    'undelivered_strings',
                    columns=['string'],
                    conditions={
                        'paper_id': paper_id,
                        'month': month,
                        'year': year
                    }
                )
            ).fetchone()

            if existing_string:
                new_string = f"{existing_string[0]},{undelivered_string}"

                connection.execute(
                    "UPDATE undelivered_strings SET string = ? WHERE paper_id = ? AND month = ? AND year = ?;",
                    (new_string, paper_id, month, year)
                )

            else:
                connection.execute(
                    "INSERT INTO undelivered_strings (string, paper_id, month, year) VALUES (?, ?, ?, ?);",
                    (undelivered_string, paper_id, month, year)
                )

            connection.commit()

        return True, f"Undelivered string added."

    return False, f"Invalid undelivered string."


def delete_undelivered_string(paper_id: int, month: int, year: int) -> tuple[bool, str]:
    with connect(DATABASE_PATH) as connection:
        existing_string = connection.execute(
            generate_sql_query(
                'undelivered_strings',
                columns=['string'],
                conditions={
                    'paper_id': paper_id,
                    'month': month,
                    'year': year
                }
            )
        ).fetchone()

        if existing_string:
            connection.execute(
                "DELETE FROM undelivered_strings WHERE paper_id = ? AND month = ? AND year = ?;",
                (paper_id, month, year)
            )

            connection.commit()

            return True, f"Undelivered string deleted."

        return False, f"Undelivered string does not exist."

    return False, "Something went wrong."


def get_previous_month() -> date_type:
    return (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1)


def extract_days_and_costs(days_delivered: str | None, prices: str | None) -> tuple[list[bool], list[float]]:
    days = []
    costs = []

    if days_delivered is not None:
        days = [
            bool(int(day == 'Y')) for day in str(days_delivered).upper()
        ]

    if prices is not None:

        costs = []
        encoded_prices = [float(price) for price in SPLIT_REGEX['semicolon'].split(prices.rstrip(';')) if float(price) > 0]

        day_count = -1
        for day in days:
            if day:
                day_count += 1
                cost = encoded_prices[day_count]

            else:
                cost = 0

            costs.append(cost)

    return days, costs
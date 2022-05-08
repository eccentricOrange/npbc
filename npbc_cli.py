"""
wraps a CLI around the core functionality (argparse)
- inherits functionality from `npbc_core.py`
- inherits regex from `npbc_regex.py`, used for validation
- inherits exceptions from `npbc_exceptions.py`, used for error handling
- performs some additional validation
- formats data retrieved from the core for the user
"""


import sqlite3
from argparse import ArgumentParser
from argparse import Namespace as ArgNamespace
from datetime import datetime
from typing import Generator

from colorama import Fore, Style

import npbc_core
import npbc_exceptions
from npbc_regex import DELIVERY_MATCH_REGEX


def define_and_read_args() -> ArgNamespace:
    """configure parsers
    - define the main parser for the application executable
    - define subparsers (one for each functionality)
    - parse the arguments"""

    # main parser for all commands
    main_parser = ArgumentParser(
        prog="npbc",
        description="Calculates your monthly newspaper bill."
    )
    functions = main_parser.add_subparsers(required=True)


    # calculate subparser
    calculate_parser = functions.add_parser(
        'calculate',
        help="Calculate the bill for one month. Previous month will be used if month or year flags are not set."
    )

    calculate_parser.set_defaults(func=calculate)
    calculate_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
    calculate_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be greater than 0.")
    calculate_parser.add_argument('-l', '--nolog', help="Don't log the result of the calculation.", action='store_true')


    # add undelivered string subparser
    addudl_parser = functions.add_parser(
        'addudl',
        help="Store a date when paper(s) were not delivered. Current month will be used if month or year flags are not set. Either paper ID must be provided, or the all flag must be set."
    )

    addudl_parser.set_defaults(func=addudl)
    addudl_parser.add_argument('-m', '--month', type=int, help="Month to register undelivered incident(s) for. Must be between 1 and 12.")
    addudl_parser.add_argument('-y', '--year', type=int, help="Year to register undelivered incident(s) for. Must be greater than 0.")
    addudl_parser.add_argument('-p', '--paperid', type=str, help="ID of paper to register undelivered incident(s) for.")
    addudl_parser.add_argument('-a', '--all', help="Register undelivered incidents for all papers.", action='store_true')
    addudl_parser.add_argument('-s', '--strings', type=str, help="Dates when you did not receive any papers.", required=True, nargs='+')


    # delete undelivered string subparser
    deludl_parser = functions.add_parser(
        'deludl',
        help="Delete a stored date when paper(s) were not delivered. If no parameters are provided, the function will not default; it will throw an error instead."
    )

    deludl_parser.set_defaults(func=deludl)
    deludl_parser.add_argument('-p', '--paperid', type=str, help="ID of paper to unregister undelivered incident(s) for.")
    deludl_parser.add_argument('-i', '--stringid', type=str, help="String ID of paper to unregister undelivered incident(s) for.")
    deludl_parser.add_argument('-m', '--month', type=int, help="Month to unregister undelivered incident(s) for. Must be between 1 and 12.")
    deludl_parser.add_argument('-y', '--year', type=int, help="Year to unregister undelivered incident(s) for. Must be greater than 0.")
    deludl_parser.add_argument('-s', '--string', type=str, help="Dates when you did not receive any papers.")


    # get undelivered string subparser
    getudl_parser = functions.add_parser(
        'getudl',
        help="Get a list of all stored date strings when paper(s) were not delivered. All parameters are optional and act as filters."
    )

    getudl_parser.set_defaults(func=getudl)
    getudl_parser.add_argument('-p', '--paperid', type=str, help="ID for paper.")
    getudl_parser.add_argument('-i', '--stringid', type=str, help="String ID of paper to unregister undelivered incident(s) for.")
    getudl_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getudl_parser.add_argument('-y', '--year', type=int, help="Year. Must be greater than 0.")
    getudl_parser.add_argument('-s', '--string', type=str, help="Dates when you did not receive any papers.")


    # edit paper subparser
    editpaper_parser = functions.add_parser(
        'editpaper',
        help="Edit a newspaper's name, days delivered, and/or price."
    )

    editpaper_parser.set_defaults(func=editpaper)
    editpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be edited.")
    editpaper_parser.add_argument('-d', '--delivered', type=str, help="Number of days the paper to be edited is delivered. All seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.")
    editpaper_parser.add_argument('-c', '--costs', type=str, help="Daywise prices of paper to be edited. 0s are ignored.", nargs='*')
    editpaper_parser.add_argument('-p', '--paperid', type=str, help="ID for paper to be edited.", required=True)


    # add paper subparser
    addpaper_parser = functions.add_parser(
        'addpaper',
        help="Add a new newspaper to the list of newspapers."
    )

    addpaper_parser.set_defaults(func=addpaper)
    addpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be added.", required=True)
    addpaper_parser.add_argument('-d', '--delivered', type=str, help="Number of days the paper to be added is delivered. All seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.", required=True)
    addpaper_parser.add_argument('-c', '--costs', type=str, help="Daywise prices of paper to be added. 0s are ignored.", required=True, nargs='+')


    # delete paper subparser
    delpaper_parser = functions.add_parser(
        'delpaper',
        help="Delete a newspaper from the list of newspapers."
    )

    delpaper_parser.set_defaults(func=delpaper)
    delpaper_parser.add_argument('-p', '--paperid', type=str, help="ID for paper to be deleted.", required=True)

    # get paper subparser
    getpapers_parser = functions.add_parser(
        'getpapers',
        help="Get all newspapers."
    )

    getpapers_parser.set_defaults(func=getpapers)
    getpapers_parser.add_argument('-n', '--names', help="Get the names of the newspapers.", action='store_true')
    getpapers_parser.add_argument('-d', '--delivered', help="Get the days the newspapers are delivered. All seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't.", action='store_true')
    getpapers_parser.add_argument('-c', '--cost', help="Get the daywise prices of the newspapers. Values must be separated by semicolons.", action='store_true')

    # get undelivered logs subparser
    getlogs_parser = functions.add_parser(
        'getlogs',
        help="Get the log of all undelivered dates."
    )

    getlogs_parser.set_defaults(func=getlogs)
    getlogs_parser.add_argument('-i', '--logid', type=int, help="ID for log to be retrieved.")
    getlogs_parser.add_argument('-p', '--paperid', type=str, help="ID for paper.")
    getlogs_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getlogs_parser.add_argument('-y', '--year', type=int, help="Year. Must be greater than 0.")
    getlogs_parser.add_argument('-t' , '--timestamp', type=str, help="Timestamp. Must be in the format dd/mm/yyyy hh:mm:ss AM/PM.")


    # update application subparser
    update_parser = functions.add_parser(
        'update',
        help="Update the application."
    )

    update_parser.set_defaults(func=update)


    return main_parser.parse_args()


def status_print(status: bool, message: str) -> None:
    """print out a coloured status message using Colorama"""

    if status:
        print(f"{Fore.GREEN}", end="")
    else:
        print(f"{Fore.RED}", end="")

    print(f"{Style.BRIGHT}{message}{Style.RESET_ALL}\n")


def calculate(args: ArgNamespace) -> None:
    """calculate the cost for a given month and year
    - default to the previous month if no month and no year is given
    - default to the current month if no month is given and year is given
    - default to the current year if no year is given and month is given"""

    ## deal with month and year

    # if either of them are given
    if args.month or args.year:

        # validate them
        try:
            npbc_core.validate_month_and_year(args.month, args.year)
        
        except npbc_exceptions.InvalidMonthYear:
            status_print(False, "Invalid month and/or year.")
            return

        # for each, if it is not given, set it to the current month and/or year
        month = args.month or datetime.now().month
        year = args.year or datetime.now().year

    # if neither are given
    else:

        # set them to the previous month and year
        previous_month = npbc_core.get_previous_month()
        month = previous_month.month
        year = previous_month.year

    # prepare a dictionary for undelivered strings
    undelivered_strings = {
        int(paper_id): []
        for paper_id, _, _, _, _ in npbc_core.get_papers()
    }

    # get the undelivered strings from the database
    try:
        raw_undelivered_strings = npbc_core.get_undelivered_strings(month=month, year=year)

        # add them to the dictionary
        for _, paper_id, _, _, string in raw_undelivered_strings:
            undelivered_strings[paper_id].append(string)

    # ignore if none exist
    except npbc_exceptions.StringNotExists:
        pass

    # calculate the cost for each paper
    costs, total, undelivered_dates = npbc_core.calculate_cost_of_all_papers(
        undelivered_strings,
        month,
        year
    )

    # format the results
    formatted = '\n'.join(npbc_core.format_output(costs, total, month, year))

    # unless the user specifies so, log the results to the database
    if not args.nolog:
        npbc_core.save_results(costs, undelivered_dates, month, year)

        formatted += '\n\nLog saved to file.'

    # print the results
    status_print(True, "Success!")
    print(f"SUMMARY:\n\n{formatted}")


def addudl(args: ArgNamespace) -> None:
    """add undelivered strings to the database
    - default to the current month if no month and/or no year is given"""

    try:
        npbc_core.validate_month_and_year(args.month, args.year)

    except npbc_exceptions.InvalidMonthYear:
        status_print(False, "Invalid month and/or year.")
        return

    month = args.month or datetime.now().month
    year = args.year or datetime.now().year

    if args.paperid or args.all:

        try:
            print(f"{month=} {year=} {args.paperid=} {args.strings=}")
            npbc_core.add_undelivered_string(month, year, args.paperid, *args.strings)

        except npbc_exceptions.PaperNotExists:
            status_print(False, f"Paper with ID {args.paperid} does not exist.")
            return

        except npbc_exceptions.InvalidUndeliveredString:
            status_print(False, "Invalid undelivered string(s).")
            return

    else:
        status_print(False, "No paper(s) specified.")
        return

    status_print(True, "Success!")


def deludl(args: ArgNamespace) -> None:
    """delete undelivered strings from the database"""

    try:
        npbc_core.validate_month_and_year(args.month, args.year)

    except npbc_exceptions.InvalidMonthYear:
        status_print(False, "Invalid month and/or year.")
        return

    try:
        npbc_core.delete_undelivered_string(
            month=args.month,
            year=args.year,
            paper_id=args.paperid,
            string=args.string,
            string_id=args.stringid
        )

    except npbc_exceptions.NoParameters:
        status_print(False, "No parameters specified.")
        return

    except npbc_exceptions.StringNotExists:
        status_print(False, "String does not exist.")
        return
        
    status_print(True, "Success!")


def getudl(args: ArgNamespace) -> None:
    """get undelivered strings from the database
    filter by whichever parameter the user provides. they as many as they want.
    available parameters: month, year, paper_id, string_id, string"""

    try:
        npbc_core.validate_month_and_year(args.month, args.year)

    except npbc_exceptions.InvalidMonthYear:
        status_print(False, "Invalid month and/or year.")
        return

    try:
        undelivered_strings = npbc_core.get_undelivered_strings(
            month=args.month,
            year=args.year,
            paper_id=args.paperid,
            string_id=args.stringid,
            string=args.string
        )

    except npbc_exceptions.NoParameters:
        status_print(False, "No parameters specified.")
        return

    except npbc_exceptions.StringNotExists:
        status_print(False, "No strings found for the given parameters.")
        return

    # format the results
    status_print(True, "Success!")

    print(f"{Fore.YELLOW}string_id{Style.RESET_ALL} | {Fore.YELLOW}paper_id{Style.RESET_ALL} | {Fore.YELLOW}year{Style.RESET_ALL} | {Fore.YELLOW}month{Style.RESET_ALL} | {Fore.YELLOW}string{Style.RESET_ALL}")

    for items in undelivered_strings:
        print('|'.join([str(item) for item in items]))


def extract_delivery_from_user_input(input_delivery: str) -> list[bool]:
    """convert the /[YN]{7}/ user input to a Boolean list"""

    if not DELIVERY_MATCH_REGEX.match(input_delivery):
        raise npbc_exceptions.InvalidInput("Invalid delivery days.")

    return [
        day == 'Y'
        for day in input_delivery
    ]


def extract_costs_from_user_input(paper_id: int | None, delivery_data: list[bool] | None, *input_costs: float) -> Generator[float, None, None]:
    """convert the user input to a float list"""

    suspected_data = [
        cost
        for cost in input_costs
        if cost != 0
    ]
    suspected_data.reverse()

    if delivery_data:
        if (len(suspected_data) != delivery_data.count(True)):
            raise npbc_exceptions.InvalidInput("Number of costs don't match number of days delivered.")

        for day in delivery_data:
            yield suspected_data.pop() if day else 0

    elif paper_id:
        raw_data = [paper for paper in npbc_core.get_papers() if paper[0] == int(paper_id)]

        delivered = [
            bool(delivered)
            for _, _, day_id, delivered, _ in raw_data
        ]

        if len(suspected_data) != delivered.count(True):
            raise npbc_exceptions.InvalidInput("Number of costs don't match number of days delivered.")

        for day in delivered:
            yield suspected_data.pop() if day else 0

    else:
        raise npbc_exceptions.InvalidInput("Something went wrong.")


def editpaper(args: ArgNamespace) -> None:
    """edit a paper's information"""
    try:
        delivery_data = extract_delivery_from_user_input(args.delivered) if args.delivered else None

        npbc_core.edit_existing_paper(
            paper_id=args.paperid,
            name=args.name,
            days_delivered=delivery_data,
            days_cost=list(extract_costs_from_user_input(args.paperid, delivery_data, *args.costs)) if args.costs else None
        )

    except npbc_exceptions.PaperNotExists:
        status_print(False, "Paper does not exist.")
        return

    except npbc_exceptions.InvalidInput as e:
        status_print(False, f"Invalid input: {e}")
        return

    status_print(True, "Success!")


def addpaper(args: ArgNamespace) -> None:
    """add a new paper to the database"""

    try:
        delivery_data = extract_delivery_from_user_input(args.delivered)

        npbc_core.add_new_paper(
            name=args.name,
            days_delivered=delivery_data,
            days_cost=list(extract_costs_from_user_input(None, delivery_data, *args.costs))
        )

    except npbc_exceptions.InvalidInput as e:
        status_print(False, f"Invalid input: {e}")
        return

    except npbc_exceptions.PaperAlreadyExists:
        status_print(False, "Paper already exists.")
        return

    status_print(True, "Success!")


def delpaper(args: ArgNamespace) -> None:
    """delete a paper from the database"""

    try:
        npbc_core.delete_existing_paper(args.paperid)

    except npbc_exceptions.PaperNotExists:
        status_print(False, "Paper does not exist.")
        return

    status_print(True, "Success!")


def getpapers(args: ArgNamespace) -> None:
    """get a list of all papers in the database
    - filter by whichever parameter the user provides. they may use as many as they want (but keys are always printed)
    - available parameters: name, days, costs
    - the output is provided as a formatted table, printed to the standard output"""

    try:
        raw_data = npbc_core.get_papers()

    except sqlite3.DatabaseError as e:
        status_print(False, f"Database error: {e}\nPlease report this to the developer.")
        return

    headers = ['paper_id']
    ids = []

    ids = list(set(paper[0] for paper in raw_data))
    ids.sort()
    
    delivery = [None for _ in ids]
    costs = [None for _ in ids]
    names = [None for _ in ids]

    if args.names:
        headers.append('name')

        names = list(set(
            (paper_id, name)
            for paper_id, name, _, _, _ in raw_data
        ))

        names.sort(key=lambda item: item[0])
        names = [name for _, name in names]

    if args.delivered or args.cost:
        days = {
            paper_id: {}
            for paper_id in ids
        }

        for paper_id, _, day_id, _, _ in raw_data:
            days[paper_id][day_id] = {}
        
        for paper_id, _, day_id, day_delivery, day_cost in raw_data:
            days[paper_id][day_id]['delivery'] = day_delivery
            days[paper_id][day_id]['cost'] = day_cost

        if args.delivered:
            headers.append('days')

            delivery = [
                ''.join([
                    'Y' if days[paper_id][day_id]['delivery'] else 'N'
                    for day_id, _ in enumerate(npbc_core.WEEKDAY_NAMES)
                ])
                for paper_id in ids
            ]

        if args.cost:
            headers.append('costs')

            costs = [
                ';'.join([
                    str(days[paper_id][day_id]['cost'])
                    for day_id, _ in enumerate(npbc_core.WEEKDAY_NAMES)
                    if days[paper_id][day_id]['cost'] != 0
                ])
                for paper_id in ids
            ]

    print(' | '.join([
        f"{Fore.YELLOW}{header}{Style.RESET_ALL}"
        for header in headers
    ]))

    # print the data
    for paper_id, name, delivered, cost in zip(ids, names, delivery, costs):
        print(paper_id, end='')

        if args.names:
            print(f", {name}", end='')

        if args.delivered:
            print(f", {delivered}", end='')

        if args.cost:
            print(f", {cost}", end='')

        print()


def getlogs(args: ArgNamespace) -> None:
    """get a list of all logs in the database
    - filter by whichever parameter the user provides. they may use as many as they want (but log IDs are always printed)
    - available parameters: log_id, paper_id, month, year, timestamp
    - will return both date logs and cost logs"""

    try:
        data = npbc_core.get_logged_data(
            log_id = args.logid,
            paper_id=args.paperid,
            month=args.month,
            year=args.year,
            timestamp= datetime.strptime(args.timestamp, r'%d/%m/%Y %I:%M:%S %p') if args.timestamp else None
        )

    except sqlite3.DatabaseError as e:
        status_print(False, f"Database error. Please report this to the developer.\n{e}")
        return

    except ValueError:
        status_print(False, "Invalid date format. Please use the following format: dd/mm/yyyy hh:mm:ss AM/PM")
        return

    print(' | '.join(
        f"{Fore.YELLOW}{header}{Style.RESET_ALL}"
        for header in ['log_id', 'paper_id', 'month', 'year', 'timestamp', 'date', 'cost']
    ))

    # print the data
    for row in data:
        print(', '.join(str(item) for item in row))


def update(args: ArgNamespace) -> None:
    """update the application
    - under normal operation, this function should never run
    - if the update CLI argument is provided, this script will never run and the updater will be run instead"""

    status_print(False, "Update failed.")


def main() -> None:
    """main function
    - initialize the database
    - parses the command line arguments
    - calls the appropriate function based on the arguments"""

    npbc_core.setup_and_connect_DB()
    parsed = define_and_read_args()
    parsed.func(parsed)


if __name__ == "__main__":
    main()

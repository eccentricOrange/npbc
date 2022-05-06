from argparse import ArgumentParser, Namespace as ArgNamespace
from datetime import datetime
from colorama import Fore, Style
import npbc_core
import npbc_exceptions
from npbc_regex import DAYS_MATCH_REGEX


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
    calculate_parser.add_argument('-c', '--nocopy', help="Don't copy the result of the calculation to the clipboard.", action='store_true')
    calculate_parser.add_argument('-l', '--nolog', help="Don't log the result of the calculation.", action='store_true')


    # add undelivered string subparser
    addudl_parser = functions.add_parser(
        'addudl',
        help="Store a date when paper(s) were not delivered. Current month will be used if month or year flags are not set. Either paper ID must be provided, or the all flag must be set."
    )

    addudl_parser.set_defaults(func=addudl)
    addudl_parser.add_argument('-m', '--month', type=int, help="Month to register undelivered incident(s) for. Must be between 1 and 12.")
    addudl_parser.add_argument('-y', '--year', type=int, help="Year to register undelivered incident(s) for. Must be greater than 0.")
    addudl_parser.add_argument('-i', '--id', type=str, help="ID of paper to register undelivered incident(s) for.")
    addudl_parser.add_argument('-a', '--all', help="Register undelivered incidents for all papers.", action='store_true')
    addudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.", required=True, nargs='+')


    # delete undelivered string subparser
    deludl_parser = functions.add_parser(
        'deludl',
        help="Delete a stored date when paper(s) were not delivered. If no parameters are provided, the function will not default; it will throw an error instead."
    )

    deludl_parser.set_defaults(func=deludl)
    deludl_parser.add_argument('-i', '--id', type=str, help="ID of paper to unregister undelivered incident(s) for.")
    deludl_parser.add_argument('-s', '--strid', type=str, help="String ID of paper to unregister undelivered incident(s) for.")
    deludl_parser.add_argument('-m', '--month', type=int, help="Month to unregister undelivered incident(s) for. Must be between 1 and 12.")
    deludl_parser.add_argument('-y', '--year', type=int, help="Year to unregister undelivered incident(s) for. Must be greater than 0.")
    deludl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.")


    # get undelivered string subparser
    getudl_parser = functions.add_parser(
        'getudl',
        help="Get a list of all stored date strings when paper(s) were not delivered. All parameters are optional and act as filters."
    )

    getudl_parser.set_defaults(func=getudl)
    getudl_parser.add_argument('-i', '--id', type=str, help="ID for paper.")
    deludl_parser.add_argument('-s', '--strid', type=str, help="String ID of paper to unregister undelivered incident(s) for.")
    getudl_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getudl_parser.add_argument('-y', '--year', type=int, help="Year. Must be greater than 0.")
    getudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.")


    # edit paper subparser
    editpaper_parser = functions.add_parser(
        'editpaper',
        help="Edit a newspaper's name, days delivered, and/or price."
    )

    editpaper_parser.set_defaults(func=editpaper)
    editpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be edited.")
    editpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited is delivered. All seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.")
    editpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited. 0s are ignored.", nargs='*')
    editpaper_parser.add_argument('-i', '--id', type=str, help="ID for paper to be edited.", required=True)


    # add paper subparser
    addpaper_parser = functions.add_parser(
        'addpaper',
        help="Add a new newspaper to the list of newspapers."
    )

    addpaper_parser.set_defaults(func=addpaper)
    addpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be added.", required=True)
    addpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be added is delivered. All seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.", required=True)
    addpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be added. 0s are ignored.", required=True, nargs=7)


    # delete paper subparser
    delpaper_parser = functions.add_parser(
        'delpaper',
        help="Delete a newspaper from the list of newspapers."
    )

    delpaper_parser.set_defaults(func=delpaper)
    delpaper_parser.add_argument('-i', '--id', type=str, help="ID for paper to be deleted.", required=True)

    # get paper subparser
    getpapers_parser = functions.add_parser(
        'getpapers',
        help="Get all newspapers."
    )

    getpapers_parser.set_defaults(func=getpapers)
    getpapers_parser.add_argument('-n', '--names', help="Get the names of the newspapers.", action='store_true')
    getpapers_parser.add_argument('-d', '--days', help="Get the days the newspapers are delivered. All seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't.", action='store_true')
    getpapers_parser.add_argument('-p', '--price', help="Get the daywise prices of the newspapers. Values must be separated by semicolons.", action='store_true')

    # get undelivered logs subparser
    getlogs_parser = functions.add_parser(
        'getlogs',
        help="Get the log of all undelivered dates."
    )

    getlogs_parser.set_defaults(func=getlogs)
    getlogs_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getlogs_parser.add_argument('-y', '--year', type=int, help="Year. Must be greater than 0.")
    getlogs_parser.add_argument('-i', '--id', type=str, help="ID for paper.", required=True)
    getlogs_parser.add_argument('-u', '--undelivered', action='store_true', help="Get the undelivered dates.")
    getlogs_parser.add_argument('-p', '--price', action='store_true', help="Get the daywise prices.")

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

    # deal with month and year
    if args.month or args.year:

        try:
            npbc_core.validate_month_and_year(args.month, args.year)
        
        except npbc_exceptions.InvalidMonthYear:
            status_print(False, "Invalid month and/or year.")
            return

        month = args.month or datetime.now().month
        year = args.year or datetime.now().year

    else:
        previous_month = npbc_core.get_previous_month()
        month = previous_month.month
        year = previous_month.year

    undelivered_strings = {
        int(paper_id): []
        for paper_id, _, _, _, _ in npbc_core.get_papers()
    }

    try:
        raw_undelivered_strings = npbc_core.get_undelivered_strings(month=month, year=year)

        for _, paper_id, _, _, string in raw_undelivered_strings:
            undelivered_strings[paper_id].append(string)

    except npbc_exceptions.StringNotExists:
        pass

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

        formatted += '\nLog saved to file.'

    # print the results
    status_print(True, "Success!")
    print(f"SUMMARY:\n{formatted}")


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

    if args.id or args.all:

        try:
            npbc_core.add_undelivered_string(month, year, paper_id=args.id, *args.undelivered)

        except npbc_exceptions.PaperNotExists:
            status_print(False, f"Paper with ID {args.id} does not exist.")
            return

        except npbc_exceptions.InvalidUndeliveredString:
            status_print(False, "Invalid undelivered string(s).")
            return

    else:
        status_print(False, "No paper(s) specified.")

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
            paper_id=args.id,
            string=args.string
            string_id=args.string_id
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
            paper_id=args.id,
            string_id=args.strid,
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

    if not DAYS_MATCH_REGEX.match(input_delivery):
        raise npbc_exceptions.InvalidInput

    return [
        day == 'Y'
        for day in input_delivery
    ]


def extract_costs_from_user_input(*input_costs: float) -> list[float]:
    """convert the user input to a float list"""

    return [
        cost
        for cost in input_costs
        if cost != 0
    ]


def editpaper(args: ArgNamespace) -> None:
    """edit a paper's information"""
    try:
        npbc_core.edit_existing_paper(
            paper_id=args.id,
            name=args.name,
            days_delivered=extract_delivery_from_user_input(args.days_delivered),
            days_cost=extract_costs_from_user_input(args.days_cost)
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
        npbc_core.add_new_paper(
            name=args.name,
            days_delivered=extract_delivery_from_user_input(args.days_delivered),
            days_cost=extract_costs_from_user_input(args.days_cost)
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
        npbc_core.delete_existing_paper(args.id)

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
        papers = npbc_core.get_papers()

    except npbc_exceptions.DatabaseError as e:
        status_print(False, f"Database error: {e}\nPlease report this to the developer.")
        return

    headers = ['paper_id']

    # format the results
    status_print(True, "Success!")

    if args.name:
        headers.append('name')

    if args.days:
        headers.append('days')

    if args.price:
        headers.append('price')

    
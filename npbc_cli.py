from argparse import ArgumentParser, Namespace as arg_namespace
from datetime import datetime
from colorama import Fore, Style
from pyperclip import copy as copy_to_clipboard
from npbc_core import add_new_paper, add_undelivered_string, calculate_cost_of_all_papers, delete_existing_paper, delete_undelivered_string, edit_existing_paper, format_output, generate_sql_query, get_previous_month, query_database, save_results

def define_and_read_args() -> arg_namespace:
    parser = ArgumentParser(
        description="Calculates your monthly newspaper bill."
    )
    subparsers = parser.add_subparsers(required=True)


    calculate_parser = subparsers.add_parser(
        'calculate',
        help="Calculate the bill for one month. Previous month will be used if month or year flags are not set."
    )

    calculate_parser.set_defaults(func=calculate)
    calculate_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
    calculate_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")
    calculate_parser.add_argument('-c', '--nocopy', help="Don't copy the result of the calculation to the clipboard.", action='store_true')
    calculate_parser.add_argument('-l', '--nolog', help="Don't log the result of the calculation.", action='store_true')


    addudl_parser = subparsers.add_parser(
        'addudl',
        help="Store a date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
    )

    addudl_parser.set_defaults(func=addudl)
    addudl_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
    addudl_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")
    addudl_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)
    addudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.", required=True)


    deludl_parser = subparsers.add_parser(
        'deludl',
        help="Delete a stored date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
    )

    deludl_parser.set_defaults(func=deludl)
    deludl_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)
    deludl_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.", required=True)
    deludl_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.", required=True)


    getudl_parser = subparsers.add_parser(
        'getudl',
        help="Get a list of all stored date strings when paper(s) were not delivered."
    )

    getudl_parser.set_defaults(func=getudl)
    getudl_parser.add_argument('-k', '--key', type=str, help="Key for paper.")
    getudl_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getudl_parser.add_argument('-y', '--year', type=int, help="Year. Must be between 1 and 9999.")
    getudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.")


    editpaper_parser = subparsers.add_parser(
        'editpaper',
        help="Edit a newspaper\'s name, days delivered, and/or price."
    )

    editpaper_parser.set_defaults(func=editpaper)
    editpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be edited or added.")
    editpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.")
    editpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.")
    editpaper_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)


    addpaper_parser = subparsers.add_parser(
        'addpaper',
        help="Add a new newspaper to the list of newspapers."
    )

    addpaper_parser.set_defaults(func=addpaper)
    addpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be edited or added.", required=True)
    addpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.", required=True)
    addpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.", required=True)


    delpaper_parser = subparsers.add_parser(
        'delpaper',
        help="Delete a newspaper from the list of newspapers."
    )

    delpaper_parser.set_defaults(func=delpaper)
    delpaper_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)


    getpapers_parser = subparsers.add_parser(
        'getpapers',
        help="Get all newspapers. Returns JSON if no flags are set."
    )

    getpapers_parser.set_defaults(func=getpapers)
    getpapers_parser.add_argument('-n', '--names', help="Get the names of the newspapers.", action='store_true')
    getpapers_parser.add_argument('-d', '--days', help="Get the days the newspapers are delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't.", action='store_true')
    getpapers_parser.add_argument('-p', '--prices', help="Get the daywise prices of the newspapers. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.", action='store_true')


    getlogs_parser = subparsers.add_parser(
        'getlogs',
        help="Get the log of all undelivered dates."
    )

    getlogs_parser.set_defaults(func=getlogs)
    getlogs_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
    getlogs_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")


    update_parser = subparsers.add_parser(
        'update',
        help="Update the application."
    )

    update_parser.set_defaults(func=update)


    return parser.parse_args()

def status_print(status: bool, message: str):
    if status:
        print(f"{Fore.GREEN}{message}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}{message}{Style.RESET_ALL}")

def calculate(args: arg_namespace):
    if args.month or args.year:
        if args.month:
            month = args.month
        
        else:
            month = datetime.now().month

        if args.year:
            year = args.year

        else:
            year = datetime.now().year

    else:
        month = get_previous_month().month
        year = get_previous_month().year

    existing_strings = query_database(
        generate_sql_query(
            'undelivered_strings',
            columns=['paper_id', 'undelivered_strings'],
            conditions={
                'month': month,
                'year': year
            }
        )
    )

    undelivered_strings: dict[int, str] = {
        paper_id: undelivered_string
        for paper_id, undelivered_string in existing_strings
    }

    costs, total, undelivered_dates = calculate_cost_of_all_papers(
        undelivered_strings,
        month,
        year
    )

    formatted = format_output(costs, total, month, year)

    if not args.nocopy():
        copy_to_clipboard(formatted)

        formatted += '\nSummary copied to clipboard.'

    if not args.nolog():
        save_results(undelivered_dates, month, year)

        formatted += '\nLog saved to file.'

    print(f"{Fore.GREEN}Success!{Style.RESET_ALL} SUMMARY:\n{formatted}")


def addudl(args: arg_namespace):
    if args.month:
        month = args.month

    else:
        month = datetime.now().month

    if args.year:
        year = args.year

    else:
        year = datetime.now().year

    feedback = add_undelivered_string(
        args.key,
        args.undelivered_string,
        month,
        year
    )

    status_print(*feedback)


def deludl(args: arg_namespace):
    feedback = delete_undelivered_string(
        args.key,
        args.month,
        args.year
    )

    status_print(*feedback)

def getudl(args: arg_namespace):
    conditions = {}

    if args.key:
        conditions['paper_id'] = args.key

    if args.month:
        conditions['month'] = args.month

    if args.year:
        conditions['year'] = args.year

    if args.undelivered_string:
        conditions['undelivered_strings'] = args.undelivered_string

    undelivered_strings = query_database(
        generate_sql_query(
            'undelivered_strings',
            conditions=conditions
        )
    )

    if undelivered_strings:
        print(f"{Fore.GREEN}Success!{Style.RESET_ALL}\n")

        print(f"{Fore.YELLOW}entry_id{Style.RESET_ALL} | {Fore.YELLOW}year{Style.RESET_ALL} | {Fore.YELLOW}month{Style.RESET_ALL} | {Fore.YELLOW}paper_id{Style.RESET_ALL} | {Fore.YELLOW}string{Style.RESET_ALL}")
        
        for string in undelivered_strings:
            print('|'.join(string))

    else:
        print(f"{Fore.RED}No results found.{Style.RESET_ALL}")


def extract_days_and_costs(args: arg_namespace) -> tuple[list[bool], list[float]]:
    days = [
        bool(int(day == 'Y')) for day in str(args.days).upper()
    ]

    prices = []
    encoded_prices = [float(price) for price in args.price.split(';') if float(price) > 0]

    day_count = -1
    for day in days:
        if day:
            day_count += 1
            price = encoded_prices[day_count]

        else:
            price = 0

        prices.append(price)

    return days, prices


def editpaper(args: arg_namespace):
    days, prices = extract_days_and_costs(args)

    feedback = edit_existing_paper(
        args.key,
        args.name,
        days,
        prices
    )

    status_print(*feedback)


def addpaper(args: arg_namespace):
    days, prices = extract_days_and_costs(args)

    feedback = add_new_paper(
        args.name,
        days,
        prices
    )

    status_print(*feedback)


def delpaper(args: arg_namespace):
    feedback = delete_existing_paper(
        args.key
    )

    status_print(*feedback)


def main():
    args = define_and_read_args()
    args.func(args)
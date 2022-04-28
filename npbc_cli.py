from argparse import ArgumentParser, Namespace as arg_namespace
from datetime import datetime
from colorama import Fore, Style
from pyperclip import copy as copy_to_clipboard
from npbc_core import VALIDATE_REGEX, WEEKDAY_NAMES, add_new_paper, add_undelivered_string, calculate_cost_of_all_papers, delete_existing_paper, delete_undelivered_string, edit_existing_paper, extract_days_and_costs, format_output, generate_sql_query, get_previous_month, query_database, save_results, setup_and_connect_DB, validate_month_and_year, validate_undelivered_string

def define_and_read_args() -> arg_namespace:
    main_parser = ArgumentParser(
        description="Calculates your monthly newspaper bill."
    )
    functions = main_parser.add_subparsers(required=True)


    calculate_parser = functions.add_parser(
        'calculate',
        help="Calculate the bill for one month. Previous month will be used if month or year flags are not set."
    )

    calculate_parser.set_defaults(func=calculate)
    calculate_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
    calculate_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")
    calculate_parser.add_argument('-c', '--nocopy', help="Don't copy the result of the calculation to the clipboard.", action='store_true')
    calculate_parser.add_argument('-l', '--nolog', help="Don't log the result of the calculation.", action='store_true')


    addudl_parser = functions.add_parser(
        'addudl',
        help="Store a date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
    )

    addudl_parser.set_defaults(func=addudl)
    addudl_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
    addudl_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")
    addudl_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)
    addudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.", required=True)


    deludl_parser = functions.add_parser(
        'deludl',
        help="Delete a stored date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
    )

    deludl_parser.set_defaults(func=deludl)
    deludl_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)
    deludl_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.", required=True)
    deludl_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.", required=True)


    getudl_parser = functions.add_parser(
        'getudl',
        help="Get a list of all stored date strings when paper(s) were not delivered."
    )

    getudl_parser.set_defaults(func=getudl)
    getudl_parser.add_argument('-k', '--key', type=str, help="Key for paper.")
    getudl_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getudl_parser.add_argument('-y', '--year', type=int, help="Year. Must be between 1 and 9999.")
    getudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.")


    editpaper_parser = functions.add_parser(
        'editpaper',
        help="Edit a newspaper\'s name, days delivered, and/or price."
    )

    editpaper_parser.set_defaults(func=editpaper)
    editpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be edited or added.")
    editpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.")
    editpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.")
    editpaper_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)


    addpaper_parser = functions.add_parser(
        'addpaper',
        help="Add a new newspaper to the list of newspapers."
    )

    addpaper_parser.set_defaults(func=addpaper)
    addpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be edited or added.", required=True)
    addpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.", required=True)
    addpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.", required=True)


    delpaper_parser = functions.add_parser(
        'delpaper',
        help="Delete a newspaper from the list of newspapers."
    )

    delpaper_parser.set_defaults(func=delpaper)
    delpaper_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)


    getpapers_parser = functions.add_parser(
        'getpapers',
        help="Get all newspapers. Returns JSON if no flags are set."
    )

    getpapers_parser.set_defaults(func=getpapers)
    getpapers_parser.add_argument('-n', '--names', help="Get the names of the newspapers.", action='store_true')
    getpapers_parser.add_argument('-d', '--days', help="Get the days the newspapers are delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't.", action='store_true')
    getpapers_parser.add_argument('-p', '--prices', help="Get the daywise prices of the newspapers. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.", action='store_true')


    getlogs_parser = functions.add_parser(
        'getlogs',
        help="Get the log of all undelivered dates."
    )

    getlogs_parser.set_defaults(func=getlogs)
    getlogs_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getlogs_parser.add_argument('-y', '--year', type=int, help="Year. Must be between 1 and 9999.")
    getlogs_parser.add_argument('-k', '--key', type=str, help="Key for paper.", required=True)


    update_parser = functions.add_parser(
        'update',
        help="Update the application."
    )

    update_parser.set_defaults(func=update)


    return main_parser.parse_args()

def status_print(status: bool, message: str):
    if status:
        print(f"{Fore.GREEN}{Style.BRIGHT}{message}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}\n")

def calculate(args: arg_namespace):
    if args.month or args.year:

        if not validate_month_and_year(args.month, args.year):
            status_print(False, "Invalid month and/or year.")
            return
        
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
            columns=['paper_id', 'string'],
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

    if not args.nocopy:
        copy_to_clipboard(formatted)

        formatted += '\nSummary copied to clipboard.'

    if not args.nolog:
        save_results(undelivered_dates, month, year)

        formatted += '\nLog saved to file.'

    status_print(True, "Success!")
    print(f"SUMMARY:\n{formatted}")


def addudl(args: arg_namespace):
    if not validate_month_and_year(args.month, args.year):
        status_print(False, "Invalid month and/or year.")
        return

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
        str(args.undelivered).lower().strip(),
        month,
        year
    )

    status_print(*feedback)


def deludl(args: arg_namespace):
    if not validate_month_and_year(args.month, args.year):
        status_print(False, "Invalid month and/or year.")
        return


    feedback = delete_undelivered_string(
        args.key,
        args.month,
        args.year
    )

    status_print(*feedback)

def getudl(args: arg_namespace):
    if not validate_month_and_year(args.month, args.year):
        status_print(False, "Invalid month and/or year.")
        return
    
    conditions = {}

    if args.key:
        conditions['paper_id'] = args.key

    if args.month:
        conditions['month'] = args.month

    if args.year:
        conditions['year'] = args.year

    if args.undelivered:
        conditions['strings'] = str(args.undelivered).lower().strip()

    undelivered_strings = query_database(
        generate_sql_query(
            'undelivered_strings',
            conditions=conditions
        )
    )

    if undelivered_strings:
        status_print(True, 'Found undelivered strings.')

        print(f"{Fore.YELLOW}entry_id{Style.RESET_ALL} | {Fore.YELLOW}year{Style.RESET_ALL} | {Fore.YELLOW}month{Style.RESET_ALL} | {Fore.YELLOW}paper_id{Style.RESET_ALL} | {Fore.YELLOW}string{Style.RESET_ALL}")
        
        for string in undelivered_strings:
            print('|'.join([str(item) for item in string]))

    else:
        status_print(False, 'No undelivered strings found.')


def editpaper(args: arg_namespace):
    feedback = True, ""

    days, costs = "", ""

    if args.days:
        days = str(args.days).lower().strip()

        if not VALIDATE_REGEX['delivery'].match(days):
            feedback = False, "Invalid delivery days."

    if args.costs:
        costs = str(args.costs).lower().strip()

        if not VALIDATE_REGEX['prices'].match(costs):
            feedback = False, "Invalid prices."

    
    if feedback[0]:

        feedback = edit_existing_paper(
            args.key,
            args.name,
            *extract_days_and_costs(days, costs)
        )

    status_print(*feedback)


def addpaper(args: arg_namespace):
    feedback = True, ""

    days, costs = "", ""

    if args.days:
        days = str(args.days).lower().strip()

        if not VALIDATE_REGEX['delivery'].match(days):
            feedback = False, "Invalid delivery days."

    if args.costs:
        costs = str(args.costs).lower().strip()

        if not VALIDATE_REGEX['prices'].match(costs):
            feedback = False, "Invalid prices."

    
    if feedback[0]:

        feedback = add_new_paper(
            args.name,
            *extract_days_and_costs(days, costs)
        )

    status_print(*feedback)


def delpaper(args: arg_namespace):
    feedback = delete_existing_paper(
        args.key
    )

    status_print(*feedback)


def getpapers(args: arg_namespace):
    headers = ['paper_id']

    papers_id_list = [
        paper_id
        for paper_id, in query_database(
            generate_sql_query(
                'papers',
                columns=['paper_id']
            )
        )
    ]

    paper_name_list, paper_days_list, paper_costs_list = [], [], []

    papers_id_list.sort()

    if args.names:
        papers_names = {
            paper_id: paper_name
            for paper_id, paper_name in query_database(
                generate_sql_query(
                    'papers',
                    columns=['paper_id', 'name']
                )
            )
        }

        paper_name_list = [
            papers_names[paper_id]
            for paper_id in papers_id_list
        ]

        headers.append('name')

    if args.days:
        papers_days = {
            paper_id: {}
            for paper_id in papers_id_list
        }

        for paper_id, day_id, delivered in query_database(
            generate_sql_query(
                'papers_days_delivered',
                columns=['paper_id', 'day_id', 'delivered']
            )
        ):
            papers_days[paper_id][day_id] = delivered

        paper_days_list = [
            ''.join([
                'Y' if int(papers_days[paper_id][day_id]) == 1 else 'N'
                for day_id, _ in enumerate(WEEKDAY_NAMES)
            ])
            for paper_id in papers_id_list
        ]

        headers.append('days')

    if args.prices:
        papers_costs = {
            paper_id: {}
            for paper_id in papers_id_list
        }

        for paper_id, day_id, cost in query_database(
            generate_sql_query(
                'papers_days_cost',
                columns=['paper_id', 'day_id', 'cost']
            )
        ):
            papers_costs[paper_id][day_id] = cost

        paper_costs_list = [
            ';'.join([
                str(papers_costs[paper_id][day_id])
                for day_id, _ in enumerate(WEEKDAY_NAMES)
            ])
            for paper_id in papers_id_list
        ]

        headers.append('costs')

    print(' | '.join([
        f"{Fore.YELLOW}{header}{Style.RESET_ALL}"
        for header in headers
    ]))

    for index, paper_id in enumerate(papers_id_list):
        print(f"{paper_id}: ", end='')
        
        values = []

        if args.names:
            values.append(paper_name_list[index])

        if args.days:
            values.append(paper_days_list[index])

        if args.prices:
            values.append(paper_costs_list[index])

        print(', '.join(values))


def getlogs(args: arg_namespace):
    if validate_month_and_year(args.month, args.year):
        status_print(False, "Invalid month and/or year.")
        return
        
    conditions = {}

    if args.key:
        conditions['paper_id'] = args.key

    if args.month:
        conditions['month'] = args.month

    if args.year:
        conditions['year'] = args.year

    undelivered_dates = query_database(
        generate_sql_query(
            'undelivered_dates',
            conditions=conditions
        )
    )

    if undelivered_dates:
        status_print(True, 'Success!')

        print(f"{Fore.YELLOW}entry_id{Style.RESET_ALL} | {Fore.YELLOW}year{Style.RESET_ALL} | {Fore.YELLOW}month{Style.RESET_ALL} | {Fore.YELLOW}paper_id{Style.RESET_ALL} | {Fore.YELLOW}dates{Style.RESET_ALL}")

        for date in undelivered_dates:
            print(', '.join(date))

    else:
        status_print(False, 'No results found.')


def update(args: arg_namespace):
    status_print(False, "Update failed.")


def main():
    setup_and_connect_DB()
    args = define_and_read_args()
    args.func(args)


if __name__ == '__main__':
    main()
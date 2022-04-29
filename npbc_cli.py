from argparse import ArgumentParser, Namespace as arg_namespace
from datetime import datetime
from colorama import Fore, Style
from pyperclip import copy as copy_to_clipboard
from npbc_core import VALIDATE_REGEX, WEEKDAY_NAMES, add_new_paper, add_undelivered_string, calculate_cost_of_all_papers, delete_existing_paper, delete_undelivered_string, edit_existing_paper, extract_days_and_costs, format_output, generate_sql_query, get_previous_month, query_database, save_results, setup_and_connect_DB, validate_month_and_year, validate_undelivered_string


## setup parsers
def define_and_read_args() -> arg_namespace:

    # main parser for all commands
    main_parser = ArgumentParser(
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
    calculate_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")
    calculate_parser.add_argument('-c', '--nocopy', help="Don't copy the result of the calculation to the clipboard.", action='store_true')
    calculate_parser.add_argument('-l', '--nolog', help="Don't log the result of the calculation.", action='store_true')

    # add undelivered string subparser
    addudl_parser = functions.add_parser(
        'addudl',
        help="Store a date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
    )

    addudl_parser.set_defaults(func=addudl)
    addudl_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
    addudl_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")
    addudl_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)
    addudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.", required=True)

    # delete undelivered string subparser
    deludl_parser = functions.add_parser(
        'deludl',
        help="Delete a stored date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
    )

    deludl_parser.set_defaults(func=deludl)
    deludl_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)
    deludl_parser.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.", required=True)
    deludl_parser.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.", required=True)

    # get undelivered string subparser
    getudl_parser = functions.add_parser(
        'getudl',
        help="Get a list of all stored date strings when paper(s) were not delivered."
    )

    getudl_parser.set_defaults(func=getudl)
    getudl_parser.add_argument('-k', '--key', type=str, help="Key for paper.")
    getudl_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getudl_parser.add_argument('-y', '--year', type=int, help="Year. Must be between 1 and 9999.")
    getudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.")

    # edit paper subparser
    editpaper_parser = functions.add_parser(
        'editpaper',
        help="Edit a newspaper\'s name, days delivered, and/or price."
    )

    editpaper_parser.set_defaults(func=editpaper)
    editpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be edited or added.")
    editpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.")
    editpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.")
    editpaper_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)

    # add paper subparser
    addpaper_parser = functions.add_parser(
        'addpaper',
        help="Add a new newspaper to the list of newspapers."
    )

    addpaper_parser.set_defaults(func=addpaper)
    addpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be edited or added.", required=True)
    addpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.", required=True)
    addpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.", required=True)

    # delete paper subparser
    delpaper_parser = functions.add_parser(
        'delpaper',
        help="Delete a newspaper from the list of newspapers."
    )

    delpaper_parser.set_defaults(func=delpaper)
    delpaper_parser.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)

    # get paper subparser
    getpapers_parser = functions.add_parser(
        'getpapers',
        help="Get all newspapers. Returns JSON if no flags are set."
    )

    getpapers_parser.set_defaults(func=getpapers)
    getpapers_parser.add_argument('-n', '--names', help="Get the names of the newspapers.", action='store_true')
    getpapers_parser.add_argument('-d', '--days', help="Get the days the newspapers are delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't.", action='store_true')
    getpapers_parser.add_argument('-p', '--prices', help="Get the daywise prices of the newspapers. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.", action='store_true')

    # get undelivered logs subparser
    getlogs_parser = functions.add_parser(
        'getlogs',
        help="Get the log of all undelivered dates."
    )

    getlogs_parser.set_defaults(func=getlogs)
    getlogs_parser.add_argument('-m', '--month', type=int, help="Month. Must be between 1 and 12.")
    getlogs_parser.add_argument('-y', '--year', type=int, help="Year. Must be between 1 and 9999.")
    getlogs_parser.add_argument('-k', '--key', type=str, help="Key for paper.", required=True)

    # update application subparser
    update_parser = functions.add_parser(
        'update',
        help="Update the application."
    )

    update_parser.set_defaults(func=update)


    return main_parser.parse_args()


## print out a coloured status message using Colorama
def status_print(status: bool, message: str):
    if status:
        print(f"{Fore.GREEN}{Style.BRIGHT}{message}{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.RED}{Style.BRIGHT}{message}{Style.RESET_ALL}\n")

## calculate the cost for a given month and year
 # default to the previous month if no month and no year is given
 # default to the current month if no month is given and year is given
 # default to the current year if no year is given and month is given
def calculate(args: arg_namespace):

    # deal with month and year
    if args.month or args.year:

        feedback = validate_month_and_year(args.month, args.year)

        if not feedback[0]:
            status_print(*feedback)
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
        previous_month = get_previous_month()
        month = previous_month.month
        year = previous_month.year

    # look for undelivered strings in the database
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

    # associate undelivered strings with their paper_id
    undelivered_strings: dict[int, str] = {
        paper_id: undelivered_string
        for paper_id, undelivered_string in existing_strings
    }

    # calculate the cost for each paper, as well as the total cost
    costs, total, undelivered_dates = calculate_cost_of_all_papers(
        undelivered_strings,
        month,
        year
    )

    # format the results
    formatted = format_output(costs, total, month, year)

    # unless the user specifies so, copy the results to the clipboard
    if not args.nocopy:
        copy_to_clipboard(formatted)

        formatted += '\nSummary copied to clipboard.'

    # unless the user specifies so, log the results to the database
    if not args.nolog:
        save_results(undelivered_dates, month, year)

        formatted += '\nLog saved to file.'

    # print the results
    status_print(True, "Success!")
    print(f"SUMMARY:\n{formatted}")


## add undelivered strings to the database
 # default to the current month if no month and/or no year is given
def addudl(args: arg_namespace):

    # validate the month and year
    feedback = validate_month_and_year(args.month, args.year)

    if feedback[0]:

        # if no month is given, default to the current month
        if args.month:
            month = args.month

        else:
            month = datetime.now().month

        # if no year is given, default to the current year
        if args.year:
            year = args.year

        else:
            year = datetime.now().year

        # add the undelivered strings to the database
        feedback = add_undelivered_string(
            args.key,
            str(args.undelivered).lower().strip(),
            month,
            year
        )

    status_print(*feedback)


## delete undelivered strings from the database
def deludl(args: arg_namespace):

    # validate the month and year
    feedback = validate_month_and_year(args.month, args.year)

    # delete the undelivered strings from the database
    if feedback[0]:

        feedback = delete_undelivered_string(
            args.key,
            args.month,
            args.year
        )

    status_print(*feedback)


## get undelivered strings from the database
 # filter by whichever parameter the user provides. they as many as they want.
 # available parameters: month, year, key, string
def getudl(args: arg_namespace):

    # validate the month and year
    feedback = validate_month_and_year(args.month, args.year)

    if not feedback[0]:
        status_print(*feedback)
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

    # if the undelivered strings exist, fetch them
    undelivered_strings = query_database(
        generate_sql_query(
            'undelivered_strings',
            conditions=conditions
        )
    )

    # if there were undelivered strings, print them
    if undelivered_strings:
        status_print(True, 'Found undelivered strings.')

        print(f"{Fore.YELLOW}entry_id{Style.RESET_ALL} | {Fore.YELLOW}year{Style.RESET_ALL} | {Fore.YELLOW}month{Style.RESET_ALL} | {Fore.YELLOW}paper_id{Style.RESET_ALL} | {Fore.YELLOW}string{Style.RESET_ALL}")
        
        for string in undelivered_strings:
            print('|'.join([str(item) for item in string]))

    # otherwise, print that there were no undelivered strings
    else:
        status_print(False, 'No undelivered strings found.')


## edit the data for one paper
def editpaper(args: arg_namespace):
    feedback = True, ""
    days, costs = "", ""

    # validate the string for delivery days
    if args.days:
        days = str(args.days).lower().strip()

        if not VALIDATE_REGEX['delivery'].match(days):
            feedback = False, "Invalid delivery days."

    # validate the string for costs
    if args.costs:
        costs = str(args.costs).lower().strip()

        if not VALIDATE_REGEX['prices'].match(costs):
            feedback = False, "Invalid prices."

    # if the string for delivery days and costs are valid, edit the paper
    if feedback[0]:

        feedback = edit_existing_paper(
            args.key,
            args.name,
            *extract_days_and_costs(days, costs)
        )

    status_print(*feedback)


## add a new paper to the database
def addpaper(args: arg_namespace):
    feedback = True, ""
    days, costs = "", ""


    # validate the string for delivery days
    if args.days:
        days = str(args.days).lower().strip()

        if not VALIDATE_REGEX['delivery'].match(days):
            feedback = False, "Invalid delivery days."

    # validate the string for costs
    if args.costs:
        costs = str(args.costs).lower().strip()

        if not VALIDATE_REGEX['prices'].match(costs):
            feedback = False, "Invalid prices."

    # if the string for delivery days and costs are valid, add the paper
    if feedback[0]:

        feedback = add_new_paper(
            args.name,
            *extract_days_and_costs(days, costs)
        )

    status_print(*feedback)


## delete a paper from the database
def delpaper(args: arg_namespace):

    # attempt to delete the paper
    feedback = delete_existing_paper(
        args.key
    )

    status_print(*feedback)


## get a list of all papers in the database
 # filter by whichever parameter the user provides. they may use as many as they want (but keys are always printed)
 # available parameters: name, days, costs
 # the output is provided as a formatted table, printed to the standard output
def getpapers(args: arg_namespace):
    headers = ['paper_id']

    # fetch a list of all papers' IDs
    papers_id_list = [
        paper_id
        for paper_id, in query_database(
            generate_sql_query(
                'papers',
                columns=['paper_id']
            )
        )
    ]

    # initialize lists for the data
    paper_name_list, paper_days_list, paper_costs_list = [], [], []

    # sort the papers' IDs (for the sake of consistency)
    papers_id_list.sort()

    # if the user wants names, fetch that data and add it to the list
    if args.names:

        # first get a dictionary of {paper_id: paper_name}
        papers_names = {
            paper_id: paper_name
            for paper_id, paper_name in query_database(
                generate_sql_query(
                    'papers',
                    columns=['paper_id', 'name']
                )
            )
        }

        # then use the sorted IDs list to create a sorted names list
        paper_name_list = [
            papers_names[paper_id]
            for paper_id in papers_id_list
        ]

        headers.append('name')

    # if the user wants delivery days, fetch that data and add it to the list
    if args.days:

        # initialize a dictionary of {paper_id: {day_id: delivery}}
        papers_days = {
            paper_id: {}
            for paper_id in papers_id_list
        }

        # then get the data for each paper
        for paper_id, day_id, delivered in query_database(
            generate_sql_query(
                'papers_days_delivered',
                columns=['paper_id', 'day_id', 'delivered']
            )
        ):
            papers_days[paper_id][day_id] = delivered

        # format the data so that it matches the regex pattern /^[YN]{7}$/, the same way the user must input this data
        paper_days_list = [
            ''.join([
                'Y' if int(papers_days[paper_id][day_id]) == 1 else 'N'
                for day_id, _ in enumerate(WEEKDAY_NAMES)
            ])
            for paper_id in papers_id_list
        ]

        headers.append('days')

    # if the user wants costs, fetch that data and add it to the list
    if args.prices:

        # initialize a dictionary of {paper_id: {day_id: price}}
        papers_costs = {
            paper_id: {}
            for paper_id in papers_id_list
        }

        # then get the data for each paper
        for paper_id, day_id, cost in query_database(
            generate_sql_query(
                'papers_days_cost',
                columns=['paper_id', 'day_id', 'cost']
            )
        ):
            papers_costs[paper_id][day_id] = cost

        # format the data so that it matches the regex pattern /^[x](;[x]){6}$/, where /x/ is a number that may be either a floating point or an integer, the same way the user must input this data.
        paper_costs_list = [
            ';'.join([
                str(papers_costs[paper_id][day_id])
                for day_id, _ in enumerate(WEEKDAY_NAMES)
            ])
            for paper_id in papers_id_list
        ]

        headers.append('costs')

    # print the headers
    print(' | '.join([
        f"{Fore.YELLOW}{header}{Style.RESET_ALL}"
        for header in headers
    ]))

    # print the data
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


## get a log of all deliveries for a paper
 # the user may specify parameters to filter the output by. they may use as many as they want, or none
 # available parameters: paper_id, month, year
def getlogs(args: arg_namespace):
    
    # validate the month and year
    feedback = validate_month_and_year(args.month, args.year)

    if not feedback[0]:
        status_print(*feedback)
        return
        
    conditions = {}

    # if the user specified a particular paper, add it to the conditions
    if args.key:
        conditions['paper_id'] = args.key

    if args.month:
        conditions['month'] = args.month

    if args.year:
        conditions['year'] = args.year

    # fetch the data
    undelivered_dates = query_database(
        generate_sql_query(
            'undelivered_dates',
            conditions=conditions
        )
    )

    # if data was found, print it
    if undelivered_dates:
        status_print(True, 'Success!')

        print(f"{Fore.YELLOW}entry_id{Style.RESET_ALL} | {Fore.YELLOW}year{Style.RESET_ALL} | {Fore.YELLOW}month{Style.RESET_ALL} | {Fore.YELLOW}paper_id{Style.RESET_ALL} | {Fore.YELLOW}dates{Style.RESET_ALL}")

        for date in undelivered_dates:
            print(', '.join(date))

    # if no data was found, print an error message
    else:
        status_print(False, 'No results found.')


## update the application
 # under normal operation, this function should never run
 # if the update CLI argument is provided, this script will never run and the updater will be run instead
def update(args: arg_namespace):
    status_print(False, "Update failed.")


## run the application
def main():
    setup_and_connect_DB()
    args = define_and_read_args()
    args.func(args)


if __name__ == '__main__':
    main()
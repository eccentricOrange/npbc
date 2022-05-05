from argparse import ArgumentParser, Namespace as ArgNamespace
from datetime import datetime
from colorama import Fore, Style
import npbc_core


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
        help="Store a date when paper(s) were not delivered. Current month will be used if month or year flags are not set."
    )

    addudl_parser.set_defaults(func=addudl)
    addudl_parser.add_argument('-m', '--month', type=int, help="Month to register undelivered incident(s) for. Must be between 1 and 12.")
    addudl_parser.add_argument('-y', '--year', type=int, help="Year to register undelivered incident(s) for. Must be greater than 0.")
    addudl_parser.add_argument('-i', '--id', type=str, help="ID of paper to register undelivered incident(s) for.", required=True)
    addudl_parser.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.", required=True, nargs='+')


    # delete undelivered string subparser
    deludl_parser = functions.add_parser(
        'deludl',
        help="Delete a stored date when paper(s) were not delivered. If no parameters are provided, the function will not default; it will throw an error instead."
    )

    deludl_parser.set_defaults(func=deludl)
    deludl_parser.add_argument('-i', '--id', type=str, help="ID of paper to unregister undelivered incident(s) for.")
    deludl_parser.add_argument('-m', '--month', type=int, help="Month to unregister undelivered incident(s) for. Must be between 1 and 12.")
    deludl_parser.add_argument('-y', '--year', type=int, help="Year to unregister undelivered incident(s) for. Must be greater than 0.")


    # get undelivered string subparser
    getudl_parser = functions.add_parser(
        'getudl',
        help="Get a list of all stored date strings when paper(s) were not delivered. All parameters are optional and act as filters."
    )

    getudl_parser.set_defaults(func=getudl)
    getudl_parser.add_argument('-i', '--id', type=str, help="ID for paper.")
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
    editpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited. Values must be separated by semicolons, and 0s are ignored.")
    editpaper_parser.add_argument('-i', '--id', type=str, help="ID for paper to be edited.", required=True)


    # add paper subparser
    addpaper_parser = functions.add_parser(
        'addpaper',
        help="Add a new newspaper to the list of newspapers."
    )

    addpaper_parser.set_defaults(func=addpaper)
    addpaper_parser.add_argument('-n', '--name', type=str, help="Name for paper to be added.", required=True)
    addpaper_parser.add_argument('-d', '--days', type=str, help="Number of days the paper to be added is delivered. All seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.", required=True)
    addpaper_parser.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be added. Values must be separated by semicolons, and 0s are ignored.", required=True)


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
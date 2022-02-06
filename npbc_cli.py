from datetime import datetime
from json import dumps
from pyperclip import copy as copy_to_clipboard
from argparse import ArgumentParser, Namespace as arg_namespace
from npbc_core import NPBC_core
from sys import exit

class NPBC_cli(NPBC_core):

    
    def __init__(self):
        self.define_schema()

    def define_and_read_args(self) -> arg_namespace:
        self.parser = ArgumentParser(
            description="Calculates your monthly newspaper bill."
        )
        subparsers = self.parser.add_subparsers(required=True)


        calculate = subparsers.add_parser(
            'calculate',
            help="Calculate the bill for one month. Previous month will be used if month or year flags are not set."
        )

        calculate.set_defaults(func=self.calculate)
        calculate.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
        calculate.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")
        calculate.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.")
        calculate.add_argument('-c', '--nocopy', help="Don't copy the result of the calculation to the clipboard.",
                action='store_true')
        calculate.add_argument('-l', '--nolog', help="Don't log the result of the calculation.",
                action='store_true')


        addudl = subparsers.add_parser(
            'addudl',
            help="Store a date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
        )

        addudl.set_defaults(func=self.addudl)
        addudl.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.")
        addudl.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.")
        addudl.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)
        addudl.add_argument('-u', '--undelivered', type=str, help="Dates when you did not receive any papers.", required=True)


        deludl = subparsers.add_parser(
            'deludl',
            help="Delete a stored date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
        )

        deludl.set_defaults(func=self.deludl)
        deludl.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)
        deludl.add_argument('-m', '--month', type=int, help="Month to calculate bill for. Must be between 1 and 12.", required=True)
        deludl.add_argument('-y', '--year', type=int, help="Year to calculate bill for. Must be between 1 and 9999.", required=True)


        getudl = subparsers.add_parser(
            'getudl',
            help="Get a list of all stored date strings when paper(s) were not delivered."
        )

        getudl.set_defaults(func=self.getudl)


        editpaper = subparsers.add_parser(
            'editpaper',
            help="Edit a newspaper\'s name, days delivered, and/or price."
        )

        editpaper.set_defaults(func=self.editpaper)
        editpaper.add_argument('-n', '--name', type=str, help="Name for paper to be edited or added.")
        editpaper.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.")
        editpaper.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.")
        editpaper.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)


        addpaper = subparsers.add_parser(
            'addpaper',
            help="Add a new newspaper to the list of newspapers."
        )

        addpaper.set_defaults(func=self.addpaper)
        addpaper.add_argument('-n', '--name', type=str, help="Name for paper to be edited or added.", required=True)
        addpaper.add_argument('-d', '--days', type=str, help="Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.", required=True)
        addpaper.add_argument('-p', '--price', type=str, help="Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.", required=True)


        delpaper = subparsers.add_parser(
            'delpaper',
            help="Delete a newspaper from the list of newspapers."
        )

        delpaper.set_defaults(func=self.delpaper)
        delpaper.add_argument('-k', '--key', type=str, help="Key for paper to be edited, deleted, or added.", required=True)


        getpapers = subparsers.add_parser(
            'getpapers',
            help="Get all newspapers."
        )

        getpapers.set_defaults(func=self.getpapers)


        getlogs = subparsers.add_parser(
            'getlogs',
            help="Get the log of all undelivered dates."
        )

        getlogs.set_defaults(func=self.getlogs)


        update = subparsers.add_parser(
            'update',
            help="Update the application."
        )

        update.set_defaults(func=self.update)


        return self.parser.parse_args()

    def format_and_copy(self) -> None:
        string = self.format()

        print(string)

        if not self.args.nocopy:
            copy_to_clipboard(string)
            print("\nSummary copied to clipboard.")

    def calculate(self) -> None:
        self.set_dates()
        self.get_undelivered_strings()
        self.get_number_of_weekdays()
        self.calculate_all_papers()
        self.format_and_copy()

        if not self.args.nolog:
            self.save_results()
            print("Saved results to logs.") 

    def deludl(self):
        self.set_dates()
        self.get_undelivered_strings()
        self.delete_undelivered_string(self.args.key)

    def addudl(self):
        self.set_dates()
        self.get_undelivered_strings()
        self.add_undelivered_string(self.args.key, self.undelivered_strings[self.args.key])

    def delpaper(self):
        self.delete_existing_paper(self.args.key)

    def addpaper(self):
        self.create_new_paper(self.args.name, self.extract_days_and_cost())

    def editpaper(self):
        self.update_existing_paper(self.args.key, self.args.name, self.extract_days_and_cost())

    def getpapers(self):
        print(dumps(self.get_all_papers(), indent=4))

    def getudl(self):
        print(dumps(self.get_undelivered_strings(), indent=4))

    def getlogs(self):
        print(dumps(self.get_undelivered_dates(), indent=4))

    def extract_undelivered_data(self):
        if self.args.undelivered is not None:
            undelivered_data = self.args.undelivered.split(';')

            for paper in undelivered_data:
                paper_key, undelivered_string = paper.split(':')

                if paper_key in self.undelivered_strings:
                    self.undelivered_strings[paper_key] += ',' + undelivered_string

                else:
                    self.undelivered_strings[paper_key] = undelivered_string

    def set_dates(self):
        if self.args.month is None and self.args.year is None:
            self.month = self.get_previous_month().month
            self.year = self.get_previous_month().year

        elif self.args.month is not None and self.args.year is None:
            self.month = self.args.month
            self.year = datetime.today().year

        elif self.args.month is None and self.args.year is not None:
            self.month = datetime.today().month
            self.year = self.args.year

        else:
            self.month = self.args.month
            self.year = self.args.year

    def extract_days_and_cost(self) -> list:
        return self.decode_delivered_and_cost(self.args.days, self.args.price)

    def update(self):
        pass

    def run(self) -> None:
        self.args = self.define_and_read_args()
        self.args.func()
        self.connection.close()

def main() -> None:
    calculator = NPBC_cli()
    calculator.run()
    del calculator
    exit(0)

if __name__ == '__main__':
    main()
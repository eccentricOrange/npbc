from datetime import datetime
from json import dumps
from pyperclip import copy as copy_to_clipboard
from argparse import ArgumentParser, RawTextHelpFormatter, Namespace as arg_namespace
from npbc_core import NPBC_core

class NPBC_cli(NPBC_core):
    functions = {
        'calculate': {
            'choice': 'calculate',
            'help': "Calculate the bill for one month. Previous month will be used if month or year flags are not set."
        },
        'addudl': {
            'choice': 'addudl',
            'help': "Store a date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
        },
        'deludl': {
            'choice': 'deludl',
            'help': "Delete a stored date when paper(s) were not delivered. Previous month will be used if month or year flags are not set."
        },
        'getudl': {
            'choice': 'getudl',
            'help': "Get a list of all stored date strings when paper(s) were not delivered."
        },
        'editpaper': {
            'choice': 'editpaper',
            'help': "Edit a newspaper's name, key, and other delivery data."
        },
        'addpaper': {
            'choice': 'addpaper',
            'help': "Add a new newspaper to the list of newspapers."
        },
        'delpaper': {
            'choice': 'delpaper',
            'help': "Delete a newspaper from the list of newspapers."
        },
        'getpapers': {
            'choice': 'getpapers',
            'help': "Get all newspapers."
        },
        'update': {
            'choice': 'update',
            'help': "Update the application."
        },
        'ui': {
                'choice': 'ui',
                'help': "Launch interactive CLI."
        }
    }

    arguments = {
        'month': {
            'short': '-m',
            'long': '--month',
            'type': int,
            'help': "Month to calculate bill for. Must be between 1 and 12.",
        },
        'year': {
            'short': '-y',
            'long': '--year',
            'type': int,
            'help': "Year to calculate bill for. Must be between 1 and 9999.",
        },
        'undelivered': {
            'short': '-u',
            'long': '--undelivered',
            'type': str,
            'help': "Dates when you did not receive any papers.",
        },
        'key': {
            'short': '-k',
            'long': '--key',
            'type': str,
            'help': "Key for paper to be edited, deleted, or added.",
        },
        'name': {
            'short': '-n',
            'long': '--name',
            'type': str,
            'help': "Name for paper to be edited or added.",
        },
        'days': {
            'short': '-d',
            'long': '--days',
            'type': str,
            'help': "Number of days the paper to be edited or added, is delivered. Monday is the first day, and all seven weekdays are required. A 'Y' means it is delivered, and an 'N' means it isn't. No separator required.",
        },
        'price': {
            'short': '-p',
            'long': '--price',
            'type': str,
            'help': "Daywise prices of paper to be edited or added. Monday is the first day. Values must be separated by semicolons, and 0s are ignored.",
        },
        'nolog': {
            'short': '-l',
            'long': '--nolog',
            'help': "Don't log the result of the calculation.",
            'action': 'store_true'
        },
        'nocopy': {
            'short': '-c',
            'long': '--nocopy',
            'help': "Don't copy the result of the calculation to the clipboard.",
            'action': 'store_true'
        }
    }

    def __init__(self):
        self.define_schema()
        self.args = self.define_and_read_args()

    def define_and_read_args(self) -> arg_namespace:
        self.parser = ArgumentParser(
            description="Calculates your monthly newspaper bill.",
            formatter_class=RawTextHelpFormatter
        )

        self.parser.add_argument(
            'command',
            # nargs='?',
            choices=[value['choice'] for key, value in self.functions.items()],
            help='\n'.join([f"{value['choice']}: {value['help']}" for key, value in self.functions.items()])
        )

        for key, value in self.arguments.items():
            if 'action' in value:
                self.parser.add_argument(
                    value['short'],
                    value['long'],
                    action=value['action'],
                    help=value['help']
                )

            else:
                self.parser.add_argument(
                    value['short'],
                    value['long'],
                    type=value['type'],
                    help=value['help']
                )

        return self.parser.parse_args()

    def format_and_copy(self) -> None:
        string = self.format()

        print(string)

        if not self.args.nocopy:
            copy_to_clipboard(string)
            print("\nSummary copied to clipboard.")

    def calculate(self) -> None:
        self.get_number_of_weekdays()
        self.calculate_all_papers()
        self.format_and_copy()

        if not self.args.nolog:
            self.save_results()
            print("Saved results to logs.") 

class NPBC_cli_args(NPBC_cli):
    def __init__(self):
        NPBC_cli.__init__(self)

    def check_args(self) -> None:
        if self.args.command == 'calculate' or self.args.command == 'addudl' or self.args.command == 'deludl':

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

            self.get_undelivered_strings()

            if self.args.command != 'deludl':
                if self.args.undelivered is not None:
                    undelivered_data = self.args.undelivered.split(';')

                    for paper in undelivered_data:
                        paper_key, undelivered_string = paper.split(':')

                        if paper_key in self.undelivered_strings:
                            self.undelivered_strings[paper_key] += ',' + undelivered_string

                        else:
                            self.undelivered_strings[paper_key] = undelivered_string

                if self.args.command == 'calculate':
                    self.calculate()

                else:
                    self.add_undelivered_string(self.args.key, self.undelivered_strings[self.args.key])

            else:
                self.delete_undelivered_string(self.args.key)

        elif self.args.command == 'getudl':
            print(dumps(self.get_undelivered_strings(), indent=4))

        elif self.args.command == 'getpapers':
            print(dumps(self.get_all_papers(), indent=4))

        elif self.args.command == 'editpaper':
            self.update_existing_paper(self.args.key, self.args.name, self.extract_days_and_cost())

        elif self.args.command == 'addpaper':
            self.create_new_paper(self.args.name, self.extract_days_and_cost())

        elif self.args.command == 'delpaper':
            self.delete_existing_paper(self.args.key)

    def extract_days_and_cost(self) -> list:
        return self.decode_delivered_and_cost(self.args.days, self.args.price)

    def run(self) -> None:
        if self.args.command != 'ui' and self.args.command in self.functions:
            self.check_args()
            self.connection.close()
        
        else:
            self.connection.close()
            exit(1)

# def interactive() -> None:
#     calculator = NPBC_cli_interactive()
#     calculator.run()
#     del calculator

def args() -> None:
    calculator = NPBC_cli_args()
    calculator.run()
    del calculator

def main() -> None:
    # interactive()
    args()
    exit(0)

if __name__ == '__main__':
    main()
import calendar
import datetime
import sys
import os
from argparse import ArgumentParser, RawTextHelpFormatter
from json import dumps
from pathlib import Path
from npbc_core import NPBC_core

from pyperclip import copy as copy_to_clipboard

CONFIG_FILEPATH = Path(Path.home()) / '.npbc' / 'config.json'
# CONFIG_FILEPATH = Path('data') / 'config.json'
HELP_FILEPATH = Path(f'includes/undelivered_help.pdf')


class NPBC(NPBC_core):

    functions = {
        'calculate': {
            'choice': 'calculate',
            'help': 'Calculate the bill for one month. Previous month will be used if month or year flags are not set.'
        },
        'addudl': {
            'choice': 'addudl',
            'help': 'Store a date when paper(s) were not delivered. Previous month will be used if month or year flags are not set.'
        },
        'deludl': {
            'choice': 'deludl',
            'help': 'Delete a stored date when paper(s) were not delivered. Previous month will be used if month or year flags are not set.'
        },
        'editpapers': {
            'choice': 'editpapers',
            'help': 'Edit newspapers, their keys, and other delivery data.'
        },
        'editconfig': {
            'choice': 'editconfig',
            'help': 'Edit filepaths of record files and newspaper data.'
        },
        'update': {
            'choice': 'update',
            'help': 'Update the application.'
        },
        'ui': {
            'choice': 'ui',
            'help': 'Launch interactive CLI.'
        }
    }

    def __init__(self):
        os.chdir(sys._MEIPASS)
        self.load_files()
        self.args = self.define_and_read_args()

    def run(self):
        self.check_args()

    def define_and_read_args(self):
        self.parser = ArgumentParser(
            description='Calculates your monthly newspaper bill.',
            formatter_class=RawTextHelpFormatter
        )

        self.parser.add_argument(
            'command',
            nargs='?',
            choices=[value['choice'] for key, value in self.functions.items()],
            default='ui',
            help='\n'.join([f"{value['choice']}: {value['help']}" for key, value in self.functions.items()])
        )

        self.parser.add_argument(
            '-m', '--month', type=int, help="the month for which you want to calculate a bill")

        self.parser.add_argument(
            '-y', '--year', type=int, help="the year for which you want to calculate a bill")

        self.parser.add_argument(
            '-p', '--papers', type=str, help="dates when you did not receive any papers")

        self.parser.add_argument(
            '-f', '--files', type=str, help="data for filepaths to edited")

        self.parser.add_argument(
            '-l', '--nolog', action='store_true', help="do not log the result")

        self.parser.add_argument(
            '-c', '--nocopy', action='store_true', help="do not copy the result to the clipboard")

        return self.parser.parse_args()

    def check_args(self):
        if self.args.command == 'calculate' or self.args.command == 'addudl' or self.args.command == 'deludl':

            if self.args.month is None and self.args.year is None:
                self.month = self.get_previous_month().month
                self.year = self.get_previous_month().year

            elif self.args.month is not None and self.args.year is None:
                self.month = self.args.month
                self.year = datetime.datetime.today().year

            elif self.args.month is None and self.args.year is not None:
                self.month = datetime.datetime.today().month
                self.year = self.args.year

            else:
                self.month = self.args.month
                self.year = self.args.year

            self.prepare_dated_data()

            if self.args.command != 'deludl':

                if self.args.papers is not None:
                    undelivered_data = self.args.papers.split(';')

                    for paper in undelivered_data:
                        paper_key, undelivered_string = paper.split(':')

                        self.undelivered_strings[f"{self.month}/{self.year}"][paper_key].append(
                            undelivered_string)

                if self.args.command == 'calculate':
                    self.calculate()

                else:
                    self.addudl()

            else:
                self.deludl()

        elif self.args.command == 'editpapers':
            self.edit_papers()

        elif self.args.command == 'editconfig':
            self.edit_config_files()

        elif self.args.command == 'update':
            self.update()

        elif self.args.command == 'ui':
            self.run_ui()

    def run_ui(self):
        task = input(
            "What do you want to do right now? ([c]alculate, edit the [p]apers, edit the [f]iles configuration, [a]dd undelivered data, [r]emove undelivered data, display [h]elp, [u]pdate, or e[x]it) ").strip().lower()

        if task in ['c', 'calculate', 'a', 'add', 'r', 'remove']:
            month = input(
                "\nPlease enter the month you want to calculate (either enter a number, or leave blank to use the previous month): ")

            if month.isdigit():
                self.month = int(month)

            else:
                self.month = self.get_previous_month().month

            year = input(
                "\nPlease enter the year you want to calculate (either enter a number, or leave blank to use the year of the previous month): ")

            if year.isdigit():
                self.year = int(year)

            else:
                self.year = self.get_previous_month().year

            self.prepare_dated_data()

            if task not in ['r', 'remove']:
                self.acquire_undelivered_papers()

                if task in ['c', 'calculate']:
                    self.calculate()

                else:
                    self.addudl()

            else:
                self.deludl()

        elif task in ['p', 'papers']:
            self.edit_papers()

        elif task in ['f', 'files']:
            self.edit_config_files()

        elif task in ['u', 'update']:
            self.update()

        elif task in ['x', 'exit']:
            pass

        else:
            self.parser.print_help()

    def edit_papers(self):
        print ("The following papers currently exist.\n")

        for paper_key in self.papers:
            print (f"{paper_key}: {self.papers[paper_key]['name']}")
        

        mode = input(
            "\n Do you want to create a [n]ew newspaper, [e]dit an existing one, [d]elete an existing one, or e[x]it? ")

        if mode.lower() in ['n', 'ne', 'new']:
            self.create_new_paper()

        elif mode.lower() in ['e', 'ed', 'edi', 'edit']:
            self.edit_existing_paper()

        elif mode.lower() in ['d', 'de', 'del', 'dele', 'delet', 'delete']:
            self.delete_existing_paper()

        elif mode.lower() in ['x', 'ex', 'exi', 'exit']:
            pass

        else:
            print("\nInvalid mode. Please try again.")

    def create_new_paper(self):
        paper_name = input("\nWhat is the name of the newspaper? ")
        paper_key = input(f"Enter a short name for {paper_name}: ")

        if paper_key in self.papers:
            print(f"{paper_key} already exists. Please try editing it.")
            exit(0)

        paper_days = {}

        for day in calendar.day_name:
            sold = input(f"\nIs the newspaper sold on {day}? ([y]es/[N]o) ")

            if sold.lower() in ['y', 'ye', 'yes']:
                sold = int(True)
                cost = float(input(f"What is the cost on {day}? "))

            else:
                sold = int(False)
                cost = 0.0

            paper_days[day] = {'sold': sold, 'cost': cost}

        print(f"\n{paper_name} has been added.")

        self.papers[paper_key] = {'name': paper_name,
                                  'key': paper_key, 'days': paper_days}

        with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
            papers_file.write(dumps(self.papers))

    def edit_existing_paper(self):
        paper_key = input("\nEnter the key of the paper to edit: ")

        if paper_key not in self.papers:
            print(f"{paper_key} does not exist. Please try again.")
            exit(0)

        print(f"Editing {self.papers[paper_key]['name']}.")

        new_paper_key = input(
            "Enter a new key for the paper, or leave blank to retain: ")

        if new_paper_key != '':
            self.papers[new_paper_key] = self.papers[paper_key]
            del self.papers[paper_key]

        else:
            new_paper_key = paper_key

        new_paper_name = input(
            "Enter a new name for the paper, or leave blank to retain: ")

        if new_paper_name != '':
            self.papers[new_paper_key]['name'] = new_paper_name

        else:
            new_paper_name = self.papers[paper_key]['name']

        print(f"\nHere is the current cost status for {new_paper_name}.")

        for day_name, day in self.papers[new_paper_key]['days'].items():
            sold = 'SOLD' if int(day['sold']) == 1 else 'NOT SOLD'
            print(f"{day_name}: {sold} {day['cost'] if sold == 'SOLD' else ''}")

        for day in [i for i in calendar.day_name]:
            sold = input(f"\nIs the newspaper sold on {day}? ([y]es/[N]o) ")

            if sold.lower() in ['y', 'ye', 'yes']:
                sold = int(True)
                cost = float(input(f"What is the cost on {day}? "))

            else:
                sold = int(False)
                cost = 0.0

            self.papers[new_paper_key]['days'][day] = {
                'sold': sold, 'cost': cost}

        print(f"\n{self.papers[new_paper_key]['name']} has been edited.")

        with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
            papers_file.write(dumps(self.papers))

    def delete_existing_paper(self):
        paper_key = input("\nEnter the key of the paper to delete: ")

        if paper_key not in self.papers:
            print(f"{paper_key} does not exist. Please try again.")
            exit(0)

        sure = input(
            f"Are you sure you want to delete {self.papers[paper_key]['name']}? ([y]es/[N]o) ")

        if sure.lower() in ['y', 'ye', 'yes']:
            del self.papers[paper_key]

            print(f"\n{self.papers[paper_key]['name']} has been deleted.")

            with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
                papers_file.write(dumps(self.papers))

        else:
            print("\nDeletion cancelled.")

    def acquire_undelivered_papers(self):
        confirmation = input(
            "\nDo you want to report any undelivered data? ([Y]es/[n]o) ")

        while confirmation.lower() in ['y', 'ye,' 'yes']:
            print("These are the available newspapers:\n")

            for paper_key, value in self.papers.items():
                print(f"\t{paper_key}: {value['name']}")

            print("\tall: ALL NEWSPAPERS\n")

            paper_key = input(
                "Please enter the key of the newspaper you want to report, or press Return to cancel: ")

            if paper_key == '':
                pass

            elif (paper_key in self.papers) or (paper_key == 'all'):
                self.report_undelivered_dates(paper_key)

            else:
                print("Invalid key. Please try again.")

            confirmation = input(
                "Do you want to report any more undelivered data? ([Y]es/[n]o) ")

    def report_undelivered_dates(self, paper_key: str):
        finished = False
        string = ""

        while not finished:
            string = input(
                f"Please tell us when {paper_key} was undelivered, or enter '?' for help: ").strip()

            if string == '?' or string == '':
                os.system(HELP_FILEPATH)

            else:
                self.undelivered_strings[f"{self.month}/{self.year}"][paper_key].append(
                    string)

                finished = True

    def format_and_copy(self):
        string = f"For {datetime.datetime(self.year, self.month, 1):%B %Y}\n\n"
        string += f"*TOTAL: {self.totals.pop('TOTAL')}*\n"

        for paper_key, value in self.totals.items():
            string += f"{self.papers[paper_key]['name']}: {value}\n"

        print(string)

        if not self.args.nocopy:
            copy_to_clipboard(string)

    def calculate(self):
        self.undelivered_strings_to_dates()
        self.calculate_all_papers()
        self.format_and_copy()
        self.save_results()

    def edit_config_files(self):
        if self.args.files is not None:

            filepaths = self.args.files.split(';')

            for filepath in filepaths:
                path_key, path = filepath.split(':')

                if path_key in self.config:
                    self.config[path_key] = path

        else:
            print("\nThe following filepaths can be edited:")

            for key in self.config:
                print(f"{key}: {self.config[key]}")

            confirmation = input(
                "\nDo you want to edit any of these paths? ([Y]es/[n]o) ").lower().strip()

            while confirmation in ['y', 'ye', 'yes']:

                invalid = True

                while invalid:
                    path_key = input("\nPlease enter the path key to edit: ")

                    if path_key in self.config:
                        self.config[path_key] = input(
                            f"Please enter the new path for {path_key}: ")
                        invalid = False

                    else:
                        print("Invalid key. Please try again.")

                confirmation = input(
                    "\nDo you want to edit any more of these paths? ([Y]es/[n]o) ").lower().strip()

        with open(CONFIG_FILEPATH, 'w') as config_file:
            config_file.write(dumps(self.config))



def main():
    calculator = NPBC()
    calculator.run()


if __name__ == '__main__':
    main()

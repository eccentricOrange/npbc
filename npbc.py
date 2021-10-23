import calendar
import datetime
import os
import sys
from argparse import ArgumentParser
from json import dumps, loads
from pathlib import Path

from pyperclip import copy as copy_to_clipboard


class Main():
    month = 0
    year = 0
    totals = {'TOTAL': 0.0}
    undelivered_dates = {}

    def __init__(self):
        os.chdir(sys._MEIPASS)
        self.load_files()
        self.args = self.define_and_read_args()
        print(self.args)

    def run(self):
        self.check_args()

    def load_files(self):
        with open(f'includes/config.json', 'r') as config_file:
            self.config = loads(config_file.read())

        if self.config['root_folder'] == 'UNSET':
            self.config['root_folder'] = f"{str(Path.home())}/.npbc"

            with open(f"includes/config.json", 'w') as config_file:
                config_file.write(dumps(self.config))

        with open(f"{self.config['root_folder']}/{self.config['papers_data']}", 'r') as papers_file:
            self.papers = loads(papers_file.read())

        with open(f"{self.config['root_folder']}/{self.config['undelivered_strings']}", 'r') as undelivered_file:
            self.undelivered_strings = loads(undelivered_file.read())

        for paper_key in self.papers:
            if paper_key not in self.undelivered_strings:
                self.undelivered_strings[paper_key] = []

            self.totals[paper_key] = 0.0
            self.undelivered_dates[paper_key] = []

    def define_and_read_args(self):
        self.parser = ArgumentParser(description='calculate your newspaper bill')
        self.parser.add_argument('command', choices=['calculate', 'addudl', 'editpapers', 'ui'])

        self.parser.add_argument('-m', '--month', type=int, help='the month for which you want to calculate a bill')

        self.parser.add_argument('-y', '--year', type=int, help='the year for which you want to calculate a bill')

        self.parser.add_argument('-p', '--papers', type=str, help="dates when you didn't receive any papers")

        self.parser.add_argument('-l', '--nolog', action='store_true', help='do not log the result')

        self.parser.add_argument('-c', '--nocopy', action='store_true', help='do not copy the result to the clipboard')

        return self.parser.parse_args()

    def check_args(self):
        if self.args.command == 'calculate' or self.args.command == 'addudl':
            if self.args.month is None or self.args.year is None:
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

            if self.args.papers is not None:
                undelivered_data = self.args.papers.split(';')

                for paper in undelivered_data:
                    paper_key, undelivered_string = paper.split(':')

                    self.undelivered_strings[f"{self.month}/{self.year}"][paper_key].append(undelivered_string)

            else:
                self.acquire_undelivered_papers()

            if self.args.command == 'calculate':
                self.calculate()

            else:
                self.addudl()

        elif self.args.command == 'editpapers':
            self.edit_papers()

        elif self.args.command == 'ui':
            self.run_ui()

    def run_ui(self):
        task = input("What do you want to do right now? ([c]alculate, edit the [p]apers, edit the [f]iles configuration, add [u]ndelivered data, display [h]elp, or e[x]it) ").strip().lower()

        if task in ['c', 'calculate', 'u', 'undelivered']:
            month = input("\nPlease enter the month you want to calculate (either enter a number, or leave blank to use the previous month): ")

            if month.isdigit():
                self.month = int(month)

            else:
                self.month = self.get_previous_month().month

            year = input("\nPlease enter the year you want to calculate (either enter a number, or leave blank to use the year of the previous month): ")

            if year.isdigit():
                self.year = int(year)

            else:
                self.year = self.get_previous_month().year

            self.prepare_dated_data()
            self.acquire_undelivered_papers()

            if task in ['c', 'calculate']:
                self.calculate()
            
            else:
                self.addudl()

        elif task in ['p', 'papers']:
            self.edit_papers()

        elif task in ['f', 'files']:
            self.edit_config_files()

        elif task in ['x', 'exit']:
            pass
            
        else:
            self.parser.print_help()

    def edit_papers(self):
        mode = input("\n Do you want to create a [n]ew newspaper, [e]dit an existing one, [d]elete an existing one, or e[x]it? ")

        if mode.lower() in ['n', 'ne', 'new']:
            self.create_new_paper()

        elif mode.lower() in ['e', 'ed', 'edi', 'edit']:
            self.edit_existing_paper()

        elif mode.lower() in ['d', 'de', 'del', 'dele', 'delet', 'delete']:
            self.delete_existing_paper()

        elif mode.lower() in ['x', 'ex', 'exi', 'exit']:
            exit(0)

        else:
            print("\nInvalid mode. Please try again.")

    def create_new_paper(self):
        paper_name = input("What is the name of the newspaper? ")
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

        self.papers[paper_key] = {'name': paper_name, 'key': paper_key, 'days': paper_days}

        with open(f"{self.config['root_folder']}/{self.config['papers_data']}", 'w') as papers_file:
            papers_file.write(dumps(self.papers))

    def edit_existing_paper(self):
        paper_key = input("Enter the key of the paper to edit: ")

        if paper_key not in self.papers:
            print(f"{paper_key} does not exist. Please try again.")
            exit(0)

        print(f"Editing {self.papers[paper_key]['name']}.")

        new_paper_key = input("Enter a new key for the paper, or leave blank to retain: ")
        
        if new_paper_key != '':
            self.papers[new_paper_key] = self.papers[paper_key]
            del self.papers[paper_key]

        else :
            new_paper_key = paper_key

        new_paper_name = input("Enter a new name for the paper, or leave blank to retain: ")

        if new_paper_name != '':
            self.papers[new_paper_key]['name'] = new_paper_name

        else:
            new_paper_name = self.papers[paper_key]['name']

        for day in [i for i in calendar.day_name]:
            sold = input(f"\nIs the newspaper sold on {day}? ([y]es/[N]o) ")

            if sold.lower() in ['y', 'ye', 'yes']:
                sold = int(True)
                cost = float(input(f"What is the cost on {day}? "))

            else:
                sold = int(False)
                cost = 0.0

            self.papers[new_paper_key]['days'][day] = {'sold': sold, 'cost': cost}

        print(f"\n{self.papers[new_paper_key]['name']} has been edited.")

        with open(f"{self.config['root_folder']}/{self.config['papers_data']}", 'w') as papers_file:
            papers_file.write(dumps(self.papers))

    def delete_existing_paper(self):
        paper_key = input("Enter the key of the paper to delete: ")

        if paper_key not in self.papers:
            print(f"{paper_key} does not exist. Please try again.")
            exit(0)

        sure = input(f"Are you sure you want to delete {self.papers[paper_key]['name']}? ([y]es/[N]o) ")

        if sure.lower() in ['y', 'ye', 'yes']:
            del self.papers[paper_key]

            print(f"\n{self.papers[paper_key]['name']} has been deleted.")

            with open(f"{self.config['root_folder']}/{self.config['papers_data']}", 'w') as papers_file:
                papers_file.write(dumps(self.papers))

        else:
            print("\nDeletion cancelled.")

    def prepare_dated_data(self) -> list:
        if f"{self.month}/{self.year}" not in self.undelivered_strings:
            self.undelivered_strings[f"{self.month}/{self.year}"] = {}

        for paper_key in self.papers:
            if paper_key not in self.undelivered_strings[f"{self.month}/{self.year}"]:
                self.undelivered_strings[f"{self.month}/{self.year}"][paper_key] = []

        return self.get_list_of_all_dates()

    def get_list_of_all_dates(self):
        self.dates_in_active_month = []

        for date_number in range(calendar.monthrange(self.year, self.month)[1]):
            date = datetime.date(self.year, self.month, date_number + 1)
            self.dates_in_active_month.append(date)

        return self.dates_in_active_month

    def get_previous_month(self) -> datetime.date:
        return (datetime.datetime.today().replace(day=1) - datetime.timedelta(days=1)).replace(day=1)

    def acquire_undelivered_papers(self):
        confirmation = input("\nDo you want to report any undelivered data? ([Y]es/[n]o) ")

        while confirmation.lower() in ['y', 'ye,' 'yes']:
            print("These are the available newspapers:\n")

            for paper_key, value in self.papers.items():
                print(f"\t{paper_key}: {value['name']}")

            print("\tall: ALL NEWSPAPERS\n")

            paper_key = input("Please enter the key of the newspaper you want to report, or press Return to cancel: ")

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
            string = input(f"Please tell us when {paper_key} was undelivered, or enter '?' for help: ").strip()

            if string == '?' or string == '':
                os.system('includes/undelivered_help.pdf')

            else:
                self.undelivered_strings[f"{self.month}/{self.year}"][paper_key].append(string)

                finished = True

    def parse_undelivered_string(self, string: str) -> list:
        undelivered_dates = []
        durations = string.split(',')

        for duration in durations:
            if duration.isdigit():
                day = int(duration)
                
                if day > 0:
                    undelivered_dates.append(datetime.date(self.year, self.month, day))

            elif '-' in duration:
                start, end = duration.split('-')

                if start.isdigit() and end.isdigit():
                    start = int(start)
                    end = int(end)

                    if start > 0 and end > 0:
                        for day in range(start, end + 1):
                            undelivered_dates.append(datetime.date(self.year, self.month, day))

            elif duration[:-1] in calendar.day_name:
                day_number = calendar.day_name.index(duration[:-1]) + 1

                for date in self.dates_in_active_month:
                    if date.weekday() == day_number:
                        undelivered_dates.append(date)

            elif duration == 'all':
                undelivered_dates = self.dates_in_active_month

        return undelivered_dates

    def undelivered_strings_to_dates(self):
        for paper_key in self.undelivered_strings[f"{self.month}/{self.year}"]:
            for string in self.undelivered_strings[f"{self.month}/{self.year}"][paper_key]:
                undelivered_dates = self.parse_undelivered_string(string)

                for date in undelivered_dates:
                    if date not in self.undelivered_dates[paper_key]:
                        self.undelivered_dates[paper_key].append(date)

    def calculate_one_paper(self, paper_key: str) -> float:
        self.totals[paper_key] = 0.0

        for date in self.dates_in_active_month:
            week_day_name = calendar.day_name[date.weekday()]

            if (date not in self.undelivered_dates[paper_key]) and (int(self.papers[paper_key]['days'][week_day_name]['sold']) != 0):

                self.totals[paper_key] += float(self.papers[paper_key]['days'][week_day_name]['cost'])

        return self.totals[paper_key]

    def calculate_all_papers(self):
        self.totals['TOTAL'] = 0.0

        for paper_key in self.papers:
            self.totals['TOTAL'] += self.calculate_one_paper(paper_key)

    def format_and_copy(self):
        string = ""

        string += f"*TOTAL: {self.totals.pop('TOTAL')}*\n"

        for paper_key, value in self.totals.items():
            string += f"{self.papers[paper_key]['name']}: {value}\n"

        print(string)

        if not self.args.nocopy:
            copy_to_clipboard(string)

    def save_results(self):
        if not self.args.nolog:
            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
            current_month = datetime.date(self.year, self.month, 1).strftime("%m/%Y")

            total = 0.0

            for paper_key, value in self.totals.items():
                if len(self.undelivered_dates[paper_key]) > 0:
                
                    delivery_record = ""

                    for date in self.undelivered_dates[paper_key]:
                        delivery_record += f",{date.day}"

                    delivery_record = f"{timestamp},{current_month},{self.papers[paper_key]['name']}{delivery_record}"
                    with open(f"{self.config['root_folder']}/{self.config['delivery_record_file']}", 'a') as delivery_record_file:
                        delivery_record_file.write(delivery_record + "\n")

                cost_record = f"{timestamp},{current_month},{self.papers[paper_key]['name']},{self.totals[paper_key]}"


                with open(f"{self.config['root_folder']}/{self.config['cost_record_file']}", 'a') as cost_record_file:
                    cost_record_file.write(cost_record + "\n")

                total += self.totals[paper_key]

            with open(f"{self.config['root_folder']}/{self.config['cost_record_file']}", 'a') as cost_record_file:
                cost_record_file.write(f"{timestamp},{current_month},TOTAL,{total}\n")

    def calculate(self):
        self.undelivered_strings_to_dates()
        self.calculate_all_papers()
        self.format_and_copy()
        self.save_results()

    def addudl(self):
        with open(f"{self.config['root_folder']}/{self.config['undelivered_strings']}", 'w') as undelivered_file:
            undelivered_file.write(dumps(self.undelivered_strings))

    def edit_config_files(self):
        pass

def main():
    main = Main()
    main.run()

if __name__ == '__main__':
    main()

import calendar
import datetime
from getopt import getopt
from json import loads, dumps
from re import split as re_split
import sys
from pyperclip import copy
import os
from pathlib import Path

class Main:
    month = 0
    year = 0
    totals = {'TOTAL': 0.0}
    undelivered_dates = {}
    undelivered_strings = {}
    nolog = False
    nocopy = False

    def __init__(self):
        os.chdir(sys._MEIPASS)

        with open(f"config.json", 'r') as config_file:
            self.config = loads(config_file.read())

        if self.config['root_folder'] == 'UNSET':
            self.config['root_folder'] = f"{str(Path.home())}/.npbc"

            with open(f"config.json", 'w') as config_file:
                config_file.write(dumps(self.config))

        with open(f"{self.config['root_folder']}/{self.config['papers_data']}", 'r') as papers_file:
            self.papers = loads(papers_file.read())

        with open(f"{self.config['root_folder']}/{self.config['undelivered_strings']}", 'r') as undelivered_file:
            self.undelivered_strings = loads(undelivered_file.read())

        with open(f"help.json", 'r') as help_file:
            self.help = loads(help_file.read())

        for key, value in self.papers.items():
            self.undelivered_dates[key] = []
            self.undelivered_strings[key] = []
            self.totals[key] = 0.0

    def check_arguments(self):
        self.argument_list = sys.argv[1:]

        if len(self.argument_list) == 0:
            self.run_ui()

        elif len(self.argument_list) >= 1:
            if self.argument_list[0] == 'calculate':
                self.read_args_for_calculate()
                self.calculate()

            elif (self.argument_list[0] == '--help') or (self.argument_list[0] == '-h'):
                self.display_help()

            elif self.argument_list[0] == 'editpapers':
                self.edit_papers()

            elif self.argument_list[0] == 'addudl':
                self.read_args_for_undelivered_dates()
                self.add_undelivered_dates()

            else:
                self.display_help()

    def display_help(self):
        print(self.help['main'])

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

    def add_undelivered_dates(self):
        if len(self.argument_list) <= 1:
            print("\nPlease enter the dates you want to add to the undelivered dates list.")
            
            self.acquire_undelivered_papers()

        with open(f"{self.config['root_folder']}/{self.config['undelivered_strings']}", 'w') as undelivered_file:
            undelivered_file.write(dumps(self.undelivered_strings))

    def read_args_for_undelivered_dates(self):
        argument_list = self.argument_list[1:]
        options = "m:y:p:"
        long_options = ["month", "year", "papers"]
        arguments, values = getopt(argument_list, options, long_options)

        undelivered_string = ''

        for argument, value in arguments:
            if argument in ['-m', '--month']:
                self.month = int(value)

            elif argument in ['-y', '--year']:
                self.year = int(value)

            elif argument in ['-p', '--papers']:
                undelivered_string = value

        if self.month == 0 and self.year == 0:
            self.month = self.get_previous_month().month
            self.year = self.get_previous_month().year

        elif self.month == 0 and self.year != 0:
            self.month = datetime.datetime.today().month

        elif self.month != 0 and self.year == 0:
            self.year = datetime.datetime.today().year

        self.get_list_of_dates()

        if len(undelivered_string.split()) > 0:
            for paper in undelivered_string.split(';'):
                paper_key, string = paper.split(':')

                self.undelivered_strings[paper_key] = string

    def read_args_for_calculate(self):
        argument_list = self.argument_list[1:]
        options = "m:y:p:l:c:"
        long_options = ["month", "year", "papers", "nolog", "nocopy"]
        arguments, values = getopt(argument_list, options, long_options)

        undelivered_string = ''

        for argument, value in arguments:
            if argument in ['-m', '--month']:
                self.month = int(value)

            elif argument in ['-y', '--year']:
                self.year = int(value)

            elif argument in ['-p', '--papers']:
                undelivered_string = value

            elif argument in ['-l', '--nolog']:
                self.nolog = True

            elif argument in ['-c', '--nocopy']:
                self.nocopy = True

        
        if self.month == 0 and self.year == 0:
            self.month = self.get_previous_month().month
            self.year = self.get_previous_month().year

        elif self.month == 0 and self.year != 0:
            self.month = datetime.datetime.today().month

        elif self.month != 0 and self.year == 0:
            self.year = datetime.datetime.today().year

        self.get_list_of_dates()

        if len(undelivered_string.split()) > 0:
            for paper in undelivered_string.split(';'):
                paper_key, string = paper.split(':')

                self.assign_parsed_undelivered_to_paper(paper_key, self.parse_undelivered_string([], string), string)

    def get_list_of_dates(self) -> list:
        self.dates_in_active_month = []

        for date_number in range(calendar.monthrange(self.year, self.month)[1]):
            date = datetime.date(self.year, self.month, date_number + 1)
            self.dates_in_active_month.append(date)

        return self.dates_in_active_month

    def get_previous_month(self) -> datetime.date:
        return (datetime.datetime.today().replace(day=1) - datetime.timedelta(days=1)).replace(day=1)

    def calculate_one_paper(self, paper_key: str) -> float:
        self.totals[paper_key] = 0.0

        for date in self.dates_in_active_month:
            self.totals[paper_key] += (float(self.papers[paper_key]['days'][calendar.day_name[date.weekday()]]['cost']) * int(
                self.papers[paper_key]['days'][calendar.day_name[date.weekday()]]['sold'])) if date not in self.undelivered_dates[paper_key] else 0.0

        return self.totals[paper_key]


    def calculate_all_papers(self):
        self.totals['TOTAL'] = 0.0

        for paper_key in self.papers:
            self.totals['TOTAL'] += self.calculate_one_paper(paper_key)

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
        undelivered_dates = []
        string = ''

        while not finished:
            string = input(
                f"Please tell us when {paper_key} was undelivered, or enter '?' for help: ").strip()

            if string == '?' or string == '':
                os.system('undelivered_help.pdf')

            else:
                undelivered_dates = self.parse_undelivered_string(undelivered_dates, string)

                finished = True

        self.assign_parsed_undelivered_to_paper(paper_key, undelivered_dates, string)

    def assign_parsed_undelivered_to_paper(self, paper_key, undelivered_dates, string):
        if paper_key == 'all':
            for paper_key in self.papers:
                self.undelivered_dates[paper_key] = undelivered_dates
                self.undelivered_strings[paper_key].append(string)

        else:
            self.undelivered_dates[paper_key] = undelivered_dates
            self.undelivered_strings[paper_key].append(string)

    def edit_config_files(self):
        pass

    def parse_undelivered_string(self, undelivered_dates: list, string: str) -> list:
        durations = string.split(',')

        for duration in durations:
            if duration.isdigit():
                duration = int(duration)

                if duration > 0:
                    undelivered_dates.append(datetime.date(
                                self.year, self.month, duration))

            elif duration == 'all':
                undelivered_dates = self.dates_in_active_month

            elif '-' in duration:
                start, end = duration.split('-')

                if start.isdigit() and end.isdigit():
                    start = int(start)
                    end = int(end)

                    if start > 0 and end > 0:
                        for date in range(start, end + 1):
                            undelivered_dates.append(
                                        datetime.date(self.year, self.month, date))

            elif duration[:-1] in calendar.day_name:
                day_number = [i for i in calendar.day_name].index(duration[:-1])

                for date in self.dates_in_active_month:
                    if date.weekday() == day_number:
                        undelivered_dates.append(date)
            
                                
        return undelivered_dates

    def output_and_copy_results(self):
        output_string = ""

        output_string += f"*TOTAL: {self.totals.pop('TOTAL')}*\n"

        for paper_key, value in self.totals.items():
            output_string += f"{self.papers[paper_key]['name']}: {value}\n"

        print(f"\n{output_string}")
        if not self.nocopy:
            copy(output_string)

    def save_results(self):
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
 

    def remove_duplicate_dates(self):
        for paper_key, value in self.undelivered_dates.items():
            self.undelivered_dates[paper_key] = list(set(self.undelivered_dates[paper_key]))
            self.undelivered_dates[paper_key].sort()           


    def calculate(self):
        self.remove_duplicate_dates()
        self.calculate_all_papers()
        self.output_and_copy_results()

        if not self.nolog:
            self.save_results()

    def run_ui(self):
        task = input("What do you want to do right now? ([c]alculate, edit the [p]apers, edit the [f]iles configuration, add [u]ndelivered data, display [h]elp, or e[x]it) ").strip().lower()

        if task in ['c', 'calculate']:
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

            self.get_list_of_dates()
            self.acquire_undelivered_papers()
            self.calculate()

        elif task in ['p', 'papers']:
            self.edit_papers()

        elif task in ['h', 'help']:
            self.display_help()

        elif task in ['f', 'files']:
            self.edit_config_files()

        elif task in ['u', 'undelivered']:
            self.add_undelivered_dates()

        elif task in ['x', 'exit']:
            pass

        else:
            self.display_help()

    def run(self):
        self.check_arguments()


def main():
    main = Main()
    main.run()


if __name__ == '__main__':
    main()

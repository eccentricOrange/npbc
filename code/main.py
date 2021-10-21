from json import loads
from sys import argv
from getopt import getopt
from re import split as re_split
from pyperclip import copy

import datetime
import calendar


class Main:
    month = 0
    year = 0
    totals = {'TOTAL': 0.0}
    undelivered_dates = {}
    undelivered_strings = {}

    def __init__(self):
        with open(f"data/config.json", 'r') as config_file:
            self.config = loads(config_file.read())

        with open(f"{self.config['papers_data']}", 'r') as papers_file:
            self.papers = loads(papers_file.read())

        with open(f"code/help.json", 'r') as help_file:
            self.help = loads(help_file.read())

        for key, value in self.papers.items():
            self.undelivered_dates[key] = []
            self.undelivered_strings[key] = []
            self.totals[key] = 0.0

    def check_arguments(self):
        self.argument_list = argv[1:]

        if len(self.argument_list) == 0:
            self.run_ui()

        elif len(self.argument_list) >= 1:
            if self.argument_list[0] == 'calculate':
                self.read_args_for_calculate()
                self.calculate()

            elif (self.argument_list[0] == '--help') or (self.argument_list[0] == '-h'):
                self.display_help()

            # elif self.argument_list[0] == 'editpapers':
            #     self.edit_papers()

            # elif self.argument_list[0] == 'editconfig':
            #     self.edit_config()

            else:
                self.display_help()

    def display_help(self):
        print(self.help['main'])

    

    def read_args_for_calculate(self):
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
            "Do you want to report any undelivered data? ([Y]es/[n]o) ")

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
                print(self.help['undelivered_dates'])

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

    def parse_undelivered_string(self, undelivered_dates: list, string: str) -> list:
        durations = re_split(r', | ', string)

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
                                
        return undelivered_dates

    def output_and_copy_results(self):
        output_string = ""

        output_string += f"*TOTAL: {self.totals.pop('TOTAL')}*\n"

        for paper_key, value in self.totals.items():
            output_string += f"{self.papers[paper_key]['name']}: {value}\n"

        print(f"\n{output_string}")
        copy(output_string)

    def save_results(self):
        pass

    def calculate(self):
        self.get_list_of_dates()
        self.calculate_all_papers()
        self.output_and_copy_results()
        self.save_results()

    def run_ui(self):
        task = input("What do you want to do right now? ([c]alculate, edit the [p]apers, edit the [f]iles configuration, display [h]elp, or e[x]it) ").strip().lower()

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

            self.acquire_undelivered_papers()
            self.calculate()

        # elif task in ['p', 'papers']:
        #     self.edit_papers()

        # elif task in ['f', 'files']:
        #     self.edit_config()

        elif task in ['h', 'help']:
            self.display_help()

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

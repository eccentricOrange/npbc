import calendar
import datetime
from json import dumps, loads
from pathlib import Path


CONFIG_FILEPATH = Path(Path.home()) / '.npbc' / 'config.json'
# CONFIG_FILEPATH = Path('data') / 'config.json'
HELP_FILEPATH = Path(f'includes/undelivered_help.pdf')

class NPBC_core():
    month = 0
    year = 0
    totals = {'TOTAL': 0.0}
    undelivered_dates = {}

    def load_files(self):
        with open(CONFIG_FILEPATH, 'r') as config_file:
            self.config = loads(config_file.read())

        if self.config['root_folder'] == 'UNSET':
            self.config['root_folder'] = f"{str(Path.home())}/.npbc"

            with open(CONFIG_FILEPATH, 'w') as config_file:
                config_file.write(dumps(self.config))

        self.define_file_structure()

        with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'r') as papers_file:
            self.papers = loads(papers_file.read())

        with open(Path(f"{self.config['root_folder']}/{self.config['undelivered_strings']}"), 'r') as undelivered_file:
            self.undelivered_strings = loads(undelivered_file.read())

        for paper_key in self.papers:
            self.totals[paper_key] = 0.0
            self.undelivered_dates[paper_key] = []

    def define_file_structure(self):
        Path(f"{self.config['root_folder']}").mkdir(parents=True, exist_ok=True)
        Path(f"{self.config['root_folder']}/{self.config['papers_data']}").touch(exist_ok=True)
        Path(f"{self.config['root_folder']}/{self.config['undelivered_strings']}").touch(exist_ok=True)
        Path(f"{self.config['root_folder']}/{self.config['cost_record_file']}").touch(exist_ok=True)
        Path(f"{self.config['root_folder']}/{self.config['delivery_record_file']}").touch(exist_ok=True)

    def prepare_dated_data(self) -> list:
        if f"{self.month}/{self.year}" not in self.undelivered_strings:
            self.undelivered_strings[f"{self.month}/{self.year}"] = {}

        for paper_key in self.papers:
            if paper_key not in self.undelivered_strings[f"{self.month}/{self.year}"]:
                self.undelivered_strings[f"{self.month}/{self.year}"][paper_key] = []

        if "all" not in self.undelivered_strings[f"{self.month}/{self.year}"]:
            self.undelivered_strings[f"{self.month}/{self.year}"]["all"] = []

        return self.get_list_of_all_dates()

    def get_list_of_all_dates(self):
        self.dates_in_active_month = []

        for date_number in range(calendar.monthrange(self.year, self.month)[1]):
            date = datetime.date(self.year, self.month, date_number + 1)
            self.dates_in_active_month.append(date)

        return self.dates_in_active_month

    def get_previous_month(self) -> datetime.date:
        return (datetime.datetime.today().replace(day=1) - datetime.timedelta(days=1)).replace(day=1)

    def create_new_paper(self, paper_key: str,paper_name: str,  paper_days: dict):
        self.papers[paper_key] = {'name': paper_name,
                                  'key': paper_key, 'days': paper_days}

        with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
            papers_file.write(dumps(self.papers))

    def edit_existing_paper(self, paper_key: str, name: str, days: dict):
        self.papers[paper_key] = {'name': name,
                            'key': paper_key, 'days': days}

        with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
            papers_file.write(dumps(self.papers))

    def delete_existing_paper(self, paper_key: str):
        print(f"{self.config['root_folder']}/{self.config['papers_data']}")
        del self.papers[paper_key]
        with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
            papers_file.write(dumps(self.papers))

    def parse_undelivered_string(self, string: str) -> list:
        undelivered_dates = []
        durations = string.split(',')

        for duration in durations:
            if duration.isdigit():
                day = int(duration)

                if day > 0:
                    undelivered_dates.append(
                        datetime.date(self.year, self.month, day))

            elif '-' in duration:
                start, end = duration.split('-')

                if start.isdigit() and end.isdigit():
                    start = int(start)
                    end = int(end)

                    if start > 0 and end > 0:
                        for day in range(start, end + 1):
                            undelivered_dates.append(
                                datetime.date(self.year, self.month, day))

            elif duration[:-1] in calendar.day_name:
                day_number = list(calendar.day_name).index(duration[:-1]) + 1

                for date in self.dates_in_active_month:
                    if date.weekday() == day_number:
                        undelivered_dates.append(date)

            elif duration == 'all':
                undelivered_dates = self.dates_in_active_month

        return undelivered_dates

    def undelivered_strings_to_dates(self):
        all_papers_strings = self.undelivered_strings[f"{self.month}/{self.year}"].pop(
            'all')
        dates_of_no_paper = []

        for all_papers_string in all_papers_strings:
            dates_of_no_paper += self.parse_undelivered_string(
                all_papers_string)

        for date in dates_of_no_paper:
            for paper_key in self.papers:
                if date not in self.undelivered_dates[paper_key]:
                    self.undelivered_dates[paper_key].append(date)

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

                self.totals[paper_key] += float(self.papers[paper_key]
                                                ['days'][week_day_name]['cost'])

        return self.totals[paper_key]

    def calculate_all_papers(self):
        self.totals['TOTAL'] = 0.0

        for paper_key in self.papers:
            self.totals['TOTAL'] += self.calculate_one_paper(paper_key)

    def save_results(self):
        timestamp = datetime.datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
        current_month = datetime.date(
            self.year, self.month, 1).strftime("%m/%Y")

        total = 0.0

        for paper_key, value in self.totals.items():
            if len(self.undelivered_dates[paper_key]) > 0:

                delivery_record = ""

                for date in self.undelivered_dates[paper_key]:
                    delivery_record += f",{date.day}"

                delivery_record = f"{timestamp},{current_month},{self.papers[paper_key]['name']}{delivery_record}"
                with open(Path(f"{self.config['root_folder']}/{self.config['delivery_record_file']}"), 'a') as delivery_record_file:
                    delivery_record_file.write(delivery_record + "\n")

            cost_record = f"{timestamp},{current_month},{self.papers[paper_key]['name']},{self.totals[paper_key]}"

            with open(Path(f"{self.config['root_folder']}/{self.config['cost_record_file']}"), 'a') as cost_record_file:
                cost_record_file.write(cost_record + "\n")

            total += self.totals[paper_key]

        with open(Path(f"{self.config['root_folder']}/{self.config['cost_record_file']}"), 'a') as cost_record_file:
            cost_record_file.write(
                f"{timestamp},{current_month},TOTAL,{total}\n")

    def calculate(self):
        self.undelivered_strings_to_dates()
        self.calculate_all_papers()
        self.save_results()

    def addudl(self):
        with open(Path(f"{self.config['root_folder']}/{self.config['undelivered_strings']}"), 'w') as undelivered_file:
            undelivered_file.write(dumps(self.undelivered_strings))

    def deludl(self):
        del self.undelivered_strings[f"{self.month}/{self.year}"]

        with open(Path(f"{self.config['root_folder']}/{self.config['undelivered_strings']}"), 'w') as undelivered_file:
            undelivered_file.write(dumps(self.undelivered_strings))

    def update(self):
        pass
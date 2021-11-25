from calendar import day_name as weekday_names
from calendar import monthrange
from datetime import date as date_type
from datetime import datetime, timedelta
from json import dumps, loads
from pathlib import Path

# CONFIG_FILEPATH = Path('data') / 'config.json'
CONFIG_FILEPATH = Path.home() / '.npbc' / 'config.json'

class NPBC_core():

    month = 0
    year = 0
    totals = {'TOTAL': 0.0}
    undelivered_dates = {}

    def load_files(self) -> None:
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

    def define_file_structure(self) -> None:
        Path(f"{self.config['records_folder']}").mkdir(
            parents=True, exist_ok=True)
        Path(
            f"{self.config['root_folder']}/{self.config['papers_data']}").touch(exist_ok=True)
        Path(
            f"{self.config['root_folder']}/{self.config['undelivered_strings']}").touch(exist_ok=True)
        Path(
            f"{self.config['root_folder']}/{self.config['cost_record_file']}").touch(exist_ok=True)
        Path(
            f"{self.config['root_folder']}/{self.config['delivery_record_file']}").touch(exist_ok=True)

    def prepare_dated_data(self) -> list:

        if f"{self.month}/{self.year}" not in self.undelivered_strings:
            self.undelivered_strings[f"{self.month}/{self.year}"] = {}

        for paper_key in self.papers:
            if paper_key not in self.undelivered_strings[f"{self.month}/{self.year}"]:
                self.undelivered_strings[f"{self.month}/{self.year}"][paper_key] = []

        if "all" not in self.undelivered_strings[f"{self.month}/{self.year}"]:
            self.undelivered_strings[f"{self.month}/{self.year}"]["all"] = []

        return self.get_list_of_all_dates()

    def get_list_of_all_dates(self) -> list:

        self.dates_in_active_month = []

        for date_number in range(monthrange(self.year, self.month)[1]):
            date = date_type(self.year, self.month, date_number + 1)
            self.dates_in_active_month.append(date)

        return self.dates_in_active_month

    def get_previous_month(self) -> date_type:

        return (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1)

    def decode_days_and_cost(self, encoded_days: str, encoded_prices: str) -> dict:
        sold = [int(i == 'Y') for i in str(encoded_days).upper()]
        prices = encoded_prices.split(';')

        days = {}
        prices = [float(price) for price in prices if float(price) != 0.0]

        delivered_count = -1

        for day in range(7):
            delivered = sold[day]
            delivered_count += delivered
            
            day_name = weekday_names[day]
            days[day_name] = {}

            days[day_name]['cost'] = prices[delivered_count] if delivered else 0
            days[day_name]['sold'] = delivered

        return days

    def create_new_paper(self, paper_key: str, paper_name: str,  paper_days: dict) -> None:

        self.papers[paper_key] = {
            'name': paper_name,
            'key': paper_key,
            'days': paper_days
        }

        with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
            papers_file.write(dumps(self.papers))

    def edit_existing_paper(self, paper_key: str, paper_name: str, days: dict) -> None:

        if paper_key in self.papers:

            self.papers[paper_key] = {
                'name': paper_name,
                'days': days
            }

            with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
                papers_file.write(dumps(self.papers))

        else:

            print(f"\n{paper_name} does not exist, please create it.")

    def delete_existing_paper(self, paper_key: str) -> None:

        if paper_key in self.papers:

            del self.papers[paper_key]

            with open(Path(f"{self.config['root_folder']}/{self.config['papers_data']}"), 'w') as papers_file:
                papers_file.write(dumps(self.papers))

        else:

            print(f"\nPaper with key {paper_key} does not exist, please create it.")

    def edit_config_file(self, files: dict) -> bool:
        found = False

        for key, path in files.items():
            if key in self.config:
                self.config[key] = path
                found = True

        with open(CONFIG_FILEPATH, 'w') as config_file:
            config_file.write(dumps(self.config))

        return found


    def parse_undelivered_string(self, string: str) -> list:
        undelivered_dates = []
        durations = string.split(',')

        for duration in durations:
            duration = f"{duration[0].upper()}{duration[1:].lower()}"

            if duration.isdigit():
                day = int(duration)

                if day > 0:
                    undelivered_dates.append(
                        date_type(self.year, self.month, day))

            elif '-' in duration:
                start, end = duration.split('-')
                start = f"{start[0].upper()}{start[1:].lower()}"

                if start.isdigit() and end.isdigit():
                    start_date = int(start)
                    end_date = int(end)

                    if start_date > 0 and end_date > 0:
                        for day in range(start_date, end_date + 1):
                            undelivered_dates.append(
                                date_type(self.year, self.month, day))

                elif (start in weekday_names) and end.isdigit():
                    print(start)
                    all_dates_with_matching_name = [i for i in self.dates_in_active_month if list(
                        weekday_names)[i.weekday()] == start]
                    undelivered_dates.append(
                        all_dates_with_matching_name[int(end) - 1])

            elif duration[:-1] in list(weekday_names):
                day_number = list(weekday_names).index(duration[:-1]) + 1

                for date in self.dates_in_active_month:
                    if date.weekday() == day_number:
                        undelivered_dates.append(date)

            elif duration == 'all':
                undelivered_dates = self.dates_in_active_month

        return undelivered_dates

    def undelivered_strings_to_dates(self) -> None:
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
            week_day_name = weekday_names[date.weekday()]

            if (date not in self.undelivered_dates[paper_key]) and (int(self.papers[paper_key]['days'][week_day_name]['sold']) != 0):
                self.totals[paper_key] += float(self.papers[paper_key]
                                                ['days'][week_day_name]['cost'])

        return self.totals[paper_key]

    def calculate_all_papers(self) -> None:
        self.totals['TOTAL'] = 0.0

        for paper_key in self.papers:
            self.totals['TOTAL'] += self.calculate_one_paper(paper_key)

    def save_results(self) -> None:
        timestamp = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
        current_month = date_type(self.year, self.month, 1).strftime("%m/%Y")

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

    def format(self) -> str:
        string = f"For {datetime(self.year, self.month, 1):%B %Y}\n\n"
        string += f"*TOTAL: {self.totals.pop('TOTAL')}*\n"

        for paper_key, value in self.totals.items():
            string += f"{self.papers[paper_key]['name']}: {value}\n"

        return string

    def calculate(self) -> None:
        self.undelivered_strings_to_dates()
        self.calculate_all_papers()
        self.save_results()

    def addudl(self) -> None:
        with open(Path(f"{self.config['root_folder']}/{self.config['undelivered_strings']}"), 'w') as undelivered_file:
            undelivered_file.write(dumps(self.undelivered_strings))

    def deludl(self) -> None:
        del self.undelivered_strings[f"{self.month}/{self.year}"]

        with open(Path(f"{self.config['root_folder']}/{self.config['undelivered_strings']}"), 'w') as undelivered_file:
            undelivered_file.write(dumps(self.undelivered_strings))

    def get_papers(self) -> None:
        return self.papers

    def update(self) -> None:
        pass

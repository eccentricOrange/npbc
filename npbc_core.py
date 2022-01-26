from sqlite3 import connect
from calendar import day_name as weekday_names_iterable
from calendar import monthrange, monthcalendar
from datetime import date as date_type, datetime, timedelta
from pathlib import Path


# DB_DIR = Path('data')
DB_DIR = Path.home() / '.npbc'
DB_PATH = DB_DIR / 'npbc.db'
SCHEMA_PATH = Path(__file__) / 'schema.sql'

weekday_names = list(weekday_names_iterable)

class NPBC_core():

    month = 0
    year = 0
    totals = {'0': 0.0}
    undelivered_dates = {}

    def __init__(self):
        self.define_schema()

    def __del__(self):
        self.connection.close()

    def define_schema(self):
        Path(DB_DIR).mkdir(parents=True, exist_ok=True)
        Path(DB_PATH).touch(exist_ok=True)

        self.connection = connect(DB_PATH)

        with open(SCHEMA_PATH, 'r') as schema_file:
            self.connection.executescript(schema_file.read())
            self.connection.commit()
        
        self.connection.close()
        del self.connection

        self.connection = connect(DB_PATH)

    def get_undelivered_strings(self) -> dict:
        undelivered_strings_list = self.connection.execute("SELECT paper_id, string FROM undelivered_strings WHERE  year = ? AND month = ?;", (self.year, self.month)).fetchall()

        self.undelivered_strings = {str(i[0]): i[1] for i in undelivered_strings_list}

        return self.undelivered_strings

    def get_undelivered_dates(self) -> dict:
        undeliver_dates_list = self.connection.execute("SELECT paper_id, string FROM undelivered_dates WHERE year = ? AND month = ?;", (self.year, self.month)).fetchall()

        undelivered_dates = {str(i[0]): self.parse_undelivered_string(i[1]) for i in undeliver_dates_list}

        return undelivered_dates

    def get_number_of_weekdays(self) -> list:
        self.main_calendar = monthcalendar(self.year, self.month)
        number_of_weeks = len(self.main_calendar)
        self.number_of_weekdays = []

        for i in range(7):
            number_of_weekday = number_of_weeks

            if self.main_calendar[0][i] == 0:
                number_of_weekday -= 1
            
            if self.main_calendar[-1][i] == 0:
                number_of_weekday -= 1

            self.number_of_weekdays.append(number_of_weekday)

        return self.number_of_weekdays

    def get_previous_month(self) -> date_type:
        return (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=1)

    def parse_undelivered_string(self, string: str) -> set:
        undelivered_dates = set([])

        if len(string) > 0:
            durations = string.split(',')
            
            for duration in durations:
                if len(duration) > 0:

                    duration = f"{duration[0].upper()}{duration[1:].lower()}"

                    if duration.isdigit():
                        day = int(duration)

                        if day > 0:
                            undelivered_dates.add(day)

                    elif '-' in duration:
                        start, end = duration.split('-')
                        start = f"{start[0].upper()}{start[1:].lower()}"

                        if start.isdigit() and end.isdigit():
                            start_date = int(start)
                            end_date = int(end)

                            if 0 < start_date <= end_date <= 31:
                                for day in range(start_date, end_date + 1):
                                    undelivered_dates.add(day)

                        elif (start in weekday_names) and end.isdigit():
                            week_number = int(end)
                            day_number = weekday_names.index(start)
                            for week in self.main_calendar:
                                if week[day_number] != 0:
                                    if week_number == 1:
                                        undelivered_dates.add(week[day_number])
                                        break
                                    else:
                                        week_number -= 1

                    elif duration[:-1] in weekday_names:
                        day_number = weekday_names.index(duration[:-1])

                        for week in self.main_calendar:
                            if week[day_number] != 0:
                                undelivered_dates.add(week[day_number])
                        

                    elif duration.lower() == 'all':
                        for day in range(monthrange(self.year, self.month)[1]):
                            undelivered_dates.add(day + 1)

        return undelivered_dates

    def calculate_one_paper(self, paper_id: int, specific_undelivered_string: str, all_undelivered_string: str = None) -> float:
        undelivered_string = specific_undelivered_string

        if all_undelivered_string is not None:
            undelivered_string += ',' + all_undelivered_string

        current_paper_undelivered_dates = self.parse_undelivered_string(undelivered_string)

        if len(current_paper_undelivered_dates) > 0:
            self.undelivered_dates[paper_id] = current_paper_undelivered_dates
        
        weekly_count = self.number_of_weekdays.copy()

        for day in current_paper_undelivered_dates:
            weekly_count[date_type(self.year, self.month, day).weekday()] -= 1

        costs = self.connection.cursor().execute("SELECT day_id, cost FROM papers_days_cost WHERE paper_id = ?;", (paper_id,)).fetchall()
        total_costs = [cost * weekly_count[day_id] for day_id, cost in costs]

        return sum(total_costs)

    def calculate_all_papers(self) -> dict:
        papers = self.connection.cursor().execute("SELECT paper_id FROM papers;").fetchall()

        all_undelivered_strings = None

        if 'all' in self.undelivered_strings:
            all_undelivered_strings = self.undelivered_strings['all']

        for paper_id, in papers:
            cost_of_current_paper = self.calculate_one_paper(paper_id, self.undelivered_strings[str(paper_id)] if str(paper_id) in self.undelivered_strings else '', all_undelivered_string=all_undelivered_strings)
            self.totals[str(paper_id)] = cost_of_current_paper
            self.totals['0'] += cost_of_current_paper

        return self.totals

    def add_undelivered_string(self, paper_id: int, string: str) -> None:
        self.connection.execute("INSERT INTO undelivered_strings (year, month, paper_id, string) VALUES (?, ?, ?, ?);", (self.year, self.month, paper_id, string))
        self.connection.commit()

    def update_undelivered_string(self, paper_id: int, string: str) -> None:
        self.connection.execute("UPDATE undelivered_strings SET string = ? WHERE paper_id = ? AND year = ? AND month = ?;", (string, paper_id, self.year, self.month))
        self.connection.commit()

    def delete_undelivered_string(self, paper_id: int) -> None:
        self.connection.execute("DELETE FROM undelivered_strings WHERE paper_id = ? AND year = ? AND month = ?;", (paper_id, self.year, self.month))
        self.connection.commit()

    def format(self) -> str:
        string = f"For {date_type(self.year, self.month, 1):%B %Y}\n\n"

        string += f"TOTAL: {self.totals.pop('0')}\n"

        
        string += '\n'.join([
            f"{self.connection.cursor().execute('SELECT name FROM papers WHERE paper_id = ?;', (paper_id,)).fetchone()[0]}: {cost}"

            for paper_id, cost in self.totals.items()
        ])

        return string

    def save_results(self) -> None:
        timestamp = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")

        for paper_id, undelivered_dates in self.undelivered_dates.items():
            self.connection.cursor().execute("INSERT INTO undelivered_dates (timestamp, year, month, paper_id, dates) VALUES (?, ?, ?, ?, ?);", (timestamp, self.year, self.month, paper_id, ','.join([str(i) for i in undelivered_dates])))

        self.connection.commit()

    @staticmethod
    def decode_delivered_and_cost(encoded_days: str, encoded_prices: str) -> list:
        sold = [int(i == 'Y') for i in str(encoded_days).upper()]
        prices = [float(price) for price in encoded_prices.split(';') if float(price) > 0]


        delievered_and_costs = []
        delivered_count = -1
        
        for i, delivered in enumerate(sold):
            if delivered == 1:
                delivered_count += 1
                price = prices[delivered_count]

            else:
                price = 0

            delievered_and_costs.append((delivered, price))

        return delievered_and_costs

    def create_new_paper(self, name: str, delivered_and_costs: list):
        paper_id = self.connection.cursor().execute("INSERT INTO papers (name) VALUES (?);", (name,)).lastrowid

        for day_id, (delivered, cost) in enumerate(delivered_and_costs):
            self.connection.cursor().execute("INSERT INTO papers_days_cost (paper_id, day_id, cost) VALUES (?, ?, ?);", (paper_id, day_id, cost))

            self.connection.cursor().execute("INSERT INTO papers_days_delivered (paper_id, day_id, delivered) VALUES (?, ?, ?);", (paper_id, day_id, delivered))

        self.connection.commit()

        return paper_id

    def update_existing_paper(self, paper_id: int, name: str = None, delivered_and_costs: list = None):

        if name:
            self.connection.cursor().execute("UPDATE papers SET name = ? WHERE paper_id = ?;", (name, paper_id))

        if delivered_and_costs:

            for day_id, (delivered, cost) in enumerate(delivered_and_costs):
                self.connection.cursor().execute("UPDATE papers_days_cost SET cost = ? WHERE paper_id = ? AND day_id = ?;", (cost, paper_id, day_id))

                self.connection.cursor().execute("UPDATE papers_days_delivered SET delivered = ? WHERE paper_id = ? AND day_id = ?;", (delivered, paper_id, day_id))

        self.connection.commit()

    def delete_existing_paper(self, paper_id: int):
        self.connection.cursor().execute("DELETE FROM papers WHERE paper_id = ?;", (paper_id,))
        self.connection.cursor().execute("DELETE FROM papers_days_cost WHERE paper_id = ?;", (paper_id,))
        self.connection.cursor().execute("DELETE FROM papers_days_delivered WHERE paper_id = ?;", (paper_id,))
        self.connection.commit()

    def get_all_papers(self) -> dict:
        query = (
            "SELECT papers.paper_id, papers.name, papers_days_cost.day_id, papers_days_cost.cost, papers_days_delivered.delivered "
            "FROM papers "
            "JOIN papers_days_cost ON papers.paper_id = papers_days_cost.paper_id "
            "JOIN papers_days_delivered ON papers.paper_id = papers_days_delivered.paper_id "
            "WHERE papers_days_cost.day_id = papers_days_delivered.day_id "
            "ORDER BY papers.name, papers_days_cost.day_id;"
        )

        data = self.connection.cursor().execute(query).fetchall()
        all_papers = {}

        for paper_id, name, day_id, cost, delivered in data:
            day_name = weekday_names[day_id]
            if str(paper_id) not in all_papers:
                all_papers[str(paper_id)] = {
                    'name': name
                }

            all_papers[str(paper_id)][day_name] = {
                'cost': cost,
                'delivered': delivered
            }

        return all_papers

    def update(self) -> None:
        pass
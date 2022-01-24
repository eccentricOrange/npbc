from sqlite3 import connect
from calendar import day_name as weekday_names
from calendar import monthrange, monthcalendar
from datetime import date as date_type
from datetime import datetime, timedelta
from json import dumps, loads
from pathlib import Path

# DB_DIR = Path.home() / '.npbc'
DB_DIR = Path('data')
DB_PATH = DB_DIR / 'npbc.db'

class NPBC_core():

    month = 0
    year = 0
    totals = {'TOTAL': 0.0}
    undelivered_dates = {}

    def connect_to_db(self):
        self.connection = connect(DB_PATH)

    def disconnect_from_db(self):
        self.connection.close()

    def define_schema(self):
        Path(DB_DIR).mkdir(parents=True, exist_ok=True)
        Path(DB_PATH).touch(exist_ok=True)

        self.connect_to_db()

        with open(DB_DIR / 'npbc.schema', 'r') as schema_file:
            self.connection.executescript(schema_file.read())
            self.connection.commit()

    def get_undelivered_strings(self) -> list:
        self.undelivered_strings = self.connection.execute("SELECT paper_id, string FROM undelivered_strings WHERE  year = ? AND month = ?", (self.month, self.year)).fetchall()

        return self.undelivered_strings

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

    def parse_undelivered_string(self, string: str) -> set:
        durations = string.split(',')
        undelivered_dates = set([])

        for duration in durations:
            duration = f"{duration[0].upper()}{duration[1:].lower()}"

            if duration.isdigit():
                day = int(duration)

                if day > 0:
                    undelivered_dates.add(date_type(self.year, self.month, day))

            elif '-' in duration:
                start, end = duration.split('-')
                start = f"{start[0].upper()}{start[1:].lower()}"

                if start.isdigit() and end.isdigit():
                    start_date = int(start)
                    end_date = int(end)

                    if start_date > 0 and end_date > 0:
                        for day in range(start_date, end_date + 1):
                            undelivered_dates.add(date_type(self.year, self.month, day))

                elif (start in weekday_names) and end.isdigit():
                    week_number = int(end)
                    day_number = weekday_names.index(start)
                    for week in self.main_calendar:
                        if week[day_number] != 0:
                            if week_number == 1:
                                undelivered_dates.add(date_type(self.year, self.month, week[day_number]))
                                break
                            else:
                                week_number -= 1

            elif duration[:-1] in list(weekday_names):
                day_number = list(weekday_names).index(duration[:-1]) + 1

                for week in self.main_calendar:
                    if week[day_number] != 0:
                        undelivered_dates.add(date_type(self.year, self.month, week[day_number]))
                

            elif duration == 'all':
                for day in range(monthrange(self.year, self.month)[1]):
                    undelivered_dates.add(date_type(self.year, self.month, day + 1))

        return undelivered_dates

    

npbc = NPBC_core()
npbc.month = 1
npbc.year = 2022
print(npbc.get_number_of_weekdays())


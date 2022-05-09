CREATE TABLE IF NOT EXISTS papers (
    paper_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    CONSTRAINT unique_paper_name UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS papers_days (
    paper_day_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL REFERENCES papers(paper_id),
    day_id INTEGER NOT NULL,
    CONSTRAINT unique_paper_day UNIQUE (paper_id, day_id)
);

CREATE TABLE IF NOT EXISTS papers_days_delivered (
    papers_days_delivered_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_day_id INTEGER NOT NULL REFERENCES papers_days(paper_day_id),
    delivered INTEGER NOT NULL CHECK (delivered IN (0, 1))
);

CREATE TABLE IF NOT EXISTS papers_days_cost (
    papers_days_cost_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_day_id INTEGER NOT NULL REFERENCES papers_days(paper_day_id),
    cost REAL
);

CREATE TABLE IF NOT EXISTS undelivered_strings (
    string_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL CHECK (year >= 0),
    month INTEGER NOT NULL CHECK (month >= 0 AND month <= 12),
    paper_id INTEGER NOT NULL REFERENCES papers(paper_id),
    string TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL REFERENCES papers(paper_id),
    timestamp TEXT NOT NULL,
    month INTEGER NOT NULL CHECK (month >= 0 AND month <= 12),
    year INTEGER NOT NULL CHECK (year >= 0),
    CONSTRAINT unique_log UNIQUE (timestamp, paper_id, month, year)
);

CREATE TABLE IF NOT EXISTS undelivered_dates_logs (
    undelivered_dates_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id INTEGER NOT NULL REFERENCES logs(log_id),
    date_not_delivered TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cost_logs (
    cost_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id INTEGER NOT NULL REFERENCES logs(log_id),
    cost REAL NOT NULL
);
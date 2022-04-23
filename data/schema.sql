CREATE TABLE IF NOT EXISTS papers (
    paper_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    CONSTRAINT unique_paper_name UNIQUE (name)
);
CREATE TABLE IF NOT EXISTS papers_days_delivered (
    paper_id INTEGER NOT NULL,
    day_id INTEGER NOT NULL,
    delivered INTEGER NOT NULL,
    CONSTRAINT unique_paper_day UNIQUE (paper_id, day_id)
);
CREATE TABLE IF NOT EXISTS papers_days_cost(
    paper_id INTEGER NOT NULL,
    day_id INTEGER NOT NULL,
    cost INTEGER,
    FOREIGN KEY(paper_id) REFERENCES papers(paper_id),
    CONSTRAINT unique_paper_day UNIQUE (paper_id, day_id)
);
CREATE TABLE IF NOT EXISTS undelivered_strings (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    string TEXT NOT NULL,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
);
CREATE TABLE IF NOT EXISTS undelivered_dates (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    dates TEXT NOT NULL,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
);
CREATE INDEX IF NOT EXISTS search_strings ON undelivered_strings(year, month);
CREATE INDEX IF NOT EXISTS paper_names ON papers(name);
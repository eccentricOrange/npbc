INSERT INTO papers (name)
VALUES
    ('paper1'),
    ('paper2'),
    ('paper3');

INSERT INTO cost_and_delivery_data (paper_id, day_id, cost, delivered)
VALUES
    (1, 0, 0.0, 0),
    (1, 1, 6.4, 1),
    (1, 2, 0.0, 0),
    (1, 3, 0.0, 0),
    (1, 4, 0.0, 0),
    (1, 5, 7.9, 1),
    (1, 6, 4.0, 1),
    (2, 0, 0.0, 0),
    (2, 1, 0.0, 0),
    (2, 2, 0.0, 0),
    (2, 3, 0.0, 0),
    (2, 4, 3.4, 1),
    (2, 5, 0.0, 0),
    (2, 6, 8.4, 1),
    (3, 0, 2.4, 1),
    (3, 1, 4.6, 1),
    (3, 2, 0.0, 0),
    (3, 3, 0.0, 0),
    (3, 4, 3.4, 1),
    (3, 5, 4.6, 1),
    (3, 6, 6.0, 1);

INSERT INTO undelivered_strings (year, month, paper_id, string)
VALUES
    (2020, 11, 1, '5'),
    (2020, 11, 1, '6-12'),
    (2020, 11, 2, 'sundays'),
    (2020, 11, 3, '2-tuesday'),
    (2020, 10, 3, 'all');
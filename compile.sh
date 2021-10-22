#!/bin/bash
pyinstaller -F --add-data config.json:. --add-data help.json:. --add-data undelivered_help.pdf:. --distpath bin npbc.py
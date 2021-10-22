#!/bin/bash
pyinstaller -F --add-data includes/config.json:. --add-data includes/help.json:. --add-data includes/undelivered_help.pdf:. --distpath bin npbc.py
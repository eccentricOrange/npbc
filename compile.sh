#!/bin/bash
pyinstaller -F --add-data includes/undelivered_help.pdf:includes --distpath bin npbc.py
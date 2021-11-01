#!/bin/bash
pyinstaller -F --add-data includes/undelivered_help.pdf:includes --distpath bin/executables npbc.py
git add .
git commit -m "linux on x64 compile"
git push origin master
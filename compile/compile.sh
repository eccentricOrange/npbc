#!/bin/bash
git pull
pyinstaller -F --add-data includes/undelivered_help.pdf:includes -n linnpbc --distpath bin/executables npbc.py
git add .
git commit -m "linux on x64 compile"
git pull
git push origin
#!/bin/bash
git pull
pyinstaller -F --add-data includes/undelivered_help.pdf;includes --distpath bin/executables npbc.py
git add .
git commit -m "windows compile"
git pull
git push origin master
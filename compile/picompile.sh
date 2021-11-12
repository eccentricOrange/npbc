#!/bin/bash
git pull
pyinstaller -F --add-data includes/undelivered_help.pdf:includes -n pinpbc --distpath bin/executables npbc.py  --specpath spec
git add .
git commit -m "linux on arm compile"
git pull
git push origin
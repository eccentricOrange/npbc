#!/bin/bash
git pull
pyinstaller -F -n pinpbc_api --distpath bin/executables npbc_api.py --specpath spec
pyinstaller -F -n pinpbc_cli --distpath bin/executables npbc_cli.py --specpath spec
git add .
git commit -m "linux on arm compile"
git pull
git push origin
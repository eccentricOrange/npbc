#!/bin/bash
git pull
python -m nuitka --include-data-file=/home/anujv/pts/npbc/data/schema.sql=schema.sql --onefile --standalone -o bin/executables/npbc_cli npbc_cli.py
python -m nuitka --include-data-file=/home/anujv/pts/npbc/data/schema.sql=schema.sql --onefile --standalone -o bin/executables/npbc_api npbc_api.py
# pyinstaller -F -n npbc_api --distpath bin/executables npbc_api.py --specpath spec
# pyinstaller -F -n npbc_cli --distpath bin/executables npbc_cli.py --specpath spec
git add .
git commit -m "linux on x64 compile"
git pull
git push origin
pyinstaller -F --add-data includes\undelivered_help.pdf;includes --distpath bin/executables npbc.py
git add .
git commit -m %1
git push origin master
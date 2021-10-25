pyinstaller -F --add-data includes\undelivered_help.pdf;includes --distpath bin npbc.py
git add .
git commit -m %1
git push origin master
npbc update
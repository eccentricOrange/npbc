git pull
pyinstaller -F --add-data includes\undelivered_help.pdf;includes -n npbc --distpath bin/executables npbc.py  --specpath spec
git add .
git commit -m "windows compile"
git pull
git push origin
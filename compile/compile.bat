git pull
pyinstaller -F -n npbc --distpath bin/executables npbc.py  --specpath spec
git add .
git commit -m "windows compile"
git pull
git push origin
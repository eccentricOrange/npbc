git pull
pyinstaller -F -n npbc_api --distpath bin/executables npbc_api.py --specpath spec
pyinstaller -F -n npbc_cli --distpath bin/executables npbc_cli.py --specpath spec
git add .
git commit -m "windows compile"
git pull
git push origin
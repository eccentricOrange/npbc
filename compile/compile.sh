#!/bin/bash
git pull
pyinstaller -F -n npbc --distpath bin/executables npbc.py --specpath spec
git add .
git commit -m "linux on x64 compile"
git pull
git push origin
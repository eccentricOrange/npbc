#!/bin/bash

al = 'alias npbc="pyenv shell 3.9.7/envs/npbc-env && python ~/bin/npbc/code/main.py"'

git clone https://github.com/eccentricOrange/npbc.git ~/bin/npbc
cp -r ~/bin/npbc/data ~/.npbc/
echo $al >> ~/.bashrc
eval $al
#!/bin/bash

git clone https://github.com/eccentricOrange/npbc.git ~/bin/npbc
cp -r ~/bin/npbc/data ~/.npbc/
echo 'alias npbc="cd ~/bin/npbc && python code/main.py"' >> ~/.bashrc
alias npbc="cd ~/bin/npbc && python code/main.py"
#!/bin/bash
git clone https://github.com/eccentricOrange/npbc.git ~/bin/npbc
dir=~/.npbc
if [ ! -d "$dir" ]; then
    cp -r ~/bin/npbc/data ~/.npbc/
fi
echo 'alias npbc=~/bin/npbc/bin/npbc' >> ~/.bashrc
alias npbc=~/bin/npbc/bin/npbc

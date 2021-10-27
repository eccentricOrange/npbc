#!/bin/bash
git clone https://github.com/eccentricOrange/npbc.git ~/bin/npbc
dir=~/.npbc
if [ ! -d "$dir" ]; then
    cp -r ~/bin/npbc/data ~/.npbc/
fi
echo 'alias npbc=sh ~/bin/npbc/bin/npbc.sh' >> ~/.bashrc
alias npbc=sh ~/bin/npbc/bin/npbc.sh

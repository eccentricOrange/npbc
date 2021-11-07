#!/bin/bash
git clone https://github.com/eccentricOrange/npbc.git ~/bin/npbc
dir=~/.npbc
if [[ ! -d "$dir" ]]; then
    cp -r ~/bin/npbc/data ~/.npbc/
fi
chmod +x ~/bin/npbc/bin/linnpbc.sh
echo 'alias npbc=~/bin/npbc/bin/linnpbc.sh' >> ~/.bashrc
alias npbc=~/bin/npbc/bin/linnpbc.sh

#!/bin/bash
git clone https://github.com/eccentricOrange/npbc.git ~/bin/npbc
dir=~/.npbc
if [ ! -d "$dir" ]; then
    cp -r ~/bin/npbc/data ~/.npbc/
fi
chmod +x ~/bin/npbc/bin/npbc.sh
echo 'alias npbc=~/bin/npbc/bin/npbc.sh' >> ~/.bashrc
alias npbc=~/bin/npbc/bin/npbc.sh

#!/bin/bash

git clone https://github.com/eccentricOrange/npbc.git /usr/local/npbc
cp -r /usr/local/npbc/data ~/.npbc/
echo 'alias npbc="cd /usr/local/npbc && code/main.py"' >> ~/.bashrc
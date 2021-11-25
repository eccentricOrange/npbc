#!/bin/bash

if [[ $1 == 'update' ]]
then
    git -C ~/bin/npbc pull
else
    ~/bin/npbc/bin/executables/npbc_cli "$@"
fi
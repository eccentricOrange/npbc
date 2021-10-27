#!/bin/bash

if [[ $1 == 'update' ]]
then
    cd ..
    git -C ~/bin/npbc pull
else
    ~/bin/npbc/bin/executables/npbc "$@"
fi
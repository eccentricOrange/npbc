#!/bin/bash

if [[ $1 == 'update' ]]
then
    cd ..
    git -C .. pull
else
    ~/bin/npbc/bin/executables/npbc "$@"
fi
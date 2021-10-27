#!/bin/sh

if [ $1 == 'update']
then
    cd ..
    git -C .. pull
else
    executables/npbc "$@"
fi
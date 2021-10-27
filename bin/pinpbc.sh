#!/bin/sh

if [ $1 == 'update']
then
    cd ..
    git pull
else
    executables/pinpbc "$@"
fi
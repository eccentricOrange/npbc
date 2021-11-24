#!/bin/bash
content=`cat data.json`
echo "'$content'"
curl -i -H "Content-Type: application/json" -X POST -d "$content" http://localhost:5000/npbc/api/addpaper
from json import loads, dumps
from os import listdir

help_dict = {}

files = listdir("experiments/help")

for file in files:
    with open("experiments/help/" + file, "r") as f:
        help_dict[f"{file.split('.')[0]}"] = f.read()

with open(f"includes/help.json", 'w') as f:
    f.write(dumps(help_dict))
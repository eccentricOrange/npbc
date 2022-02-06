# NewsPaper Bill Calculator

This app calculates your monthly newspaper bill.

[![.github/workflows/compile.yml](https://github.com/eccentricOrange/npbc/actions/workflows/compile.yml/badge.svg?branch=master)](https://github.com/eccentricOrange/npbc/actions/workflows/compile.yml)

## Key concepts
1. Each newspaper has a certain cost per day of the week
2. Each newspaper may or may not be delivered on a given day
3. Each newspaper has a name and a short name, called a key
4. You may register any dates when you didn't receive a paper in advance using the `addudl` command
5. Once you calculate, the results are displayed and copied to your clipboard

## Key files

The `~` represents your home directory.

| Location | Name | Purpose |
| -- | -- | -- |
| `~/.npbc` | `papers.json` | holds all newspapers, their names and keys, and all delivery and cost information |
| `~/.npbc` | `undelivered_strings.json` | holds dates when papers weren't delivered |
| `~/.npbc/record-files` | `cost-record.csv` | holds records of each paper' cost from every calculation |
| `~/.npbc/record-files` | `cost-record.csv` | holds records of when any paper wasn't delivered |

## Installation

### Bash shells (most Unix-like systems)

Run the following shell command on x64 or x86 systems.

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/eccentricOrange/npbc/master/install/install.sh)"
```

For an ARM-based systems (like the Raspberry Pi), run the following command.

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/eccentricOrange/npbc/master/install/piinstall.sh)"
```

### Windows
Download and run `install/install.bat` from this repository. You'll have to add the download location (`%APPDATA%\npbc\bin`)to your Windows path. Or do whatever you like to run `npbc.bat` from that path—it's all that matters.
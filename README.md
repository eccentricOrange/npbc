# NewsPaper Bill Calculator

This app calculates your monthly newspaper bill. Requires SQLite>=3.35 (and Python>=3.9 if you intend to develop anything, instead of just using the executables).

[![Test, build and release](https://github.com/eccentricOrange/npbc/actions/workflows/test-build-release.yml/badge.svg)](https://github.com/eccentricOrange/npbc/actions/workflows/test-build-release.yml)

## Key concepts
1. Each newspaper has a certain cost per day of the week
2. Each newspaper may or may not be delivered on a given day
3. Each newspaper has a name, and a number called a key
4. You may register any dates when you didn't receive a paper in advance using the `addudl` command
5. Once you calculate, the results are displayed and logged.

## Installation
1. From [the latest release](https://github.com/eccentricOrange/npbc/releases/latest), download the "updater" file for your operating system in any folder, and make it executable.

    **Recommended locations**, where the CLI will always download.
    | OS | Location |
    | --- | --- |
    | Linux | `~/bin/npbc/npbc` |
    | macOS | `~/Applications/npbc/npbc` |
    | Windows | `~\.npbc\bin\npbc.exe` |

2. Run the following command:

    ```sh
    /path/to/updater update
    ```

3. You can now run `path/to/updater init` to begin.

&nbsp;

Alternatively, just run these scripts. You'll need to have wget installed.

For Linux systems, run:
```bash
mkdir -p ~/bin/npbc
wget https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_updater-linux-x64 -O ~/bin/npbc/npbc
chmod +x ~/bin/npbc/npbc
~/bin/npbc/npbc init
echo "alias npbc=\"~/bin/npbc/npbc\"" >> ~/.bashrc
exec "$SHELL"
```

For macOS systems, run:
```bash
mkdir -p ~/Applications/npbc
wget https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_updater-macos-x64 -O ~/Applications/npbc/npbc
chmod +x ~/Applications/npbc/npbc
~/bin/Applications/npbc init
echo "alias npbc=\"~/Applications/npbc/npbc\"" >> ~/.bashrc
exec "$SHELL"
```

For Windows systems, run the following from PowerShell and add `~\.npbc\bin` to PATH:
```bat
mkdir -p "~\.npbc\bin";
wget https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_updater-windows-x64.exe -O "~\.npbc\bin\npbc.exe";
& "~\.npbc\bin\npbc.exe" init;
```

## Detailed explanations
### What is this?
This application helps you calculate monthly newspaper bills. The goal is to generate a message that I can paste into WhatsApp and send to my newspaper vendor. The end result here is a CLI tool that will be later used as a back-end to build GUIs (hence learn about: C\#, HTML/CSS/JS, Flutter). In its current form, everything will be "compiled" by PyInstaller into one-file stand-alone executables for the end-user using GitHub Actions.

The other important goal was to be a testbed for learning a bunch of new tools: more Python libraries, SQL connectors, GitHub Actions (CI/CD, if I understand correctly), unit tests, CLI libraries, type-hinting, regex. I had [earlier built](https://github.com/eccentricOrange/Newspaper-Bill-Calculator-v2) this on a different platform, so I now have a solid idea of how this application is used.

### What files exist?
(ignoring conventional ones like `README` and `requirements.txt`)

| File | Purpose/Description | Review |
| -- | -- | -- |
| [`npbc_core.py`](/npbc_core.py) | Provide the core functionality: the calculation, parsing and validation of user input, interaction with the DB etc. Later on, some functionality from this will be extracted to create server-side code that can service more users, but I have to learn a lot more before getting there. |
| [`npbc_regex.py`](/npbc_regex.py) | Contains all the regex statements used to validate and parse user input. |
| [`npbc_exceptions.py`](/npbc_regex.py) | Defines classes for all the custom exceptions used by the core and the CLI. |
| [`npbc_cli.py`](/npbc_cli.py) | Import functionality from `npbc_core.py` and wrap a CLI layer on it using `argparse`. Also provide some additional validation. |
| [`npbc_updater.py`](/npbc_updater.py) | Provide a utility to update the application on the user's end.
| [`test_core.py`](/test_core.py) | Test the functionality of the core file (pytest), except anything to do with the database. |
| [`test_db.py`](/test_db.py) | Test the functionality of the core file (pytest), for anything to do with the database. |
| [`test_regex.py`](/test_regex.py) | Test the functionality of the regex statements. |
| [`data/schema.sql`](/data/schema.sql) | Database schema. In my local environment, the [`data`](/data/) folder also has a test database file (but I don't want to upload this online). |
| [`data/test.sql`](/data/test.sql) | SQL statements to generate test data for `test_db.py`. |
| [`test.dockerfile`](/test.dockerfile) | Provide an environment for the PyTest to run, because the project needs SQLite>=3.35, which does not ship with most stable Debian Bullseye or Ubuntu 20 systems. This is available as built image from Docker Hub as [`eccentricorange/npbc:test`](https://hub.docker.com/repository/docker/eccentricorange/npbc). |

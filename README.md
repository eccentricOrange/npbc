# NewsPaper Bill Calculator

This app calculates your monthly newspaper bill.

[![.github/workflows/build.yml](https://github.com/eccentricOrange/npbc/actions/workflows/build.yml/badge.svg)](https://github.com/eccentricOrange/npbc/actions/workflows/build.yml)

## Key concepts
1. Each newspaper has a certain cost per day of the week
2. Each newspaper may or may not be delivered on a given day
3. Each newspaper has a name, and a number called a key
4. You may register any dates when you didn't receive a paper in advance using the `addudl` command
5. Once you calculate, the results are displayed and copied to your clipboard

## Installation
1. From [the latest release](https://github.com/eccentricOrange/npbc/releases/latest), download the "updater" file for your operating system in any folder, and make it executable.

    **Recommended locations**, where the CLI and API will always download.
    | OS | Location |
    | --- | --- |
    | Linux | `~/bin/npbc/npbc_updater-linux-x64` |
    | macOS | `~/Applications/npbc/npbc_updater-macos-x64` |
    | Windows | `~\.npbc\bin\npbc.exe` |

2. Run the following command:

    ```sh
    /path/to/updater update
    ```

3. You can now run `npbc -h` to begin.

&nbsp;

Alternatively, just run these scripts. You'll need to have wget installed.

For Linux systems, run:
```bash
mkdir -p ~/bin/npbc
wget https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_updater-linux-x64 -O ~/bin/npbc/npbc
chmod +x ~/bin/npbc/npbc
~/bin/npbc/npbc update
echo "alias npbc=\"~/bin/npbc/npbc\"" >> ~/.bashrc
exec "$SHELL"
```

For macOS systems, run:
```bash
mkdir -p ~/Applications/npbc
wget https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_updater-macos-x64 -O ~/Applications/npbc/npbc
chmod +x ~/Applications/npbc/npbc
~/bin/Applications/npbc update
echo "alias npbc=\"~/Applications/npbc/npbc\"" >> ~/.bashrc
exec "$SHELL"
```

For Windows systems, run the following from PowerShell and add `~\.npbc\bin` to PATH:
```bat
mkdir -p "~\.npbc\bin";
wget https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_updater-windows-x64.exe -O "~\.npbc\bin\npbc.exe";
& "~\.npbc\bin\npbc.exe" update;
```

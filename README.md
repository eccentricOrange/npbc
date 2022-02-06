# NewsPaper Bill Calculator

This app calculates your monthly newspaper bill.

[![.github/workflows/build.yml](https://github.com/eccentricOrange/npbc/actions/workflows/build.yml/badge.svg)](https://github.com/eccentricOrange/npbc/actions/workflows/build.yml)

## Key concepts
1. Each newspaper has a certain cost per day of the week
2. Each newspaper may or may not be delivered on a given day
3. Each newspaper has a name and a short name, called a key
4. You may register any dates when you didn't receive a paper in advance using the `addudl` command
5. Once you calculate, the results are displayed and copied to your clipboard

## Installation
1. From [the latest release](https://github.com/eccentricOrange/npbc/releases/latest), download the "updater" file for your operating system in any folder, and make it executable.

    **Recommended locations**, where the CLI and API will always download
    | OS | Location |
    | --- | --- |
    | Linux | `~/bin/npbc/npbc_updater-linux-x64` |
    | macOS | `~/Applications/npbc/npbc_updater-macos-x64` |
    | Windows | `C:\Program Files\npbc\npbc_updater-windows-x64.exe` |

2. Run the following command:

    ```sh
    /path/to/updater update
    ```

3. You can now run `npbc -h` to begin.

Alternatively, just run these scripts.

    For Linux systems, run:
    ```bash
    wget https://github.com/eccentricOrange/npbc/releases/download/v1.0.4/npbc_updater-linux-x64 -O ~/bin/npbc/npbc_updater-linux-x64
    chmod +x ~/bin/npbc/npbc_updater-linux-x64
    ~/bin/npbc/npbc_updater-linux-x64 update
    echo "alias npbc=\"~/bin/npbc/npbc_updater-linux-x64\"" >> ~/.bashrc
    exec "$SHELL"
    ```

    For macOS systems, run:
    ```bash
    wget https://github.com/eccentricOrange/npbc/releases/download/v1.0.4/npbc_updater-macos-x64 -O ~/bin/npbc/npbc_updater-macos-x64
    chmod +x ~/Applications/npbc/npbc_updater-macos-x64
    ~/bin/npbc/npbc_updater-macos-x64 update
    echo "alias npbc=\"~/Applications/npbc/npbc_updater-macos-x64\"" >> ~/.bashrc
    exec "$SHELL"
    ```

    For Windows systems, run the following and add `%programfiles%\npbc` to PATH:
    ```bat
    wget https://github.com/eccentricOrange/npbc/releases/download/v1.0.4/npbc_updater-windows-x64 -O "C:\Program Files\npbc\npbc_updater-windows-x64"
    "C:\Program Files\npbc\npbc_updater-windows-x64" update
    echo "^"%programfiles%\npbc\npbc_updater-windows-x64.exe %*^"" > "C:\Program Files\npbc\npbc.bat"
    ```

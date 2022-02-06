from subprocess import call
from platform import system as get_platform_data
from sys import argv
from pathlib import Path
from urllib.request import urlopen


location_data = {
    "Linux": {
        "name": "linux-x64",
        "path": Path.home() / 'bin' / 'npbc'
    },
    "Windows": {
        "name": "windows-x64.exe",
        "path": Path('C:') / 'Program Files' / 'npbc'
    },
    "Darwin": {
        "name": "macos-x64",
        "path": Path.home() / 'Applictaions' / 'npbc'
    }
}


class NPBC_updater:
    def __init__(self):
        self.current_platform_data = location_data[get_platform_data()]
        self.current_platform_data['path'].mkdir(parents=True, exist_ok=True)
        self.cli_path = self.current_platform_data['path'] / \
            f"npbc_cli-{self.current_platform_data['name']}"
        self.api_path = self.current_platform_data['path'] / \
            f"npbc_api-{self.current_platform_data['name']}"
        self.cli_url = f"https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_cli-{self.current_platform_data['name']}"
        self.api_url = f"https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_api-{self.current_platform_data['name']}"

    def read_args(self):
        if argv[1].strip().lower() == "update":
            self.update()

        else:
            self.execute()

    def update(self):
        cli_download = urlopen(self.cli_url).read()
        api = urlopen(self.api_url).read()

        with open(self.cli_path, 'wb') as cli_file:
            cli_file.write(cli_download)

        with open(self.api_path, 'wb') as api_file:
            api_file.write(api)

    def execute(self):
        call([self.cli_path, *argv[1:]])


def main():
    updater = NPBC_updater()
    updater.read_args()


if __name__ == "__main__":
    main()

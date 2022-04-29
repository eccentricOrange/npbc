from subprocess import call
from platform import system as get_platform_data
from sys import argv
from pathlib import Path
from urllib.request import urlopen
from sys import exit
from os import environ

class NPBC_updater:
    def __init__(self):
        self.current_platform_data = {}
        self.set_paths()
        self.current_platform_data['path'].mkdir(parents=True, exist_ok=True)
        self.cli_path = self.current_platform_data['path'] / f"npbc_cli-{self.current_platform_data['name']}"
        # self.api_path = self.current_platform_data['path'] / f"npbc_api-{self.current_platform_data['name']}"
        self.cli_url = f"https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_cli-{self.current_platform_data['name']}"
        # self.api_url = f"https://github.com/eccentricOrange/npbc/releases/latest/download/npbc_api-{self.current_platform_data['name']}"

    def set_paths(self):
        self.current_platform = get_platform_data()

        if self.current_platform == "Linux":
            self.current_platform_data['path'] = Path.home() / 'bin' / 'npbc'
            self.current_platform_data['name'] = 'linux-x64'

        elif self.current_platform == "Windows":
            self.current_platform_data['path'] = Path.home() / '.npbc' / 'bin'
            self.current_platform_data['name'] = 'windows-x64.exe'

        elif self.current_platform == "Darwin":
            self.current_platform_data['path'] = Path.home() / 'Applications' / 'npbc'
            self.current_platform_data['name'] = 'macos-x64'

        else:
            print("Your platform is not supported by NPBC.")
            exit(1)

    def read_args(self):
        if len(argv) == 2 and argv[1].strip().lower() == "update":
            self.update()
            exit(0)

        self.execute()
        exit(0)

    def update(self):
        print ("Downloading NPBC CLI...")
        cli_download = urlopen(self.cli_url).read()
        print ("Done.\n")

        # print ("Downloading NPBC API...")
        # api = urlopen(self.api_url).read()
        # print ("Done.\n\n")

        print ("Installing NPBC CLI...")
        with open(self.cli_path, 'wb') as cli_file:
            cli_file.write(cli_download)
        print ("Done.\n")

        # print ("Installing NPBC API...")
        # with open(self.api_path, 'wb') as api_file:
        #     api_file.write(api)
        # print ("Done.\n\n")

        self.cli_path.chmod(0o755)
        # self.api_path.chmod(0o755)

        print ("NPBC has been updated.")


    def execute(self):
        call([self.cli_path, *argv[1:]])


def main():
    updater = NPBC_updater()
    updater.read_args()


if __name__ == "__main__":
    main()

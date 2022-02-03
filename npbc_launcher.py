from argparse import ArgumentParser, RawTextHelpFormatter, Namespace as arg_namespace
from json import loads
from urllib import request
from npbc_core import NPBC_core
from pathlib import Path
from os import environ, name as platform_name
import sh

class NPBC_cli(NPBC_core):
    def __init__(self):
        self.args = self.define_and_read_args()

    functions = {
        'check': {
            'choice': 'check',
            'help': 'Check for updates.'
        },
        'update': {
            'choice': 'update',
            'help': "Update the application."
        },
        'api': {
            'choice': 'api',
            'help': "Get the NPBC API."
        }
    }

    def define_and_read_args(self) -> arg_namespace:
        self.parser = ArgumentParser(
            description="Calculates your monthly newspaper bill.",
            formatter_class=RawTextHelpFormatter
        )

        self.parser.add_argument(
            'command',
            # nargs='?',
            choices=[value['choice'] for key, value in self.functions.items()],
            help='\n'.join([f"{value['choice']}: {value['help']}" for key, value in self.functions.items()])
        )

        return self.parser.parse_args()

    def check_args(self):
        if self.args.command == 'check':
            self.set_app_directory()
            self.check()

        elif self.args.command == 'update':
            self.set_app_directory()
            self.update()

        elif self.args.command == 'api':
            self.api()

        else:
            self.run_cli()

    def get_release_data(self):
        self.release_data = loads(request.urlopen('https://api.github.com/repos/eccentricOrange/NPBC/releases/latest').read())

    def set_app_directory(self):
        # if windows, set to program files; else opt/npbc
        if platform_name == 'nt':
            self.app_directory = Path(environ['ProgramFiles']) / 'NPBC'
        else:
            self.app_directory = Path('/opt') / 'npbc'

        self.get_release_data()
        
        self.install_location = list(self.app_directory.glob('*npbc*x*'))[0]
        self.current_version = self.install_location.name.split('-')[1]
        self.latest_version = self.release_data['tag_name']

    def check(self):
        if self.current_version != self.latest_version:
            print(f"A new version of NPBC is available: {self.latest_version}")
            print("Run 'npbc update' to update.")
        else:
            print("You are already running the latest version of NPBC.")

    def update(self):
        print("Updating")
        self.download_release()
        print("NPBC updated.")

    def api(self):
        path = list(self.app_directory.glob('*npbc*api*'))[0]
        sh.npbc_api(_cwd=path)

    def run_cli(self):
        path = list(self.app_directory.glob('*npbc*cli*'))[0]
        sh.npbc_cli(_cwd=path, )
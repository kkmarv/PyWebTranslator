import inspect
import os
from argparse import ArgumentParser, Action
from types import ModuleType
from typing import Optional, Sequence

from code import drivers, services

default_service = 'DeepL'
default_browser = 'Firefox'


class _Args:
    """An object containing all arguments parsed through the CLI."""
    input: str
    is_path: bool
    file_dir_path: str
    output: Optional[None]
    browser: str
    service: str


class _PrintListAction(Action):
    def __init__(self, option_strings: Sequence[str], dest: str, **kwargs):
        self._supported_browser = []
        self._supported_services = []

        for drivername in get_classnames(drivers):
            self._supported_browser.append(drivername)
        for servicename in get_classnames(services):
            self._supported_services.append(servicename)

        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values == 'browser':
            print(f'Currently supported browser are:{os.linesep}')
            for classname in get_classnames(drivers):
                print(classname)
        elif values == 'services':
            print(f'Currently supported translation services are:{os.linesep}')


def get_classnames(module: ModuleType) -> list[str]:
    """Get the classname from all non-abstract classes of a given module.

    :param module: The Module in which to look for non-abstract classes.
    :return: A list containing the names."""
    classnames = []
    for name, _ in inspect.getmembers(module, lambda member: (
            inspect.isclass(member) and not inspect.isabstract(member) and member.__module__ == module.__name__)):
        classnames.append(name)
    return classnames


parser = ArgumentParser(
    prog='PyWebTranslator',
    description='A Python CLI web scraper that allows translation from a variety of online translation services.')

subparsers = parser.add_subparsers(help='Begin translating or list a number of supported services.')

# translate command
translate_parser = subparsers.add_parser('translate')

# positional arguments
translate_parser.add_argument(
    'input', type=str,
    help='The input text which to translate. See -p flag if translation of files is desired.')

# optional arguments
translate_parser.add_argument(
    '-p', action='store_true', dest='is_path',
    help='Interpret input as a path (defaults to %(default)s). '
         'If specified, input must be a plain .txt file or a directory containing .txt files. '
         'From these files, all lines (separated by line breaks) will be translated independently, '
         'so make sure that a single sentence is not spread over multiple lines.')
translate_parser.add_argument(
    '-o', '--output', type=str,
    help='Specify an output file or dir. '
         'If input is made through the command line or a single file, a new file containing the translation will be created. '
         'If input is a dir, the whole directory structure will be copied with each text file getting its own translated counterpart.')
translate_parser.add_argument(
    '-s', '--service', type=str, choices=('DeepL', 'GoogleTranslate'),
    help='The translation service to use (defaults to %(default)s).')
translate_parser.add_argument(
    '-b', '--browser', type=str, choices=('Edge', 'Firefox'),
    help='The browser to use (defaults to %(default)s). Will download additional files on first use.')

translate_parser.set_defaults(
    is_path=False,
    output=None,
    browser=default_browser,
    service=default_service
)

# list command
list_parser = subparsers.add_parser('list')
list_parser.add_argument(
    'option', action=_PrintListAction, choices=('browser', 'services'),
    help='Print a list of supported browser or translation services respectively.')

ARGS = parser.parse_args(namespace=_Args)

# argument validation

# translate command
if ARGS.is_path and not os.path.exists(ARGS.input):
    translate_parser.error(f'Input path not found: "{ARGS.input}". '
                           'If it is not meant to be interpreted as a path, remove the -p flag.')

if not ARGS.is_path and os.path.exists(ARGS.input):  # Warn the user if a path gets input without -p flag
    print('Warning: Input seems to be a path. If you want it to be handled as one, add the -p flag.')

if ARGS.output is not None and not os.path.exists(ARGS.output):
    translate_parser.error(f'Input path not found: "{ARGS.output}"')

import argparse
import dataclasses
import typing

@dataclasses.dataclass
class CliCommonOptions:
    dry_run: bool
    use_symlinks: bool
    debug_ngproc: bool

def parse() -> typing.Tuple[argparse.ArgumentParser, argparse.Namespace, CliCommonOptions]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'root',
        action='store',
        nargs=1,
        help="the root TOML configuration file")
    parser.add_argument(
        '--dry-run',
        '-d',
        action='store_true',
        help="don't perform any actual operations on the filesystem")
    parser.add_argument(
        '--use-symlinks',
        '-s',
        dest='use_symlinks',
        action='store_const',
        const=True,
        help="use symlinks - default")
    parser.add_argument(
        '--no-use-symlinks',
        '-S',
        dest='use_symlinks',
        action='store_const',
        const=False,
        help="don't use symlinks and copy instead - useful on Windows")
    parser.add_argument(
        '--debug-ngproc',
        action='store_true',
        help="make the NgProc parser print more debug messages - useful to find subtle syntax errors or to debug the parser itself")
    parser.add_argument(
        '--def',
        '-f',
        nargs=2,
        metavar=('name', 'val'),
        dest='defs',
        action='append',
        help="define a variable")

    parse_result = parser.parse_args()

    cli_common_options = CliCommonOptions(
            parse_result.dry_run,
            parse_result.use_symlinks if parse_result.use_symlinks is not None else True,
            parse_result.debug_ngproc)

    return (parser, parse_result, cli_common_options)

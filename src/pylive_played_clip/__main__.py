'''
Usage
-----
.. argparse::
   :module: pylive_played_clip.__main__
   :func: _get_argument_parser
   :prog: pylive_played_clip.__main__
'''
import argparse
import logging
import textwrap

from pathlib import Path
from typing import List


from pylive_played_clip import AbletonClipMonitor


def _main() -> None:
    '''The main routine for the module.'''
    args: argparse.Namespace = _parse_arguments()
    set_log_level(args)

    ableton = AbletonClipMonitor(
        dim_color=args.dim_color,
        dim_ratio=float(args.dim_ratio),
        polling_delay=float(args.polling_delay),
        no_reset=bool(args.no_reset)
    )
    ableton.monitor()


def _get_argument_parser() -> argparse.ArgumentParser:
    """Returns the argument parser. This function is used by
    sphinx to include the command line usage in the documentation.

    :return: The argparse.ArgumentParser before the arguments have been parsed.
    :rtype: :class:`argparse.ArgumentParser`
    """
    basename: str = Path(__file__).name
    usage = textwrap.dedent(f"""\
{basename} --version

Command Line Examples
> {basename}
> {basename} --dim-color 555555 --log-level debug

Selected Options:
    --log-level, -l [debug]  Use this value as the build number.
    -h                       Show the full help, including all options.
""")

    description: str = textwrap.dedent('''\
This is a script to watch Ableton live for when a clip finishes and dim the
color of the track. If the script detects that Ableton play has stopped, it will
reset the colors.
''')

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        usage=usage,
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--dim-color', '-c',
                        dest='dim_color',
                        help=('The color to dim to in hex form, FFFFFF'))
    parser.add_argument('--dim-ratio',
                        default=2.0,
                        dest='dim_ratio',
                        type=float,
                        help=('If dim values for red, green and blue are not '
                              'all specified, we\'ll reduce the clips values by '
                              'this amount'))
    parser.add_argument('--polling-delay',
                        default=0.1,
                        type=float,
                        dest='polling_delay',
                        help=('Default 0.1 second. The polling delay'))
    parser.add_argument('--no-reset',
                        action='store_true',
                        dest='no_reset',
                        help=('If provided, the colors will not be reset '
                              'when Ableton stops.'))
    parser.add_argument('--log-level', '-l',
                        dest='log_level',
                        default='info',
                        choices=['fatal', 'error', 'warn', 'info', 'debug'],
                        help='Sets the logging level.')

    return parser


# --------------------------------------------------------------------------- #
# General Script Utilities
# --------------------------------------------------------------------------- #
def _parse_arguments(test_args: List[str] = []) -> argparse.Namespace:
    """Used to parse the command line arguments

    :param test_args: Used during unit testing, defaults to None
    :type test_args: List[str]

    :return: The argparse argument parser with the arguments parsed.
    :rtype: :class:`argparse.Namespace`
    """
    parser: argparse.ArgumentParser = _get_argument_parser()
    if test_args:
        return parser.parse_args(test_args)
    else:
        return parser.parse_args()


def set_log_level(args: argparse.Namespace) -> None:
    """Sets the logging level.

    Defaults to **logging.INFO**
    See :py:class:`logging.Logger`

    :param args: The argument parser
    :type args: :class:`argparse.ArgumentParser`

    :returns: Nothing
    :rtype: None
    """

    log_level: str = 'info'
    if args.log_level:
        log_level = args.log_level

    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.StreamHandler()
        ]
    )

    logging.basicConfig()
    if log_level.lower() == 'fatal':
        logging.getLogger().setLevel(logging.CRITICAL)
    elif log_level.lower() == 'error':
        logging.getLogger().setLevel(logging.ERROR)
    elif log_level.lower() == 'warn':
        logging.getLogger().setLevel(logging.WARNING)
    elif log_level.lower() == 'debug':
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


if __name__ == '__main__':
    _main()

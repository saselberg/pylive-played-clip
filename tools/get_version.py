#!/usr/bin/python3
import argparse
import json
import os
import logging
import textwrap
import platform
import subprocess
import sys

from pathlib import Path
from typing import Dict, List

__project_dir__: Path = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__project_dir__, 'src')))
import pylive_played_clip  # noqa: E402


__version_info__: List[str] = ['99', '99', '99']
__version__: str = '.'.join(__version_info__)


class VersionScriptError(Exception):
    """Version Script Error Class."""
    pass


def get_base_version_from_source(build_number: str) -> str:
    """Get the base version

    :param build_number: The build number
    :type build_number: str

    :returns: The semantic version Major.Minor.Patch
    :rtype: str
    """
    version = pylive_played_clip.__version__
    logging.debug(f"Base version is {version}")
    return version


# --------------------------------------------------------------------------- #
# Script subroutines.
# --------------------------------------------------------------------------- #
def main() -> None:
    build_number: str

    args: argparse.Namespace = _parse_arguments()
    set_log_level(args)

    prerelease: str = ''
    build_info: str = ''
    use_unique_count: bool = False

    build_number = get_build_number(args)

    base_version: str = get_base_version_from_source(build_number)

    if args.include_build_info:
        build_info = get_build_info(args, build_number)

    if args.include_prerelease:
        prerelease = get_prerelease(args, build_number)

    full_version: str = base_version
    if prerelease:
        full_version += f"{args.prerelease_delimiter}{prerelease}"

    if build_info:
        full_version += f"+{build_info}"

    if args.json:
        version_object: Dict[str, str] = {
            'executable': os.path.basename(__file__),
            'version': full_version,
            'base': base_version,
            'prerelease': prerelease,
            'build-info': build_info
        }
        print(json.dumps(version_object, indent=4))
    else:
        print(full_version)


def get_build_number(args: argparse.Namespace) -> str:
    """ Gets the build number. This will first check for args.build_number.
    If no value exists there, we'll check for the BUILD_NUMBER environment
    variable. If that doesn't exist, we'll default to 0.

    :param args: The argparse namespace
    :type args: :py:class:`argparse.Namespace`
    """
    build_number: str = '0'
    if args.build_number:
        build_number = args.build_number
        logging.debug('The build number according to the cli argument '
                      f"build-number is \"{build_number}\".")
    elif os.environ.get('BUILD_NUMBER'):
        build_number = str(os.environ.get('BUILD_NUMBER'))
        logging.debug('The build number according to the BUILD_NUMBER '
                      f"environment variable is \"{build_number}\".")
    else:
        logging.debug(f"The build number default is \"{build_number}\".")

    return build_number


def get_build_info(args: argparse.Namespace, build_number: str = '0') -> str:
    """ Gets the build info suffix. If args.build_info_base is defined,
    this will return f"{build_info_base}{build_number}". If the build info
    base is not defined, this will just return the build_number.

    :params args: The argparse namespace object.
    :type: :py:class:`argparse.Namespace`
    :params build_number: The build number.
    :type: str

    :returns: The prerelease string if one is appropriate
    :rtype: str
    """
    build_info: str = ''

    if args.build_info_base:
        logging.debug(f"Using the build info base \"{args.build_info_base}\".")
        build_info = str(args.build_info_base)

    build_info += build_number

    return build_info


def get_prerelease(args: argparse.Namespace, build_number: str = '0') -> str:
    """ Gets the pre-release suffix which is the leaf of the git branch with
    non-alphanumeric characters replaced by underscores.

    :params args: The argparse namespace object.
    :type: :py:class:`argparse.Namespace`
    :params build_number: The build number.
    :type: str

    :returns: The prerelease string if one is appropriate
    :rtype: str
    """
    prerelease: str = ''
    branch: str = get_git_branch(args)
    release_branches: List[str] = args.release_branch

    if not release_branches:
        release_branches = ['master']
    elif isinstance(release_branches, str):
        logging.debug("The release branch is a str, make it a list[str]")
        release_branches = [release_branches]

    if branch not in release_branches:
        if args.prerelease_base:
            logging.debug('Using the specified prerelease base '
                          f"{args.prerelease_base}")
            prerelease = str(args.prerelease_base)
        else:
            git_branch_leaf = Path(branch).name
            logging.debug(f"Using the leaf of the git branch, \"{branch}\", "
                          f"as the prerelease base: {git_branch_leaf}")
            prerelease = git_branch_leaf

        if args.include_build_number_in_prerelease:
            prerelease += build_number
    else:
        logging.debug(f"The current branch, \"{branch}\", is a release branch "
                      "therefore there is no prerelease suffix.")

    return prerelease


def get_git_branch(args: argparse.Namespace) -> str:
    """ Gets the git branch. This will first check for the cli argument
    'git_branch'. If that is empty, it will check the environment variable
    GIT_BRANCH. If that is also empty, it will call git to try and figure
    out the branch.

    Jenkins checks out a detached head, so it's hard to use git commands to
    figure out the git branch from git which is why we check the environment
    variable first.

    :params args: The argparse namespace object.
    :type: :py:class:`argparse.Namespace`

    :returns: The prerelease string if one is appropriate
    :rtype: str
    """
    git_branch: str = ''
    if args.git_branch:
        git_branch = str(args.git_branch)
        logging.debug('The current branch according to the '
                      f"git-branch cli argument is: \"{git_branch}\".")
    elif os.environ.get('GIT_BRANCH'):
        git_branch = str(os.environ.get('GIT_BRANCH'))
        logging.debug('The current branch according to the '
                      f"GIT_BRANCH environment variable is: \"{git_branch}\".")
    else:
        git_branch = run_command_and_capture_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
        logging.debug('The current branch according to '
                      f"git rev-parse --abbrev-ref HEAD' is: \"{git_branch}\".")

    return git_branch


def run_command_and_capture_output(command: List[str]) -> str:
    """This runs a command and returns the output.

    :param command: The command as a list.
    :type command: List[str]

    :returns: The stdout printed by the command.
    :rtype: str
    """

    shell: bool = False
    if 'Windows' in platform.system():
        shell = True

    result = subprocess.run(
        command, check=True, shell=shell, stdout=subprocess.PIPE)
    return result.stdout.decode(sys.stdout.encoding).strip()


# --------------------------------------------------------------------------- #
# General Script Utilities
# --------------------------------------------------------------------------- #
def _get_argument_parser() -> argparse.ArgumentParser:
    """Returns the argument parser. This function is used by
    sphinx to include the command line usage in the documentation.

    :return: The argparse.ArgumentParser before the arguments have been parsed.
    :rtype: :class:`argparse.ArgumentParser`
    """
    basename: str = Path(__file__).name
    usage = textwrap.dedent(f"""\
{basename} --version-json

Command Line Examples
> {basename}
> {basename} --json
> {basename} --json --build-number 1

Selected Options:
    --json                          Print the information as a json string.
    --build-number $BUILD_NUMBER    Use this value as the build number.
    --no-prerelease                 Do not include the prerelease information.
    -h                              Show the full help, including all options.
""")

    description: str = textwrap.dedent('''\
This is a script to compute the version.
''')

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        usage=usage,
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--build-number',
                        dest='build_number',
                        help=('The build number included in the prerelease '
                              'and build info fields. If not provided, the '
                              'script will check the environment variable '
                              'BUILD_NUMBER or default to 0.'))
    parser.add_argument('--no-prerelease', action='store_false',
                        dest='include_prerelease',
                        help='If specified, no prerelease will be included.')
    parser.add_argument('--no-build-info', action='store_false',
                        dest='include_build_info',
                        help='If specified, no build info will be included.')
    parser.add_argument('--no-build-number-in-prerelease',
                        action='store_false',
                        dest='include_build_number_in_prerelease',
                        help=('If specified, the build number will not be '
                              'included in the prerelease suffix.'))
    parser.add_argument('--release-branch', action='append',
                        dest='release_branch',
                        help=('Default: master. The name of a release branch '
                              'which will have no prerelease suffix. This '
                              'argument can be provided multiple times to '
                              'specify multiple release branches.'))
    parser.add_argument('--git-branch',
                        dest='git_branch',
                        help=('The name of the current git branch. If not '
                              'provided, the script will check for the '
                              'environment variable GIT_BRANCH and if that '
                              'is also absent will use git to try and figure '
                              'out the branch. Jenkins checks the code out in '
                              'a detached head mode, so git cannot be used to '
                              'detect the branch name which is why we check '
                              'the other options first.'))
    parser.add_argument('--prerelease-delimiter', default='-',
                        dest='prerelease_delimiter',
                        help=('Semantic version wants a \"-\" character, but '
                              'pypi requires you to use a \".\" character.'))
    parser.add_argument('--prerelease-base',
                        help=('If provided, the script will use this value '
                              'rather than the normalized leaf of the git '
                              'branch for the base of the prerelease suffix.'))
    parser.add_argument('--build-info-base',
                        help=('If provided, the script will use this value '
                              'for the base of the build info field. For '
                              'example, if the --build-info-base is '
                              '\"build\", the version will be 0.0.0+build1'))
    parser.add_argument('--json', action='store_true',
                        help='Prints out the version info in json format.')
    parser.add_argument('--log-level', '-l',
                        dest='log_level',
                        default='info',
                        choices=['fatal', 'error', 'warn', 'info', 'debug'],
                        help='Sets the logging level.')

    return parser


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
    if log_level.lower() == "fatal":
        logging.getLogger().setLevel(logging.CRITICAL)
    elif log_level.lower() == "error":
        logging.getLogger().setLevel(logging.ERROR)
    elif log_level.lower() == "warn":
        logging.getLogger().setLevel(logging.WARNING)
    elif log_level.lower() == "debug":
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)


# --------------------------------------------------------------------------- #
# Main script.
# --------------------------------------------------------------------------- #
if __name__ == '__main__':
    main()
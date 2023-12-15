#!/usr/bin/python3
import argparse
import json
import os
import getpass
import glob
import logging
import platform
import socket
import shutil
import subprocess
import sys
import textwrap

from datetime import datetime


__version_info__: list[str] = ['1', '0', '1']
__version__: str = ".".join(__version_info__)

cwd: str = os.getcwd()
output_directory: str = 'html'
__default_sphinx_title__: str = 'Pylive Played Clip'
__default_sphinx_title_placeholder__: str = 'SPHINX_TITLE'
__default_version_placeholder__: str = '__PROJECT_VERSION__'
__now__: str = datetime.now().strftime('%H:%M:%S %a %b %d, %Y')

prerelease_map: dict[str, str] = {}


# ---------------------------------------------------------------------------- #
# Script subroutines.
# ---------------------------------------------------------------------------- #
def main() -> None:
    args: argparse.Namespace = _parse_arguments()
    set_log_level(args)

    if os.path.isdir(output_directory):
        shutil.rmtree(output_directory)

    if os.path.isfile(f"{output_directory}.zip"):
        os.remove(f"{output_directory}.zip")

    version: str = get_version()
    scm_url: str = get_git_url()
    scm_branch: str = get_git_branch()
    scm_commit_hash: str = get_git_commit_hash()
    build_job: str = get_build_job()

    if args.prerelease_string:
        version = version + "-" + args.prerelease_string
    elif scm_branch in prerelease_map:
        version = version + "-" + str(prerelease_map.get(scm_branch))
    elif not scm_branch == 'master':
        version = version + "-" + scm_branch

    os.chdir('docs')
    sphinx_build: list[str] = ['sphinx-build', '-v', '-W', '-n']
    if detect_all_warnings(args):
        sphinx_build.append('--keep-going')
    sphinx_build.extend(['-b', 'html', '.', os.path.join('..', output_directory)])
    status = subprocess.run(sphinx_build)
    print('\n')
    os.chdir(cwd)

    if status.returncode > 0:
        logging.error('sphinx-build operation failed')
        exit(status.returncode)

    # These steps are usually done by the Jenkins CI/CD pipeline,
    # but replicated here to support running manually
    os.chdir(output_directory)
    logging.info(' Updating Generated Documentation')
    logging.info(f"    title: {args.sphinx_title}")
    logging.info(f"    version: {version}")
    logging.info(f"    scm url: {scm_url}")
    logging.info(f"    scm branch: {scm_branch}")
    logging.info(f"    scm commit hash: {scm_commit_hash}")
    logging.info(f"    build job: {build_job}")
    update_version_in_files(args, version)
    update_build_info(scm_url, scm_branch, scm_commit_hash, build_job)
    logging.info(' Done.\n')
    os.chdir(cwd)

    logging.info(' Creating documentation zip file.')
    shutil.make_archive(output_directory, "zip", output_directory)
    logging.info(' Done.\n')


def get_git_branch() -> str:
    command: list[str] = ['git', 'rev-parse', '--abbrev-ref', 'HEAD']
    return execute_command_and_capture_output(command)


def get_git_commit_hash() -> str:
    command: list[str] = ['git', 'rev-parse', '--short', 'HEAD']
    return execute_command_and_capture_output(command)


def get_git_url() -> str:
    command: list[str] = ['git', 'config', '--get', 'remote.origin.url']
    return execute_command_and_capture_output(command)


def get_build_job() -> str:
    user: str = getpass.getuser()
    hostfqdn: str = socket.getfqdn()
    return os.path.basename(__file__) + f": {user}@{hostfqdn}"


def get_version() -> str:
    version: str = '0.0.0'

    python = sys.executable
    get_version_executable: str = os.path.join(os.path.dirname(__file__), 'get_version.py')
    command: list[str] = [python, get_version_executable, '--json']
    script_output: str = execute_command_and_capture_output(command)

    output_dict: dict = json.loads(script_output)
    if output_dict.get('version'):
        version = str(output_dict.get('version'))

    return version


def update_version_in_files(args: argparse.Namespace, version: str) -> None:
    version_placeholder: str = args.version_placeholder
    update_map: dict[str, str] = {version_placeholder: version}

    for type in ['.html', '.js']:
        for file in glob.glob(f"**/*{type}", recursive=True):
            replace_strings_in_file(file, update_map)


def update_build_info(url: str, branch: str, commit_hash: str, buildjob: str) -> None:
    update_map: dict = {
        'SCM_URL': url,
        'SCM_BRANCH': branch,
        'SCM_COMMIT_HASH': commit_hash,
        'BUILD_JOB': buildjob,
        'BUILD_DATETIME': __now__
    }
    replace_strings_in_file('build-info.html', update_map)


def detect_all_warnings(args: argparse.Namespace) -> bool:
    return args.detect_all_warnings


# ---------------------------------------------------------------------------- #
# Utilities to help out this script
# ---------------------------------------------------------------------------- #
def execute_command_and_capture_output(command: list[str]) -> str:
    shell: bool = False
    if is_windows():
        shell = True

    subprocess_result = subprocess.run(command,
                                       check=False,
                                       shell=shell,
                                       stdout=subprocess.PIPE)
    return subprocess_result.stdout.decode(sys.stdout.encoding).strip()


def replace_strings_in_file(target_file: str, replace_map: dict[str, str]) -> None:
    contents: str = ''
    with open(target_file, 'r', encoding='utf-8') as file_handle:
        contents = file_handle.read()

    for old_string in replace_map:
        contents = contents.replace(old_string, replace_map[old_string])

    with open(target_file, 'w', encoding='utf-8') as file_handle:
        file_handle.write(contents)

    return


def is_windows() -> bool:
    return "Windows" in platform.system()


# ---------------------------------------------------------------------------- #
# General Script Utilities
# ---------------------------------------------------------------------------- #
def _get_argument_parser() -> argparse.ArgumentParser:
    """Returns the argument parser. This function is used by
    sphinx to include the command line usage in the documentation.

    :return: The argparse argument parser before the arguments have been parsed.
    :rtype: :class:`argparse.ArgumentParser`
    """
    basename: str = os.path.basename(__file__)
    usage: str = textwrap.dedent(f"""\
{basename} --version-json
Version: {__version__}

Command Line Examples
> {basename} --prefix

Selected Options:
    --prefix                        Use the supplied prefix

    -h                              Show the full help, including all options.
""")

    description: str = textwrap.dedent("""\
This is a script to build the sphinx documentation.  The Jenkins pipeline for
this job will replace the strings SPHINX_TITLE and the __PROJECT_VERSION__ with
the appropriate values. This script will make the substitutions as well in the
final html output so the strings in the source code do not get accidentally
modified.
""")

    epilog: str = textwrap.dedent("""\
For extra documentation about this script, see https://bitbucket.it.keysight.com/projects/KOSIUTIL/repos/keysight-sphinx-writers-guide/browse
""")

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        usage=usage,
        description=description,
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--prerelease-string', '-p',
                        dest='prerelease_string',
                        help='The prerelease string to append to the version. Example: \"beta\".')
    parser.add_argument('--sphinx-title', '-t',
                        default=__default_sphinx_title__,
                        dest='sphinx_title',
                        help='The title of the sphinx documentation.')
    parser.add_argument('--sphinx-title-placeholder',
                        default=__default_sphinx_title_placeholder__,
                        dest='sphinx_title_placeholder',
                        help=('The string in the source code that identifies '
                              'where the Sphinx title should be inserted by '
                              'the build code.'))
    parser.add_argument('--version-placeholder',
                        default=__default_version_placeholder__,
                        dest='version_placeholder',
                        help=('The string in the source code that identifies '
                              'where the version should be inserted by '
                              'the build code.'))
    parser.add_argument('-s', '--stop-on-first-warning',
                        action='store_false',
                        dest='detect_all_warnings',
                        help=('Use \'--stop-on-first-warning\' to stop the '
                              'sphinx-build command after the first warning is found. '
                              'By default, sphinx will process the full project but '
                              'still exit with an error if any warnings are found. '
                              'The option is useful for large sphinx projects.'))

    add_standard_cli_options_to_argparse_parser(parser, __version__)

    return parser


def _parse_arguments(test_args: list[str] = []) -> argparse.Namespace:
    """Used to parse the command line arguments

    :param test_args: Used during unit testing to pass in the command line args, defaults to None
    :type test_args: dict

    :return: The argparse Namespace
    :rtype: :class:`argparse.Namespace`
    """
    parser: argparse.ArgumentParser = _get_argument_parser()
    if test_args:
        return parser.parse_args(test_args)
    else:
        return parser.parse_args()


def add_standard_cli_options_to_argparse_parser(parser: argparse.ArgumentParser, version: str) -> None:
    """Used to insert standard cli options, **--log-level**, **--version**
    and **--version-json** into the argparse list.

    :param parser: The argparse parser.
    :type parser: :py:class:`argparse.ArgumentParser`
    :param version: The version string, something like '1.0.1'
    :type version: str

    :returns: Nothing
    :rtype: None
"""

    # Standard Arguments...
    parser.add_argument('--log-level', '-l',
                        dest='log_level',
                        default='info',
                        choices=['fatal', 'error', 'warn', 'info', 'debug'],
                        help='Sets the logging level.')
    parser.add_argument('--version', '-v', action='version',
                        version=version,
                        help='Prints the version number.')
    parser.add_argument('--version-json', action='version',
                        version="{\"executable\":\"%(prog)s\", \"version\":\""+version+"\"}",
                        help='Prints the version number in json format.')


def set_log_level(args: argparse.Namespace) -> None:
    """Sets the logging level.

    Defaults to **logging.INFO**
    See :py:class:`logging.Logger`

    :param args: The argument parser namespace
    :type args: :class:`argparse.Namespace`

    :returns: Nothing
    :rtype: None
    """

    log_level: str = "info"
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


# ---------------------------------------------------------------------------- #
# Main script.
# ---------------------------------------------------------------------------- #
if __name__ == '__main__':
    main()

#!/usr/bin/python3
# the purpose of this module is to add the src directory
# into the path to search for modules.
import sys

from pathlib import Path


def get_parent_directory() -> str:
    return str(Path(Path(__file__).parent.parent, 'src'))


def add_parent_directory_to_module_search_path() -> None:
    sys.path.insert(0, get_parent_directory())


add_parent_directory_to_module_search_path()

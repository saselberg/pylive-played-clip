#!/usr/bin/python3
import logging
import re

from pathlib import Path
from typing import Dict, List

import enable_imports_from_src_folder
import pylive_played_clip


def test_versions_matched() -> None:
    setup_file = Path( Path(__file__).parent.parent, 'setup.cfg')
    version_line_re = re.compile(r'^version\s*=\s*(\d+\.\d+\.\d+)')

    with open(setup_file, 'r') as f:
        contents: List[str] = f.readlines()

    for line in contents:
        matches = version_line_re.match(line)
        if matches:
            setup_version = matches.group(1)
            break

    assert pylive_played_clip.__version__ == setup_version

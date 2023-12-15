#!/usr/bin/python3
import re

from pathlib import Path
from typing import List

import enable_imports_from_src_folder  # noqa: F401
import pylive_played_clip


def test_versions_matched() -> None:
    setup_file: Path = Path(Path(__file__).parent.parent, 'setup.cfg')
    setup_version: str = ''
    version_line_re: re.Pattern = re.compile(r'^version\s*=\s*(\d+\.\d+\.\d+)')

    with open(setup_file, 'r') as f:
        contents: List[str] = f.readlines()

    for line in contents:
        matches = version_line_re.match(line)
        if matches:
            setup_version = matches.group(1)
            break

    assert pylive_played_clip.__version__ == setup_version

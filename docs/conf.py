# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import json
import os
import subprocess
import sys

__project_dir__ = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(__project_dir__, 'src'))


class ConfError(Exception):
    """Sphinx Configuration Error."""
    pass


def get_project_version(default_version="99.99.99"):
    '''Gets the project version. When run by the build system, the string
    '99.99.99 will be replaced by the version computed by the build system,
    so in here we are testing to see if it's still that value. If it is
    we query for the current version and use that value.  If the build system
    has modified that string, then we keep the current value.'''

    if default_version == ".".join(['99', '99', '99']):
        get_version_script = os.path.join(__project_dir__, 'tools', 'get_version.py')
        python = sys.executable

        result = subprocess.run([python, get_version_script, '--json'], stdout=subprocess.PIPE, check=True)
        json_string = result.stdout.decode(sys.stdout.encoding)

        try:
            version = json.loads(json_string).get('version')
        except json.JSONDecodeError:
            raise ConfError("Failed to get the version from get_version.py")
    else:
        version = default_version

    return version


# -- Project information -----------------------------------------------------
project = 'Pylive Played Clip'
copyright = '2023, Scott Selberg'
author = 'Scott Selberg'

# The full version, including alpha/beta/rc tags
release = get_project_version()

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinxarg.ext',
    'sphinx_copybutton',
    'sphinx_toolbox.collapse',
    'sphinx_rtd_theme',
    'linuxdoc.rstFlatTable',      # Implementation of the 'flat-table' reST-directive
    'myst_parser'                 # support for markdown
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

nitpick_ignore = [('py:class', 'any')]
numfig = True

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/images/PyPI_logo.svg'
html_favicon = '_static/images/PyPI_logo.svg'

html_theme_options = {
    'display_version': True,
    'style_external_links': True
}

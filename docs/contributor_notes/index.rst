=================
Contributor Notes
=================

Development environment setup
=============================

.. code-block:: console

   git clone https://github.com/saselberg/pylive-played-clip.git
   cd pylive-played-clip
   python3 -m venv .venv
   source ./.venv/bin/activate  # Linux
   # .\.venv\Scripts\activate  # Windows
   python3 -m pip install -e ".[dev]"

Publishing
==========

Preparation
-----------

* update the version in setup.cfg and src/pylive_played_clip.__init__.py
* make sure the following checks are free of errors

   * Run ``flake8 src``
   * Run ``flake8 test``
   * Run ``mypy src``
   * Run ``mypy test``
   * Run ``pyright src``
   * Run ``pyright text``
   * Run ``pytest``
   * Run ``python3 ./tools/build_docs``

Build
-----

.. code-block:: console

   python3 -m build

Upload
------

.. note::

   For the username, use ``__token__`` and for the password use your pypi
   token value including the ``pypi-`` prefix.

.. code-block:: console

   python3 -m twine upload dist/*

Clip Colors
===========

Ableton Live uses a single integer to represent the red, green and blue
values of the clip color. The first 8 bits are the blue, the next 8 bits
are the green and the last 8 bits are the red.

.. code-block:: console

   int(24) color = 'rrrrrrrrggggggggbbbbbbbb'

==================
Pylive Played Clip
==================

.. toctree::
   :hidden:
   :titlesonly:
   :caption: Documentation:

   Project README.md <readme.md>

Introduction
============

This is a python package that deploys a command line tool to monitor
Ableton Live clips through `AbletonOSC`_ and `pylive`_. When a clip finishes
playing, this utility will change it's color to visually flag the clip as
having been played. When the global playback is stopped, the utility will
reset all of the clips to the color they had before it changed them. (When
the utility is stopped, it forgets what clips it's changed and what their
original color was.)

This was developed for a talent show at `Foothills Elementary`_.
We needed a way for an elementary student to control the sequencing of several
dozen sound clips. In the past we've used iTunes, but it was a bit unresponsive
and error prone. Starting in 2024, we'll be using a launchpad to trigger the
clips and using this utility to dim the color of the clips as they get played.
This will make it very simple to know which clips have been played and which
is the next clip to play.

There is a `similar utility <https://blog.abletondrummer.com/automatically-change-played-clips/>`_
created using MaxForLive created by AbletonDrummer. That 'device' costs $12
and I believe it requires `MaxForLive <https://www.ableton.com/en/live/max-for-live/>`_
or Ableton Live Suite which I think includes MaxForLive. We only have the
free Ableton Live Lite license that came with the LaunchPad so the Max4Live
path did not seem viable for us. This path using `AbletonOSC`_ works fine with
Ableton Live Lite 11.

.. _AbletonOSC: https://github.com/ideoforms/AbletonOSC
.. _pylive: https://github.com/ideoforms/pylive
.. _Foothills Elementary: https://foothills.asd20.org

How it works
============

`AbletonOSC`_ is a MIDI remote script that should be placed in Ableton's
'Remote Scripts' folder. As Ableton starts up, it will launch the script.
This creates a listener program on the local computer where messages
conforming to the `Live Object Model <https://docs.cycling74.com/max8/vignettes/live_object_model>`_
can be sent and it will convert them to the proper MIDI syntax that Ableton
receives.

The same group that makes AbletonOSC also maintain a python library,
`pylive`_, that makes it easy to write python programs can interact with
Ableton using the `AbletonOSC`_ interface.

This project builds on top of `pylive`_ to create a utility that monitors
Ableton and changes the color of a clip when it finishes playing. The utility
can either set the clip to a pre-defined value, such as dark grey, or it can
'dim' the original color. When Ableton is stopped, the colors will be reset
to the values they had before the utility changed them.

Installation
============

First, install Python version 3.8 or above. This is likely to be preinstalled
on a linux or MacOS machine. There are plenty of install instructions on the
internet for Windows.

Next, you will need to install `AbletonOSC`_. This involves downloading a zip
file and unpacking it into ``.../Ableton/User Library/Remote Scripts``. On my
system, I had to create the directory ``Remote Scripts``, but the rest had
already been created by Ableton. After putting the files in place, I had to
restart Ableton, locate the 'Link|Tempo|Midi' preferences and add
``AbletonOSC`` as a controller to complete the process. The `AbletonOSC`_
home page has detailed instructions on the process.

Lastly, you will need to install ``pylive-played-clip`` using python's package
manager pip. The python package creates a command line script that you can use
to launch the utility. On Windows, it needs administrative permissions to create
the command line entry point. You can install with only normal user permissions,
but you will need to launch the utility differently. On linux and macOS, the
user install will also setup the command line utility.

.. code-block:: console

   pip install pylive-played-clip

Using
=====

To use, Ableton should already be up and running. Then from a console launch
pylive-played-clip as shown below.

.. code-block:: console

   pylive-played-clip

If you installed on Windows as a regular user, the command line script will
not be setup because of permissions issues, but you can still launch it by
calling python first as shown below.

.. code-block:: console

   python -m pylive_played_clip

Command Line Options
--------------------

The command line utility has the following options:

* **--dim-color FFFFFF**: This is the fixed color that played clips should receive.
  We're using the standard web notation for colors without the leading '#' symbol.
* **--dim-ratio 2**: If a dim-color is not specified, we'll take the original color
  and in the HSB space divide the brightness by this number. A value of 2 should
  reduce the brightness of the clip by half, but have the same hue and saturation.
* **--polling-delay**: The utility will scan all of the tracks for playing clips,
  wait this amount of time, and then re-scan. Should it detect that a clip was
  playing in the previous scan but not playing in the current scan, the color
  will be changed.

Examples
--------

All played clips will be set to dark gray:

.. code-block:: console

   pylive-played-clip --dim-color 555555

All played clips will be dimmed by 25%:

.. code-block:: console

   pylive-played-clip --dim-ratio 4
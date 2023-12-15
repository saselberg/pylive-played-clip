# pylive-played-clip.py

## Details

**Original Author:** [Scott Selberg](mailto:scott_selberg@keysight.com)  
**Current Owner:** [Scott Selberg](mailto:scott_selberg@keysight.com)  

## Introduction

This is a python package that deploys a command line tool to monitor
Ableton Live clips through [AbletonOSC](https://github.com/ideoforms/AbletonOSC) and
[pylive](https://github.com/ideoforms/pylive). When a clip finishes playing,
this utility can change the color to visually flag the clip as having been
played. When the global playback is stopped, the utility will reset all of the
clips to the color they had before it changed them.

This was developed for a talent show at [Foothills Elementary](https://foothills.asd20.org/).
We needed a way for an elementary student to control the sequencing of several
dozen sound clips. In the past we've used iTunes, but it was a bit unresponsive
and error prone. We'll be using a launchpad to trigger the clips and this
utility will be running in the background to dim the color of the clips as they
get played to make it easy to know which clips have been played and which
is the next clip to play.

There is a [similar utility](https://blog.abletondrummer.com/automatically-change-played-clips/)
created using MaxForLive created by AbletonDrummer. That 'device' costs $12
and I believe it requires [MaxForLive](https://www.ableton.com/en/live/max-for-live/)
or Ableton Live Suite which I think includes MaxForLive. I've only got the
free Ableton Live Lite license that came with the LaunchPad. The
[AbletonOSC](https://github.com/ideoforms/AbletonOSC) works fine with
Ableton Live Lite 11.

## How it works

[AbletonOSC](https://github.com/ideoforms/AbletonOSC]) is a MIDI remote script
that should be placed in Ableton's 'Remote Scripts' folder. As Ableton starts
up, it will launch the script. This creates a listener program on
the local computer where we can send messages that conform to the [Live Object
Model](https://docs.cycling74.com/max8/vignettes/live_object_model) and it
will convert them to the proper MIDI syntax and pass it into Ableton.

The same group that makes AbletonOSC also maintain a python library,
[pylive](https://github.com/ideoforms/pylive), that makes it easy to send
messages to the listener.

This project builds on top of [pylive](https://github.com/ideoforms/pylive)
to create a background program that will monitor Ableton and when a clip
finishes playing, it will change the color of that clip. The program can
either set the clip to a pre-defined value, such as dark grey, or it can
'dim' the original color.

## Installation

First, install Python version 3.8 or above. This is likely to be preinstalled
on a linux or MacOS machine. There are plenty of install instructions on the
internet for Windows.

Next, you will need to install [AbletonOSC](https://github.com/ideoforms/AbletonOSC).
This involves downloading a zip file and unpacking it into
``.../Ableton/User Library/Remote Scripts``.  On my system, I had to create the
directory ``Remote Scripts``, but the rest was created by Ableton. After
putting the files in place, I had to restart Ableton, locate the 'Link|Tempo|Midi'
preferences and add ``AbletonOSC`` as a controller. The
[AbletonOSC](https://github.com/ideoforms/AbletonOSC) home page has detailed
instructions on the process.

Lastly, you will need to install ``pylive-played-clip``.  The python package
creates a command line script that you can use to launch the utility.  On
Windows, it will only have permissions to setup the utility if you install the
package as an administrator.  On linux and macOS, the user install will also
setup the utility.

```console
> pip install pylive-played-clip
```

## Using

To use, Ableton should already be up and running. Then from a console launch
pylive-played-clip as shown below.

```console
> pylive-played-clip
```

If you installed on Windows as a regular user, the command line script will
not be setup because of permissions issues, but you can still launch it by
calling python first as shown below.

```console
> python -m pylive_played_clip
```

### Command Line Options

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

### Examples

All played clips will be set to dark gray:

```console
> pylive-played-clip --dim-color 555555
```

All played clips will be dimmed by 25%:

```console
> pylive-played-clip --dim-ratio 4
```

## License

BSD 3-Clause

## Author Information

Scott Selberg

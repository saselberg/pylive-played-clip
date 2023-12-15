# pylive-played-clip.py

## Details

**Original Author:** [Scott Selberg](mailto:scott_selberg@keysight.com)  
**Current Owner:** [Scott Selberg](mailto:scott_selberg@keysight.com)  

## Introduction

This is a python script to monitor Ableton Live through the AbletonOSC
utility to update the color of a clip after it has been played.

The way this works is we install AbletonOSC which creates a listener on
the local computer where we can send messages that will get to Ableton.
It is pretending to be a piece of hardware and will convert nice messages
to the MIDI syntax Ableton is expecting.

Then we start a second process on the computer which is constantly checking
with Ableton to see what tracks are playing.  When it discovers one has stopped
it will change it's color.

## Installation

First, install Python version 3.8 or above.

Next, install [AbletonOSC](https://github.com/ideoforms/AbletonOSC) and
enable it as a controller in Ableton Live.

Then, install pylive-played-clip which will also install pylive.

```console
> pip install pylive-played-clip
```

To use, start up Ableton, they from a console launch pylive-played-clip using
one of the following:

```console
> pylive-played-clip
```

or

```console
> python -m pylive_played_clip
```

## Using

```none
> pylive-played-clip
```

## License

BSD 3-Clause

## Author Information

Scott Selberg

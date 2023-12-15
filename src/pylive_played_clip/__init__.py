'''
The initialization code for the pylive_played_clip module
'''
__version_info__ = ('1', '1', '4')
__version__ = ".".join(__version_info__)
import logging
import re
import time

from typing import Dict, Optional, Tuple

import colorsys
import live  # type: ignore


def hexToRgb(hex: str) -> Tuple[int, int, int]:
    '''Converts a hex number without a leading # into an RGB triplet

    :param hex: The color hex value, such as FFFFFF.
    :type hex: str

    :returns: A tuple of the red, green and blue integer values.
    :rtype: typing.Tuple[int, int, int]

    Taken from https://stackoverflow.com/questions/29643352/converting-hex-to-rgb-value-in-python
    '''
    red: int = int(hex[0:2], 16)
    green: int = int(hex[2:4], 16)
    blue: int = int(hex[4:6], 16)
    return (red, green, blue)


def rgbToColorInt(red: int, green: int, blue: int) -> int:
    '''Converts a triplet of integers representing red,
    green and blue and returns a single integer.

    :param red: The red value between 0 and 255
    :type red: int
    :param green: The red value between 0 and 255
    :type green: int
    :param blue: The blue value between 0 and 255
    :type blue: int

    :returns: An integer representing all three values
    :rtype: int
    '''
    return (2**16 * red) + (2**8 * green) + blue


def colorIntToRgb(color: int) -> Tuple[int, int, int]:
    '''Converts a single integer representing a color into
    a triplet of integers representing the red, green and blue values.

    :param color: The single integer representing the color.
    :type color: int

    :returns: A tuple of integers representing the red, green and blue values.
    :rtype: typing.Tuple[int, int, int]
    '''
    red = (color & rgbToColorInt(255, 0, 0)) >> 16
    green = (color & rgbToColorInt(0, 255, 0)) >> 8
    blue = (color & rgbToColorInt(0, 0, 255))

    return (red, green, blue)


def colorIntToRgbString(color: int) -> str:
    '''Converts a single integer representing a color into
    a triplet of integers representing the red, green and blue values
    as a string that is easy to put into logs or print statements.

    :param color: The single integer representing the color.
    :type color: int

    :returns: A string showing the values for the red, green and blue values.
    :rtype: str
    '''
    (red, green, blue) = colorIntToRgb(color)
    return f"[{red}, {green}, {blue}]"


class AbletonClipMonitorException(Exception):
    '''Ableton Clip Monitor Exception Class'''
    pass


class AbletonClipMonitor():
    '''
    This class is used to manage the variables for monitoring Ableton.

    **Class Properties**

    * dim_color: Optional[str] - The color to dim to
    * dim_ratio: float - The ratio to dim to.
    * polling_delay: float - The delay between scans of the live set tracks.
    * polling_delay: float - The delay between scans of the live set tracks.
    * ableton: live.Set - The pylive Set object
    * num_of_tracks: int - The number of tracks in the live set.
    * original_cell_color: typing.Dict - A dictionary tracking the original
      color in the cells that have been changed.
    * dim_clip_on_track: typing.Dict - When a track starts to play, we make
      a record in this dictionary. When it is no longer playing, we know it
      is time to dim the clip.
    '''
    def __init__(
            self,
            dim_color: Optional[str] = None,
            dim_ratio: float = 2.0,
            polling_delay: float = 0.1,
            no_reset: bool = False) -> None:
        '''
        :param dim_color: The color, in hex such as FFFFFF, to dim to.
        :type dim_color: Optional[str]
        :param dim_ratio:
            The ratio to dim the color by. Should be greater or equal to 1.
            The RGB color will be converted to HSB, the brightness divided by
            this ratio, then converted back to RGB.
        :type dim_ratio: int
        :param polling_delay: The number of seconds between queries to Ableton
        :type polling_delay: float
        :param no_reset: If set to true, ableton will not be reset when it stops playing.
        :type no_reset: bool

        :returns: An instance of the AbletonClipMonitor object.
        :rtype: `AbletonClipMonitor`
        '''
        self.dim_color: Optional[str] = dim_color
        self.dim_ratio: float = dim_ratio
        self.polling_delay = polling_delay
        self.no_reset = no_reset
        self.ableton: live.Set = live.Set()
        self.num_of_tracks: int = 0

        if dim_color is not None and dim_color.startswith('#'):
            self.dim_color = dim_color[1:]

        self.original_cell_color: Dict = {}
        self.dim_clip_on_track: Dict = {}

        if not self.dim_color_is_valid(self.dim_color):
            raise AbletonClipMonitorException('The dim_color can be null or '
                                              'a six character string such as '
                                              'FFFFFF. We received '
                                              f"\"{self.dim_color}\".")

        if not self.dim_ratio_is_valid(self.dim_ratio):
            raise AbletonClipMonitorException('The dim_ratio cannot be 1 or '
                                              'less. We received '
                                              f"\"{self.dim_ratio}\".")

    def dim_color_is_valid(self, dim_color: Optional[str]) -> bool:
        '''Tests if the string defining the color is valid.

        :param dim_color: The dim color a a six character hex web color.
        :type dim_color: str

        :returns: A boolean indicating if the passed in dim_color is valid.
        :rtype: bool
        '''
        color_pattern = re.compile(r'^[0-9A-Fa-f]{6}$')
        color_ok: bool = False

        if dim_color is None:
            color_ok = True
        else:
            if color_pattern.match(dim_color):
                color_ok = True

        return color_ok

    def dim_ratio_is_valid(self, dim_ratio: float) -> bool:
        '''Tests if the dim_ratio value is valid.
        :param dim_ratio: The dim color a a six character hex web color.
        :type dim_ratio: float

        :returns: A boolean indicating if the passed in dim_ratio is valid.
        :rtype: bool
        '''
        ratio_is_ok: bool = False
        if self.dim_ratio >= 1.0:
            ratio_is_ok = True

        return ratio_is_ok

    def get_number_of_tracks(self) -> int:
        '''Queries Ableton to get the number of tracks in the open set.

        :returns: The number of tracks in the live set.
        :type: int
        '''
        num_tracks: int = self.ableton.live.query('/live/song/get/num_tracks')[0]
        return num_tracks

    def capture_playing_clip_info(
            self,
            track_index: int,
            playing_clip_index: int) -> None:
        '''Records the information of the currently playing clip.

        :param track_index: The index of the live set track to query.
        :type track_index: int
        :param playing_clip_index: The index of the clip in the live set track to query.
        :type playing_clip_index: int

        :returns: Nothing
        :rtype: None
        '''
        if not self.dim_clip_on_track.get(track_index):
            cell_index = f"{track_index}.{playing_clip_index}"
            color = self.get_clip_color(track_index, playing_clip_index)

            print(f"Playing track {track_index}, clip {playing_clip_index} with color {colorIntToRgbString(color)}")
            self.dim_clip_on_track[track_index] = {'clip_index': playing_clip_index, 'color': color}

            if cell_index not in self.original_cell_color:
                self.original_cell_color[cell_index] = color

    def dim_color_of_played_clip(self, track_index: int) -> None:
        '''Records the information of the currently playing clip.

        :param track_index: The index of the live set track to query.
        :type track_index: int

        :returns: Nothing
        :rtype: None
        '''
        if self.dim_clip_on_track.get(track_index):

            if self.dim_color:
                (red, green, blue) = hexToRgb(self.dim_color)
                dim_color = rgbToColorInt(red, green, blue)
            else:
                dim_color = self.get_dimmed_color_int_from_ratio(track_index)

            print(f"Dimming track {track_index}, clip {self.dim_clip_on_track[track_index]['clip_index']} to color {colorIntToRgbString(dim_color)}")
            self.ableton.live.cmd(
                '/live/clip/set/color',
                (track_index,
                 self.dim_clip_on_track[track_index]['clip_index'],
                 dim_color))
            self.dim_clip_on_track[track_index] = None

    def get_dimmed_color_int_from_ratio(self, track_index) -> int:
        '''Get the color we should dim to based on the recorded clip color
        and the dim_ratio.

        :param track_index: The index of the live set track to query.
        :type track_index: int

        :returns: Nothing
        :rtype: None
        '''
        (red, green, blue) = colorIntToRgb(self.dim_clip_on_track[track_index]['color'])
        (hue, lightness, saturation) = colorsys.rgb_to_hls(red, green, blue)
        (dim_red, dim_green, dim_blue) = colorsys.hls_to_rgb(hue, lightness/self.dim_ratio, saturation)
        return rgbToColorInt(int(dim_red), int(dim_green), int(dim_blue))

    def get_clip_color(self, track_index: int, playing_clip_index: int) -> int:
        '''Queries Ableton for the clip color.

        :param track_index: The index of the live set track to query.
        :type track_index: int
        :param playing_clip_index: The index of the clip in the live set track to query.
        :type playing_clip_index: int

        :returns: The clip color as a integer.
        :rtype: int
        '''
        return int(self.ableton.live.query('/live/clip/get/color', (track_index, playing_clip_index))[2])

    def restore_clip_colors(self) -> None:
        '''Restores the clips to their original colors.

        :returns: Nothing
        :rtype: None
        '''
        logging.debug('Reset colors')
        for cell in self.original_cell_color:
            (track_index, clip_index) = cell.split('.')
            print(f"Reset color of track {track_index}, clip {clip_index} to original color {colorIntToRgbString(self.original_cell_color[cell])}")
            self.ableton.live.cmd('/live/clip/set/color', (track_index, clip_index, self.original_cell_color[cell]))

        self.original_cell_color = {}

    def scan_tracks(self) -> None:
        '''Scans all of the tracks for clips that have started to play or
        stopped and need to be dimmed.

        :returns: Nothing
        :rtype: None
        '''
        for track_index in range(self.num_tracks):
            self.scan_track(track_index)

    def scan_track(self, track_index: int) -> None:
        '''Scans a single tracks for clips that have started to play or
        stopped and need to be dimmed.

        :param track_index: The index of the live set track to query.
        :type track_index: int

        :returns: Nothing
        :rtype: None
        '''
        logging.debug(f"Check track {track_index}")
        playing_clip_index = self.ableton.live.query('/live/track/get/playing_slot_index', (track_index,))[1]

        logging.debug(f"Playing clip {playing_clip_index}")
        dim_clip_info: Optional[Dict] = self.dim_clip_on_track.get(track_index)
        if isinstance(dim_clip_info, Dict) and self.should_dim_clip_that_just_ended(track_index, playing_clip_index):
            logging.debug(f"Dim clip color {track_index}:{playing_clip_index}:{dim_clip_info.get('clip_index')}")
            self.dim_color_of_played_clip(track_index)

        if playing_clip_index >= 0:
            logging.debug(f"Capture clip info {track_index}:{playing_clip_index}")
            self.capture_playing_clip_info(track_index, playing_clip_index)

    def should_dim_clip_that_just_ended(
            self,
            track_index: int,
            playing_clip_index: int) -> bool:
        '''Tests if a track should be dimmed.

        :param track_index: The index of the live set track to query.
        :type track_index: int
        :param playing_clip_index: The index of the clip in the live set track to query.
        :type playing_clip_index: int

        :returns: A boolean indicating if the track should be dimmed
        :rtype: bool
        '''
        dim_clip_info: Optional[Dict] = self.dim_clip_on_track.get(track_index)
        return (dim_clip_info is not None
                and playing_clip_index != dim_clip_info.get('clip_index'))

    def monitor(self) -> None:
        '''The main routine

        :returns: Nothing
        :rtype: None
        '''
        self.num_tracks = self.get_number_of_tracks()
        print('Monitoring Ableton')
        print('press ctrl-c to exit')
        logging.debug(f"There are {self.num_tracks} tracks.")

        try:
            while True:
                if self.ableton.is_playing:
                    self.scan_tracks()
                elif self.original_cell_color and not self.no_reset:
                    self.restore_clip_colors()

                time.sleep(float(self.polling_delay))
        except KeyboardInterrupt:
            pass

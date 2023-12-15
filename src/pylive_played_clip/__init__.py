'''
The initialization code for the pylive_played_clip module
'''
__version_info__ = ('1', '0', '1')
__version__ = ".".join(__version_info__)
import logging
import re
import time

from typing import Dict, Optional, Tuple

import colorsys
import live


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

    Class Properties
    ----------------

    * dim_color: Optional[str] - The color to dim to
    * dim_ratio: int - The ratio to dim to.
    '''
    def __init__(
            self,
            dim_color: Optional[str] = None,
            dim_ratio: float = 2.0,
            polling_delay: float = 0.1) -> None:
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
        '''
        self.dim_color: Optional[str] = dim_color
        self.dim_ratio: float = dim_ratio
        self.polling_delay = polling_delay
        self.ableton: live.Set = live.Set()
        self.num_of_tracks: int = 0

        self.original_cell_color: Dict = {}
        self.dim_clip_on_track: Dict = {}

        if not self.dim_color_is_valid():
            raise AbletonClipMonitorException('The dim_color can be null or '
                                              'a six character string such as '
                                              'FFFFFF. We received '
                                              f"\"{self.dim_color}\".")

        if not self.dim_ratio_is_valid():
            raise AbletonClipMonitorException('The dim_ratio cannot be 1 or '
                                              'less. We received '
                                              f"\"{self.dim_ratio}\".")

    def dim_color_is_valid(self) -> bool:
        color_pattern = re.compile(r'^[0-9A-Fa-f]{6}$')
        color_ok: bool = False

        if self.dim_color is None:
            color_ok = True
        else:
            if color_pattern.match(self.dim_color):
                color_ok = True

        return color_ok

    def dim_ratio_is_valid(self) -> bool:
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
        (red, green, blue) = colorIntToRgb(self.dim_clip_on_track[track_index]['color'])
        (hue, lightness, saturation) = colorsys.rgb_to_hls(red, green, blue)
        (dim_red, dim_green, dim_blue) = colorsys.hls_to_rgb(hue, lightness/self.dim_ratio, saturation)
        return rgbToColorInt(int(dim_red), int(dim_green), int(dim_blue))

    def get_clip_color(self, track_index: int, playing_clip_index: int) -> int:
        '''Queries Ableton for the clip color.

        :returns: The clip color as a integer.
        :rtype: int
        '''
        return int(self.ableton.live.query('/live/clip/get/color', (track_index, playing_clip_index))[2])

    def restore_clip_colors(self) -> None:
        '''Restores the clips to their original colors.
        '''
        logging.debug('Reset colors')
        for cell in self.original_cell_color:
            (track_index, clip_index) = cell.split('.')
            print(f"Reset color of track {track_index}, clip {clip_index} to original color {colorIntToRgbString(self.original_cell_color[cell])}")
            self.ableton.live.cmd('/live/clip/set/color', (track_index, clip_index, self.original_cell_color[cell]))

        self.original_cell_color = {}

    def check_tracks(self) -> None:
        for track_index in range(self.num_tracks):
            self.check_track(track_index)

    def check_track(self, track_index: int) -> None:
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
        dim_clip_info: Optional[Dict] = self.dim_clip_on_track.get(track_index)
        return (dim_clip_info is not None
                and (playing_clip_index < 0
                     or playing_clip_index != dim_clip_info.get('clip_index')))

    def monitor(self) -> None:
        '''The main routine'''

        self.num_tracks = self.get_number_of_tracks()
        logging.debug(f"There are {self.num_tracks} tracks.")

        try:
            while True:
                if self.ableton.is_playing:
                    self.check_tracks()
                elif self.original_cell_color:
                    self.restore_clip_colors()

                time.sleep(float(self.polling_delay))
        except KeyboardInterrupt:
            pass

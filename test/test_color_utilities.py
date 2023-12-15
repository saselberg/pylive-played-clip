#!/usr/bin/python3
import enable_imports_from_src_folder  # noqa: F401
import pylive_played_clip


def test_hex_to_rgb_ffffff() -> None:
    hex_color: str = 'ffffff'
    expected_red: int = 255
    expected_green: int = 255
    expected_blue: int = 255

    _hex_to_rgb(hex_color, expected_red, expected_green, expected_blue)


def test_hex_to_rgb_ff0000() -> None:
    hex_color: str = 'ff0000'
    expected_red: int = 255
    expected_green: int = 0
    expected_blue: int = 0

    _hex_to_rgb(hex_color, expected_red, expected_green, expected_blue)


def test_hex_to_rgb_00ff00() -> None:
    hex_color: str = '00ff00'
    expected_red: int = 0
    expected_green: int = 255
    expected_blue: int = 0

    _hex_to_rgb(hex_color, expected_red, expected_green, expected_blue)


def test_hex_to_rgb_0000ff() -> None:
    hex_color: str = '0000ff'
    expected_red: int = 0
    expected_green: int = 0
    expected_blue: int = 255

    _hex_to_rgb(hex_color, expected_red, expected_green, expected_blue)


def test_hex_to_rgb_000000() -> None:
    hex_color: str = '000000'
    expected_red: int = 0
    expected_green: int = 0
    expected_blue: int = 0

    _hex_to_rgb(hex_color, expected_red, expected_green, expected_blue)


def test_color_int_ffffff() -> None:
    red: int = 255
    green: int = 255
    blue: int = 255

    _rgb_to_color_to_rgb(red, green, blue)


def test_color_int_ff0000() -> None:
    red: int = 255
    green: int = 0
    blue: int = 0

    _rgb_to_color_to_rgb(red, green, blue)


def test_color_int_00ff00() -> None:
    red: int = 0
    green: int = 255
    blue: int = 0

    _rgb_to_color_to_rgb(red, green, blue)


def test_color_int_0000ff() -> None:
    red: int = 0
    green: int = 0
    blue: int = 255

    _rgb_to_color_to_rgb(red, green, blue)


def test_color_int_000000() -> None:
    red: int = 0
    green: int = 0
    blue: int = 0

    _rgb_to_color_to_rgb(red, green, blue)


def _hex_to_rgb(
        hex_color: str,
        expected_red: int,
        expected_green: int,
        expected_blue: int) -> None:

    (red, green, blue) = pylive_played_clip.hexToRgb(hex_color)

    assert expected_red == red
    assert expected_green == green
    assert expected_blue == blue


def _rgb_to_color_to_rgb(red: int, green: int, blue: int) -> None:
    color_integer = pylive_played_clip.rgbToColorInt(red, green, blue)
    (red_from_int, green_from_int, blue_from_int) = pylive_played_clip.colorIntToRgb(color_integer)

    assert red == red_from_int
    assert green == green_from_int
    assert blue == blue_from_int

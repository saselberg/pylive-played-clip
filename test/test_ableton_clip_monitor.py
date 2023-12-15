#!/usr/bin/python3
import pytest

import enable_imports_from_src_folder  # noqa: F401

from pylive_played_clip import AbletonClipMonitor, AbletonClipMonitorException


def test_ableton_clip_monitor_constructor_upper() -> None:
    dim_color: str = 'FF0000'
    dim_ratio: float = 4
    ableton_monitor: AbletonClipMonitor = AbletonClipMonitor(
        dim_color=dim_color,
        dim_ratio=dim_ratio)

    assert ableton_monitor.dim_color == dim_color
    assert ableton_monitor.dim_ratio == dim_ratio


def test_ableton_clip_monitor_constructor_lower() -> None:
    dim_color: str = 'ff0000'
    dim_ratio: float = 4
    ableton_monitor: AbletonClipMonitor = AbletonClipMonitor(
        dim_color=dim_color,
        dim_ratio=dim_ratio)

    assert ableton_monitor.dim_color == dim_color
    assert ableton_monitor.dim_ratio == dim_ratio


def test_ableton_clip_monitor_constructor_with_ratio_error() -> None:
    dim_ratio: float = 0.1
    with pytest.raises(AbletonClipMonitorException):
        _: AbletonClipMonitor = AbletonClipMonitor(dim_ratio=dim_ratio)


def test_ableton_clip_monitor_constructor_with_color_to_large_error() -> None:
    dim_color: str = 'FFFFFF0'
    with pytest.raises(AbletonClipMonitorException):
        _: AbletonClipMonitor = AbletonClipMonitor(dim_color=dim_color)


def test_ableton_clip_monitor_constructor_with_color_to_small_error() -> None:
    dim_color: str = 'FFFFF'
    with pytest.raises(AbletonClipMonitorException):
        _: AbletonClipMonitor = AbletonClipMonitor(dim_color=dim_color)


def test_ableton_clip_monitor_constructor_with_color_bad_characters_error() -> None:
    dim_color: str = 'FFFFFJ'
    with pytest.raises(AbletonClipMonitorException):
        _: AbletonClipMonitor = AbletonClipMonitor(dim_color=dim_color)

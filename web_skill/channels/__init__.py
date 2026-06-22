# -*- coding: utf-8 -*-
"""Channel registry — add a channel = import it and append to ALL_CHANNELS."""
from typing import List

from .base import Channel
from .reddit import RedditChannel
from .video_transcript import VideoTranscriptChannel
from .xiaohongshu import XiaoHongShuChannel

ALL_CHANNELS: List[Channel] = [
    VideoTranscriptChannel(),
    XiaoHongShuChannel(),
    RedditChannel(),
]


def get_all_channels() -> List[Channel]:
    return ALL_CHANNELS

"""Channel registry. Add a channel = import it and add to CHANNELS."""
from .video_transcript import VideoTranscript
from .xiaohongshu import Xiaohongshu

CHANNELS = [
    VideoTranscript(),
    Xiaohongshu(),
]

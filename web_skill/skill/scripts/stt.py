# /// script
# requires-python = ">=3.10"
# dependencies = ["mlx-whisper", "mlx-audio>=0.4.4"]
# ///
"""Transcribe an audio file on Apple Silicon GPU.

Usage: uv run stt.py <audio-file> [lang]
- lang=zh: Qwen3-ASR 1.7B 4bit (27x realtime, best Chinese accuracy)
- lang=anything else / auto-detect: Whisper large-v3-turbo
Requires ffmpeg on PATH.
"""
import subprocess, sys, tempfile, time
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("usage: uv run stt.py <audio-file> [lang]")

audio = sys.argv[1]
lang  = sys.argv[2] if len(sys.argv) > 2 else None

if lang == "zh":
    from mlx_audio.stt import load_model

    CHUNK_SEC = 30

    def get_duration(path):
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True, text=True)
        return float(r.stdout.strip())

    def extract_chunk(src, start, dur, dst):
        subprocess.run(
            ["ffmpeg", "-ss", str(start), "-t", str(dur), "-i", src,
             "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", dst, "-y", "-loglevel", "error"],
            check=True)

    model    = load_model("mlx-community/Qwen3-ASR-1.7B-4bit")
    duration = get_duration(audio)
    parts    = []

    with tempfile.TemporaryDirectory() as tmp:
        start = 0; i = 0
        while start < duration:
            chunk = f"{tmp}/chunk_{i:04d}.wav"
            extract_chunk(audio, start, CHUNK_SEC, chunk)
            result = model.generate(chunk, language="zh")
            parts.append((result.text if hasattr(result, "text") else str(result)).strip())
            start += CHUNK_SEC; i += 1

    print(" ".join(p for p in parts if p))

else:
    import mlx_whisper
    result = mlx_whisper.transcribe(
        audio,
        path_or_hf_repo="mlx-community/whisper-large-v3-turbo",
        language=lang,
    )
    print(result["text"])

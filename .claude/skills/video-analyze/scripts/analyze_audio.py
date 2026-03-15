#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_audio.py - Analyze audio from video or audio files using ffmpeg.

Usage:
  python analyze_audio.py <file_path> [options]

Modes:
  --info-only              Print audio metadata only
  --waveform               Generate a waveform PNG image
  --transcribe             Transcribe audio using Whisper
  --model <name>           Whisper model size: tiny, base, small, medium, large
                           (default: base)

Common options:
  --output-dir <path>      Where to save output files (default: temp directory)

Output: JSON to stdout
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        subprocess.run(["ffprobe", "-version"], capture_output=True, check=True)
    except FileNotFoundError:
        print(
            json.dumps({
                "error": "ffmpeg/ffprobe not found. Install it with:\n"
                         "  macOS:   brew install ffmpeg\n"
                         "  Linux:   sudo apt install ffmpeg\n"
                         "  Windows: winget install ffmpeg"
            })
        )
        sys.exit(1)


def get_audio_info(file_path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"error": f"ffprobe failed: {result.stderr.strip()}"}

    probe = json.loads(result.stdout)
    audio_stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "audio"),
        None,
    )
    fmt = probe.get("format", {})

    if audio_stream is None:
        return {"error": "No audio stream found in file."}

    duration = float(fmt.get("duration") or audio_stream.get("duration") or 0)
    sample_rate = int(audio_stream.get("sample_rate") or 0)
    channels = int(audio_stream.get("channels") or 0)
    codec = audio_stream.get("codec_name", "unknown")
    bitrate = fmt.get("bit_rate")
    if bitrate:
        bitrate = f"{int(bitrate) // 1000}k"

    return {
        "file_path": str(file_path),
        "duration_seconds": round(duration, 3),
        "codec": codec,
        "sample_rate": sample_rate,
        "channels": channels,
        "bitrate": bitrate,
    }


def generate_waveform(file_path: Path, output_dir: Path) -> Optional[str]:
    """Generate a waveform PNG using ffmpeg's showwavespic filter."""
    out_file = output_dir / "waveform.png"
    result = subprocess.run(
        [
            "ffmpeg",
            "-i", str(file_path),
            "-filter_complex",
            "aformat=channel_layouts=mono,showwavespic=s=1280x240:colors=#4A90D9",
            "-frames:v", "1",
            "-y",
            str(out_file),
        ],
        capture_output=True,
    )
    if result.returncode == 0 and out_file.exists():
        return str(out_file)
    return None


def transcribe_audio(
    file_path: Path,
    output_dir: Path,
    model: str = "base",
) -> dict:
    """
    Transcribe audio using openai-whisper.
    Returns {"transcript": "...", "segments": [...]} or {"error": "..."}
    """
    try:
        import whisper  # type: ignore
    except ImportError:
        return {
            "error": (
                "openai-whisper is not installed. Install it with:\n"
                "  pip install openai-whisper\n"
                "Note: Requires ffmpeg to be installed as well."
            )
        }

    try:
        wmodel = whisper.load_model(model)
        result = wmodel.transcribe(str(file_path))
        transcript = result.get("text", "").strip()
        segments = [
            {
                "start": round(s["start"], 2),
                "end": round(s["end"], 2),
                "text": s["text"].strip(),
            }
            for s in result.get("segments", [])
        ]
        return {"transcript": transcript, "segments": segments}
    except Exception as e:
        return {"error": f"Whisper transcription failed: {e}"}


def main():
    parser = argparse.ArgumentParser(
        description="Analyze audio from a video or audio file using ffmpeg."
    )
    parser.add_argument("file_path", help="Path to the video or audio file")
    parser.add_argument("--info-only", action="store_true", help="Print metadata only")
    parser.add_argument("--waveform", action="store_true", help="Generate waveform PNG")
    parser.add_argument(
        "--transcribe", action="store_true",
        help="Transcribe audio using Whisper"
    )
    parser.add_argument(
        "--model", default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument("--output-dir", help="Directory to save output files")

    args = parser.parse_args()

    check_ffmpeg()

    file_path = Path(args.file_path)
    if not file_path.exists():
        print(json.dumps({"error": f"File not found: {file_path}"}))
        sys.exit(1)

    info = get_audio_info(file_path)
    if "error" in info:
        print(json.dumps(info))
        sys.exit(1)

    if args.info_only:
        print(json.dumps(info, indent=2))
        return

    # Set up output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(tempfile.mkdtemp(prefix="video-audio-"))

    result = {**info, "output_dir": str(output_dir)}

    if args.waveform:
        waveform_path = generate_waveform(file_path, output_dir)
        if waveform_path:
            result["waveform_path"] = waveform_path
        else:
            result["waveform_error"] = "Failed to generate waveform PNG."

    if args.transcribe:
        transcription = transcribe_audio(file_path, output_dir, model=args.model)
        if "error" in transcription:
            result["transcription_error"] = transcription["error"]
        else:
            result["transcript"] = transcription["transcript"]
            result["segments"] = transcription["segments"]

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

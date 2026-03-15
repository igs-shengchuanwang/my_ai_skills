#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_frames.py - Extract frames from video files using ffmpeg.

Usage:
  python extract_frames.py <video_path> [options]

Modes:
  --info-only              Print video metadata without extracting frames
  --frames 0 30 60 90      Extract specific frame indices
  --time-start T --time-end T [--sample-count N]
                           Extract N frames evenly spaced in a time range
  --keyframes [--sample-count N]
                           Extract keyframes (scene changes) only

Common options:
  --output-dir <path>      Where to save PNGs (default: temp directory)

Output: JSON to stdout
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def check_ffmpeg():
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True,
        )
        subprocess.run(
            ["ffprobe", "-version"],
            capture_output=True,
            check=True,
        )
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


def get_video_info(video_path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(video_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return {"error": f"ffprobe failed: {result.stderr.strip()}"}

    probe = json.loads(result.stdout)

    video_stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "video"),
        None,
    )
    audio_stream = next(
        (s for s in probe.get("streams", []) if s.get("codec_type") == "audio"),
        None,
    )
    fmt = probe.get("format", {})

    if video_stream is None:
        return {"error": "No video stream found in file."}

    # FPS: stored as fraction string e.g. "30/1" or "30000/1001"
    fps_raw = video_stream.get("r_frame_rate", "0/1")
    try:
        num, den = fps_raw.split("/")
        fps = float(num) / float(den) if float(den) != 0 else 0.0
    except Exception:
        fps = 0.0

    duration = float(fmt.get("duration") or video_stream.get("duration") or 0)
    total_frames_raw = video_stream.get("nb_frames")
    if total_frames_raw and total_frames_raw != "N/A":
        total_frames = int(total_frames_raw)
    else:
        total_frames = int(duration * fps) if fps > 0 else 0

    width = video_stream.get("width", 0)
    height = video_stream.get("height", 0)
    codec = video_stream.get("codec_name", "unknown")

    return {
        "video_path": str(video_path),
        "duration_seconds": round(duration, 3),
        "total_frames": total_frames,
        "fps": round(fps, 3),
        "resolution": [width, height],
        "codec": codec,
        "has_audio": audio_stream is not None,
    }


def frame_index_to_time(index: int, fps: float) -> float:
    return index / fps if fps > 0 else 0.0


def extract_by_indices(
    video_path: Path,
    frame_indices: list[int],
    fps: float,
    output_dir: Path,
) -> list[dict]:
    extracted = []
    for idx in frame_indices:
        t = frame_index_to_time(idx, fps)
        out_file = output_dir / f"frame_{idx:06d}.png"
        result = subprocess.run(
            [
                "ffmpeg",
                "-ss", str(t),
                "-i", str(video_path),
                "-frames:v", "1",
                "-q:v", "2",
                "-y",
                str(out_file),
            ],
            capture_output=True,
        )
        if result.returncode == 0 and out_file.exists():
            extracted.append({
                "index": idx,
                "time_seconds": round(t, 3),
                "path": str(out_file),
            })
    return extracted


def extract_by_time_range(
    video_path: Path,
    time_start: float,
    time_end: float,
    sample_count: int,
    fps: float,
    output_dir: Path,
) -> list[dict]:
    if sample_count <= 1:
        timestamps = [time_start]
    else:
        step = (time_end - time_start) / (sample_count - 1)
        timestamps = [time_start + i * step for i in range(sample_count)]

    extracted = []
    for t in timestamps:
        frame_idx = int(t * fps) if fps > 0 else 0
        out_file = output_dir / f"frame_{frame_idx:06d}.png"
        result = subprocess.run(
            [
                "ffmpeg",
                "-ss", str(t),
                "-i", str(video_path),
                "-frames:v", "1",
                "-q:v", "2",
                "-y",
                str(out_file),
            ],
            capture_output=True,
        )
        if result.returncode == 0 and out_file.exists():
            extracted.append({
                "index": frame_idx,
                "time_seconds": round(t, 3),
                "path": str(out_file),
            })
    return extracted


def extract_keyframes(
    video_path: Path,
    sample_count: int,
    output_dir: Path,
    fps: float,
) -> list[dict]:
    """Extract keyframes (I-frames) using ffmpeg's select filter."""
    pattern = output_dir / "keyframe_%06d.png"
    result = subprocess.run(
        [
            "ffmpeg",
            "-i", str(video_path),
            "-vf", "select=eq(pict_type\\,I)",
            "-vsync", "vfr",
            "-q:v", "2",
            "-y",
            str(pattern),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        return []

    # Collect all extracted keyframes
    keyframe_files = sorted(output_dir.glob("keyframe_*.png"))

    # Sub-sample if more than requested
    if sample_count and len(keyframe_files) > sample_count:
        indices = [
            int(i * (len(keyframe_files) - 1) / (sample_count - 1))
            for i in range(sample_count)
        ]
        keyframe_files = [keyframe_files[i] for i in indices]

    extracted = []
    for f in keyframe_files:
        # Estimate time from filename index
        num_str = f.stem.replace("keyframe_", "")
        try:
            seq = int(num_str)
        except ValueError:
            seq = 0
        extracted.append({
            "index": seq,
            "time_seconds": None,  # exact time not trivially available
            "path": str(f),
        })
    return extracted


def default_sample(
    video_path: Path,
    info: dict,
    sample_count: int,
    output_dir: Path,
) -> list[dict]:
    """Sample N frames evenly across the full video duration."""
    duration = info["duration_seconds"]
    fps = info["fps"]
    return extract_by_time_range(
        video_path,
        time_start=0.0,
        time_end=duration,
        sample_count=sample_count,
        fps=fps,
        output_dir=output_dir,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Extract frames from a video file using ffmpeg."
    )
    parser.add_argument("video_path", help="Path to the video file")
    parser.add_argument("--info-only", action="store_true", help="Print metadata only")
    parser.add_argument(
        "--frames", nargs="+", type=int, metavar="N",
        help="Frame indices to extract"
    )
    parser.add_argument("--time-start", type=float, help="Start time in seconds")
    parser.add_argument("--time-end", type=float, help="End time in seconds")
    parser.add_argument(
        "--sample-count", type=int, default=6,
        help="Number of frames to sample (default: 6)"
    )
    parser.add_argument(
        "--keyframes", action="store_true",
        help="Extract keyframes (scene-change I-frames) only"
    )
    parser.add_argument("--output-dir", help="Directory to save PNG files")

    args = parser.parse_args()

    check_ffmpeg()

    video_path = Path(args.video_path)
    if not video_path.exists():
        print(json.dumps({"error": f"File not found: {video_path}"}))
        sys.exit(1)

    info = get_video_info(video_path)
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
        output_dir = Path(tempfile.mkdtemp(prefix="video-frames-"))

    # Extract frames based on mode
    fps = info["fps"]
    extracted = []

    if args.frames:
        extracted = extract_by_indices(video_path, args.frames, fps, output_dir)
    elif args.keyframes:
        extracted = extract_keyframes(video_path, args.sample_count, output_dir, fps)
    elif args.time_start is not None and args.time_end is not None:
        if args.time_start >= args.time_end:
            print(json.dumps({"error": "--time-start must be less than --time-end"}))
            sys.exit(1)
        extracted = extract_by_time_range(
            video_path, args.time_start, args.time_end,
            args.sample_count, fps, output_dir
        )
    else:
        # Default: sample evenly across full duration
        extracted = default_sample(video_path, info, args.sample_count, output_dir)

    result = {
        **info,
        "output_dir": str(output_dir),
        "extracted_frames": extracted,
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

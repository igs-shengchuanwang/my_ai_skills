#!/usr/bin/env python3
"""Extract specific frames from a GIF file as PNG images."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print(json.dumps({"error": "Pillow is not installed. Run: pip install Pillow"}))
    sys.exit(1)


def get_gif_info(gif_path: str) -> dict:
    """Get metadata about a GIF file."""
    img = Image.open(gif_path)

    total_frames = 0
    durations = []
    try:
        while True:
            duration_ms = img.info.get("duration", 100)  # default 100ms per frame
            durations.append(duration_ms)
            total_frames += 1
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    total_duration_ms = sum(durations)
    total_duration_s = total_duration_ms / 1000.0
    fps = total_frames / total_duration_s if total_duration_s > 0 else 0

    return {
        "gif_path": str(gif_path),
        "total_frames": total_frames,
        "duration_seconds": round(total_duration_s, 3),
        "fps": round(fps, 2),
        "size": list(img.size),
        "frame_durations_ms": durations,
    }


def time_to_frame_indices(info: dict, time_start: float, time_end: float, sample_count: int) -> list[int]:
    """Convert a time range to evenly-spaced frame indices."""
    durations = info["frame_durations_ms"]
    total_frames = info["total_frames"]

    # Build cumulative time for each frame's start
    cum_time = [0.0]
    for d in durations:
        cum_time.append(cum_time[-1] + d / 1000.0)

    # Find frames within the time range
    candidates = []
    for i in range(total_frames):
        frame_start = cum_time[i]
        frame_end = cum_time[i + 1]
        if frame_end > time_start and frame_start < time_end:
            candidates.append(i)

    if not candidates:
        return []

    if len(candidates) <= sample_count:
        return candidates

    # Evenly sample from candidates
    step = (len(candidates) - 1) / (sample_count - 1) if sample_count > 1 else 0
    indices = []
    for i in range(sample_count):
        idx = round(i * step)
        indices.append(candidates[idx])
    return indices


def extract_frames(gif_path: str, frame_indices: list[int], output_dir: str) -> list[dict]:
    """Extract specific frames from a GIF and save as PNGs."""
    img = Image.open(gif_path)
    os.makedirs(output_dir, exist_ok=True)

    results = []
    cum_time = 0.0
    frame_idx = 0
    target_set = set(frame_indices)

    try:
        while True:
            if frame_idx in target_set:
                # Convert to RGBA to handle transparency properly
                frame = img.convert("RGBA")
                filename = f"frame_{frame_idx:04d}.png"
                filepath = os.path.join(output_dir, filename)
                frame.save(filepath, "PNG")
                results.append({
                    "index": frame_idx,
                    "time_seconds": round(cum_time / 1000.0, 3),
                    "path": filepath,
                })

            duration_ms = img.info.get("duration", 100)
            cum_time += duration_ms
            frame_idx += 1
            img.seek(img.tell() + 1)
    except EOFError:
        pass

    # Sort by index
    results.sort(key=lambda x: x["index"])
    return results


def main():
    parser = argparse.ArgumentParser(description="Extract frames from a GIF file")
    parser.add_argument("gif_path", help="Path to the GIF file")
    parser.add_argument("--frames", type=int, nargs="+", help="Frame indices to extract")
    parser.add_argument("--time-start", type=float, help="Start time in seconds")
    parser.add_argument("--time-end", type=float, help="End time in seconds")
    parser.add_argument("--sample-count", type=int, default=5, help="Number of frames to sample in time range (default: 5)")
    parser.add_argument("--output-dir", type=str, help="Output directory for PNGs")
    parser.add_argument("--info-only", action="store_true", help="Only print GIF metadata")
    args = parser.parse_args()

    gif_path = args.gif_path
    if not os.path.isfile(gif_path):
        print(json.dumps({"error": f"File not found: {gif_path}"}))
        sys.exit(1)

    # Get GIF info
    info = get_gif_info(gif_path)

    if args.info_only:
        # Remove frame_durations_ms from output for cleaner display
        output = {k: v for k, v in info.items() if k != "frame_durations_ms"}
        print(json.dumps(output, indent=2))
        return

    # Determine which frames to extract
    if args.frames:
        frame_indices = [i for i in args.frames if 0 <= i < info["total_frames"]]
        if not frame_indices:
            print(json.dumps({"error": f"No valid frame indices. GIF has {info['total_frames']} frames (0-{info['total_frames']-1})."}))
            sys.exit(1)
    elif args.time_start is not None and args.time_end is not None:
        if args.time_start >= args.time_end:
            print(json.dumps({"error": "time-start must be less than time-end"}))
            sys.exit(1)
        frame_indices = time_to_frame_indices(info, args.time_start, args.time_end, args.sample_count)
        if not frame_indices:
            print(json.dumps({"error": f"No frames found in time range {args.time_start}s - {args.time_end}s"}))
            sys.exit(1)
    else:
        # Default: sample evenly across the whole GIF
        total = info["total_frames"]
        count = min(6, total)
        if count <= 1:
            frame_indices = [0]
        else:
            step = (total - 1) / (count - 1)
            frame_indices = [round(i * step) for i in range(count)]

    # Set output directory
    if args.output_dir:
        output_dir = args.output_dir
    else:
        output_dir = tempfile.mkdtemp(prefix="gif-frames-")

    # Extract
    extracted = extract_frames(gif_path, frame_indices, output_dir)

    # Build output
    output = {
        "gif_path": info["gif_path"],
        "total_frames": info["total_frames"],
        "duration_seconds": info["duration_seconds"],
        "fps": info["fps"],
        "size": info["size"],
        "output_dir": output_dir,
        "extracted_frames": extracted,
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

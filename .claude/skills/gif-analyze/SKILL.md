---
name: gif-analyze
description: Extract and visually analyze frames from GIF files. Use this skill whenever the user mentions analyzing a GIF, extracting GIF frames, inspecting GIF animation, viewing specific frames of a GIF, or provides a .gif file path and wants to understand its contents. Also trigger when the user asks about what's happening in a GIF, wants to compare frames, check animation quality, or debug GIF-related issues.
---

# GIF Frame Analyzer

Extract specific frames from a GIF file so Claude can see and analyze them visually.

## How It Works

1. Run the extraction script to pull frames out of the GIF as PNG images
2. Read the extracted PNGs with the Read tool (which supports viewing images)
3. Analyze the frames based on whatever the user is asking about

## Finding the Script

Use the Glob tool to locate the script at runtime (do NOT hardcode paths):

```
**/.claude/skills/gif-analyze/scripts/extract_frames.py
```

## Frame Extraction Script

### Usage

```bash
python <script_path> <gif_path> [options]
```

### Options

There are two modes for selecting frames. Pick whichever matches the user's request:

**Mode 1: By frame indices**
```bash
python <script_path> animation.gif --frames 0 5 10 20
```

**Mode 2: By time range (seconds)**
```bash
python <script_path> animation.gif --time-start 1.0 --time-end 3.5 --sample-count 5
```
This extracts `--sample-count` frames evenly spaced within the time window. Defaults to 5 if omitted.

**Common options:**
- `--output-dir <path>`: Where to save PNG files. Defaults to a temp directory.
- `--info-only`: Just print GIF metadata (total frames, duration, FPS) without extracting.

### Script Output

The script prints JSON to stdout:

```json
{
  "gif_path": "animation.gif",
  "total_frames": 48,
  "duration_seconds": 2.4,
  "fps": 20.0,
  "size": [320, 240],
  "output_dir": "/tmp/gif-frames-xxxxx",
  "extracted_frames": [
    {"index": 0, "time_seconds": 0.0, "path": "/tmp/gif-frames-xxxxx/frame_000.png"},
    {"index": 5, "time_seconds": 0.25, "path": "/tmp/gif-frames-xxxxx/frame_005.png"}
  ]
}
```

## Workflow

### Step 1: Get GIF info (optional but recommended for large GIFs)

Run with `--info-only` first to understand the GIF's structure — how many frames, total duration, FPS. This helps decide which frames to extract, and you can share this info with the user if they haven't specified exact frames.

### Step 2: Extract frames

Run the script with the appropriate mode. If the user said something like "show me frames 0, 10, 20", use `--frames`. If they said "show me what happens between second 2 and 4", use `--time-start` / `--time-end`.

If the user just says "analyze this GIF" without specifying frames, use `--info-only` first, then pick a reasonable sampling strategy — for example, 5-8 frames evenly spaced across the full duration. This gives a good overview without overwhelming the context.

### Step 3: Read the extracted frames

Use the Read tool to view each extracted PNG. Claude can see images natively, so just read them one by one. Read them in order so you can understand the animation sequence.

### Step 4: Analyze

Respond to whatever the user asked about. Since you can now see the frames, describe, compare, or analyze them based on the user's prompt. If the user hasn't asked a specific question, provide a general summary of what the GIF shows and how the animation progresses.

### Step 5: Saving frames (if requested)

By default, frames go to a temp directory. If the user wants to keep them, either:
- Re-run with `--output-dir` pointing to their desired location, or
- Copy the files from the temp directory to where they want them

Let the user know where the frames are saved.

## Tips

- For very long GIFs (100+ frames), avoid extracting all frames — sample intelligently
- When comparing frames, reading them sequentially helps spot differences
- The script handles disposal methods and transparency correctly via Pillow's frame iteration
- If Pillow is not installed, install it with `pip install Pillow`

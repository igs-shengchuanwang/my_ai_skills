---
name: video-analyze
description: Extract frames and analyze audio from video or audio files (.mp4, .mov, .mkv, .webm, .avi, .mp3, .wav, .aac, etc.). Use this skill when the user provides a video or audio file path and wants to understand its contents, analyze what's happening in the video, compare scenes, check video/audio quality, transcribe speech, or visualize the audio waveform. Also trigger when the user asks to extract frames from a video, inspect specific moments in a video, or debug video/audio issues.
---

# Video & Audio Analyzer

Extract frames and analyze audio from video or audio files so Claude can see and hear what's in them.

**Requires:** `ffmpeg` installed on the system.
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`
- Windows: `winget install ffmpeg`

**Optional for transcription:** `pip install openai-whisper`

---

## Finding the Scripts

Use the Glob tool to locate the scripts at runtime (do NOT hardcode paths):

```
**/.claude/skills/video-analyze/scripts/extract_frames.py
**/.claude/skills/video-analyze/scripts/analyze_audio.py
```

---

## Script 1: extract_frames.py

Extracts video frames as PNG images that Claude can read and analyze visually.

### Options

**Info only (recommended first step):**
```bash
python <script_path> <video_path> --info-only
```

**By frame indices:**
```bash
python <script_path> video.mp4 --frames 0 30 60 90
```

**By time range:**
```bash
python <script_path> video.mp4 --time-start 5.0 --time-end 15.0 --sample-count 6
```

**Keyframes only (scene changes):**
```bash
python <script_path> video.mp4 --keyframes --sample-count 10
```

**Common option:**
- `--output-dir <path>` — where to save PNGs (default: temp directory)

### Output JSON
```json
{
  "video_path": "video.mp4",
  "duration_seconds": 40.0,
  "total_frames": 1200,
  "fps": 30.0,
  "resolution": [1920, 1080],
  "codec": "h264",
  "has_audio": true,
  "output_dir": "/tmp/video-frames-xxxxx",
  "extracted_frames": [
    {"index": 0, "time_seconds": 0.0, "path": "/tmp/video-frames-xxxxx/frame_000000.png"}
  ]
}
```

---

## Script 2: analyze_audio.py

Analyzes the audio track of a video or an audio-only file.

### Options

**Info only:**
```bash
python <script_path> video.mp4 --info-only
```

**Waveform PNG:**
```bash
python <script_path> video.mp4 --waveform
```

**Transcription (Whisper):**
```bash
python <script_path> video.mp4 --transcribe --model base
```
Model sizes: `tiny` (fastest) → `base` → `small` → `medium` → `large` (most accurate)

**All at once:**
```bash
python <script_path> video.mp4 --waveform --transcribe --model small
```

**Common option:**
- `--output-dir <path>` — where to save output files

### Output JSON
```json
{
  "file_path": "video.mp4",
  "duration_seconds": 40.0,
  "codec": "aac",
  "sample_rate": 44100,
  "channels": 2,
  "bitrate": "128k",
  "output_dir": "/tmp/video-audio-xxxxx",
  "waveform_path": "/tmp/video-audio-xxxxx/waveform.png",
  "transcript": "Hello, welcome to this video...",
  "segments": [
    {"start": 0.0, "end": 2.5, "text": "Hello, welcome to this video."}
  ]
}
```

---

## Workflow

### Step 1: Get metadata

Always start with `--info-only` to understand the file:

```bash
python extract_frames.py video.mp4 --info-only
```

Share key info with the user if relevant (duration, resolution, fps, has_audio).

### Step 2: Extract frames

Choose the mode that fits the user's request:
- "show me frames 0, 100, 200" → `--frames 0 100 200`
- "what happens between second 10 and 20?" → `--time-start 10 --time-end 20`
- "show me scene changes" → `--keyframes`
- "analyze this video" (no specifics) → default mode (6 frames evenly spaced)

### Step 3: Analyze audio (if needed)

If the user asks about audio, speech, transcript, or sound:
- Run `--info-only` to confirm audio track exists
- Run `--waveform` to generate a waveform image
- Run `--transcribe` if they want the speech as text

### Step 4: Read extracted files

Use the Read tool to view each extracted PNG (frames and waveform). Read frames in order to understand the sequence.

### Step 5: Analyze and respond

Answer the user's question based on what you see. If no specific question was asked, provide:
- A summary of the video content based on the extracted frames
- Key moments or scene changes observed
- Audio transcript excerpt (if transcription was run)

---

## Tips

- For long videos (>5 min), use `--keyframes` or limit time ranges to avoid extracting too many frames
- Whisper `base` model is fast and good enough for most content; use `small` or `medium` for better accuracy with accented speech or technical content
- Waveform PNG is useful for understanding audio structure (silence gaps, speech patterns, music beats)
- If the user wants to keep the extracted files, re-run with `--output-dir` pointing to their desired location

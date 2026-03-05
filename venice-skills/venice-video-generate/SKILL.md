---
name: "venice-video-generate"
description: "Generate complete video from prompt to saved file in single operation. Handles queue, poll, retrieve, save with progress logging."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - video
  - generation
  - complete
  - text-to-video
  - image-to-video
trigger_patterns:
  - "generate video"
  - "create video"
  - "make video"
  - "video from prompt"
  - "text to video"
  - "image to video"
---

# Venice Video Generate (Full Lifecycle)

Generate complete video from prompt to saved file in a single operation.

## When to Use

Use this skill when you need to:
- Generate video from text prompt (text-to-video)
- Generate video from image (image-to-video)
- Complete video generation with automatic polling and saving

**This is the recommended approach** - it combines queue + poll + retrieve + save into one call.

## Usage

### Quick Start (Text-to-Video)
```bash
python /a0/usr/skills/venice-video-generate/scripts/generate_video.py "A cat playing piano"
```

### With Options
```bash
python /a0/usr/skills/venice-video-generate/scripts/generate_video.py "Ocean waves at sunset" \
  --model kling-2.6-pro-text-to-video \
  --duration 10s \
  --resolution 1080p
```

### Image-to-Video
```bash
python /a0/usr/skills/venice-video-generate/scripts/generate_video.py "Make this image come alive" \
  --image /path/to/image.png \
  --model wan-2.5-preview-image-to-video
```

## Progress Logging (Every 20 Seconds)

```
[14:32:15] START: Queueing video generation with model: wan-2.5-preview-text-to-video
[14:32:15] CONFIG: duration=5s, resolution=720p, aspect_ratio=16:9
[14:32:16] QUEUED: queue_id=abc123-def456
[14:32:36] PROGRESS: 20s elapsed | [====----------------] 25% | ETA: 45s | status: processing
[14:32:56] PROGRESS: 40s elapsed | [==========----------] 55% | ETA: 25s | status: processing
[14:33:16] PROGRESS: 60s elapsed | [================----] 85% | ETA: 8s | status: processing
[14:33:21] COMPLETE: Video saved to /root/venice_videos/video_20260131_143321_abc123.mp4
```

## Result Output

```
======================================================================
RESULT: SUCCESS
VIDEO_PATH: /root/venice_videos/video_20260131_143321_abc123.mp4
ELAPSED_SECONDS: 65.3
QUEUE_ID: abc123-def456-...
MODEL: wan-2.5-preview-text-to-video
======================================================================
```

## Common Options

| Option | Default | Description |
|--------|---------|-------------|
| --model, -m | wan-2.5-preview-text-to-video | Venice model ID |
| --duration, -d | 5s | Video duration (5s, 10s, etc.) |
| --resolution, -r | 720p | Video resolution |
| --aspect-ratio, -a | 16:9 | Aspect ratio (16:9, 9:16, 1:1) |
| --audio | off | Enable audio generation |
| --image, -i | none | Input image (for image-to-video) |
| --output, -o | auto | Custom output path |
| --max-wait | 900 | Max wait seconds (15 min) |

## Model Selection

### Text-to-Video
- `wan-2.5-preview-text-to-video` - Default, fast, good quality
- `kling-2.6-pro-text-to-video` - Higher quality, slower
- `veo3.1-full-text-to-video` - Google Veo, excellent but expensive

### Image-to-Video
- `wan-2.5-preview-image-to-video` - Fast, reliable
- `veo3.1-full-image-to-video` - Premium quality

## Expected Generation Times

| Model Type | 5s Video | 10s Video |
|------------|----------|----------|
| Wan 2.5 | 30-60s | 60-120s |
| Kling 2.6 Pro | 60-120s | 120-240s |
| Veo 3.1 | 90-180s | 180-360s |

## Python Import

```python
import sys
sys.path.insert(0, '/a0/usr/skills/venice-video-generate/scripts')
from generate_video import generate_video, GenerationResult

result = generate_video(
    prompt="A beautiful sunset over mountains",
    model="wan-2.5-preview-text-to-video",
    duration="5s",
    verbose=True
)

if result.success:
    print(f"Video saved: {result.video_path}")
else:
    print(f"Failed: {result.error}")
```

## Default Output Directory

`/root/venice_videos/` (auto-created)

## Requirements

- `VENICE_API_KEY` environment variable

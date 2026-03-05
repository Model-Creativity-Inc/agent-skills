---
name: "venice-video-queue"
description: "Queue a video for generation on Venice.ai (text-to-video, image-to-video). Returns queue_id for retrieval."
version: "1.0.0"
author: "Agent Zero"
tags: ["venice", "video", "ai", "generation", "queue"]
trigger_patterns:
  - "queue video"
  - "start video generation"
  - "venice video queue"
---

# Venice Video Queue

Queue videos for generation on Venice.ai. Supports text-to-video and image-to-video.

## Requirements
- `VENICE_API_KEY` environment variable

## CLI Usage

```bash
python /a0/usr/skills/venice-video-queue/scripts/queue_video.py PROMPT [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `PROMPT` | Yes | Text prompt describing the video |

### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--model` | `-m` | `wan-2.5-preview-text-to-video` | Model to use |
| `--duration` | `-d` | `5s` | Video duration: `5s` or `10s` |
| `--resolution` | `-r` | `720p` | Resolution: `480p`, `720p`, `1080p` |
| `--aspect-ratio` | `-a` | None | Aspect ratio e.g. `16:9`, `9:16`, `1:1` |
| `--negative-prompt` | `-n` | None | Things to avoid in the video |
| `--image` | `-i` | None | Input image path for image-to-video |
| `--video` | `-v` | None | Input video path for video-to-video |
| `--audio` | | None | Audio file path to include |
| `--with-audio` | | False | Enable audio generation |
| `--json` | | False | Output result as JSON |

## Examples

### Text-to-Video
```bash
python /a0/usr/skills/venice-video-queue/scripts/queue_video.py "A cat playing piano in a jazz club" \
  --duration 5s \
  --resolution 720p \
  --aspect-ratio 16:9
```

### Image-to-Video
```bash
python /a0/usr/skills/venice-video-queue/scripts/queue_video.py "Animate this scene with gentle motion" \
  --image /path/to/image.png \
  --model wan-2.5-preview-image-to-video \
  --duration 5s
```

### JSON Output
```bash
python /a0/usr/skills/venice-video-queue/scripts/queue_video.py "Cinematic sunset" --json
# Output: {"model": "wan-2.5-preview-text-to-video", "queue_id": "abc123..."}
```

## Output

On success, displays:
```
✅ Video queued successfully!
   Model:    wan-2.5-preview-text-to-video
   Queue ID: abc123-def456-...

To retrieve, run:
   python retrieve_video.py wan-2.5-preview-text-to-video abc123-def456-...
```

## Retrieval

After queuing, use the `venice-video-retrieve` skill:
```bash
python /a0/usr/skills/venice-video-retrieve/scripts/retrieve_video.py MODEL QUEUE_ID
```

## Common Models

| Model | Type | Notes |
|-------|------|-------|
| `wan-2.5-preview-text-to-video` | Text-to-video | Default, good quality |
| `wan-2.5-preview-image-to-video` | Image-to-video | Animate still images |
| `veo3.1-full-image-to-video` | Image-to-video | No aspect_ratio support |

## Programmatic Usage

```python
from queue_video import queue_video, queue_text_to_video, queue_image_to_video

# Text-to-video
result = queue_text_to_video(
    prompt="A cat playing piano",
    duration="5s",
    resolution="720p"
)
print(f"Queue ID: {result.queue_id}")

# Image-to-video
result = queue_image_to_video(
    prompt="Animate this scene",
    image_path="/path/to/image.png"
)
```

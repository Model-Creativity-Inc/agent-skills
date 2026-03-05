---
name: "venice-video-retrieve"
description: "Retrieve a queued video from Venice.ai by queue_id. Polls until complete then downloads."
version: "1.0.0"
author: "Agent Zero"
tags: ["venice", "video", "ai", "generation", "download"]
trigger_patterns:
  - "retrieve video"
  - "download video"
  - "get video"
  - "venice video retrieve"
---

# Venice Video Retrieve

Retrieve and download queued videos from Venice.ai. Automatically polls until generation is complete.

## Requirements
- `VENICE_API_KEY` environment variable
- A `queue_id` from `venice-video-queue`

## CLI Usage

```bash
python /a0/usr/skills/venice-video-retrieve/scripts/retrieve_video.py MODEL QUEUE_ID [options]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `MODEL` | Yes | Model that was used for generation |
| `QUEUE_ID` | Yes | Queue ID returned from queue_video |

### Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | Auto-generated | Output path for the video file |
| `--interval` | `-i` | `5` | Polling interval in seconds |
| `--max-wait` | `-w` | `600` | Maximum wait time in seconds |
| `--delete-after` | | False | Delete from Venice servers after download |
| `--quiet` | `-q` | False | Suppress progress output |
| `--json` | | False | Output result as JSON |

## Examples

### Basic Retrieval
```bash
python /a0/usr/skills/venice-video-retrieve/scripts/retrieve_video.py \
  wan-2.5-preview-text-to-video \
  abc123-def456-queue-id
```

### Save to Specific Path
```bash
python /a0/usr/skills/venice-video-retrieve/scripts/retrieve_video.py \
  wan-2.5-preview-text-to-video \
  abc123-def456-queue-id \
  --output /path/to/my_video.mp4
```

### Custom Polling Settings
```bash
python /a0/usr/skills/venice-video-retrieve/scripts/retrieve_video.py \
  wan-2.5-preview-text-to-video \
  abc123-def456-queue-id \
  --interval 10 \
  --max-wait 900
```

### Quiet Mode with JSON Output
```bash
python /a0/usr/skills/venice-video-retrieve/scripts/retrieve_video.py \
  wan-2.5-preview-text-to-video \
  abc123-def456-queue-id \
  --quiet --json
# Output: {"status": "completed", "path": "/root/venice_videos/video_1234567890.mp4"}
```

## Output

Progress output during polling:
```
🎬 Retrieving video...
   Model:    wan-2.5-preview-text-to-video
   Queue ID: abc123-def456-...

  [5s] Status: pending | Progress: 10% ETA 45s
  [10s] Status: pending | Progress: 25% ETA 35s
  [15s] Status: pending | Progress: 50% ETA 20s
  [20s] Status: pending | Progress: 75% ETA 10s
  [25s] Status: completed | Progress: 100%
  ✅ Video ready!
  💾 Saved to: /root/venice_videos/video_1234567890.mp4

✅ Video saved to: /root/venice_videos/video_1234567890.mp4
```

## Default Output Location

If no `--output` is specified, videos are saved to:
```
/root/venice_videos/video_<timestamp>.mp4
```

## Error Handling

| Exit Code | Meaning |
|-----------|----------|
| `0` | Success |
| `1` | General error (API, network, etc.) |
| `2` | Timeout - generation took too long |

## Programmatic Usage

```python
from retrieve_video import retrieve_and_save, poll_until_complete

# Full workflow: poll and save
path = retrieve_and_save(
    model="wan-2.5-preview-text-to-video",
    queue_id="abc123-def456",
    output_path="/path/to/video.mp4",
    poll_interval=5,
    max_wait=600
)
print(f"Saved to: {path}")

# Just poll (without saving)
result = poll_until_complete(
    model="wan-2.5-preview-text-to-video",
    queue_id="abc123-def456"
)
print(f"Status: {result.status}")
# Access result.video_data or result.video_url
```

## Complete Workflow Example

```bash
# Step 1: Queue a video
python /a0/usr/skills/venice-video-queue/scripts/queue_video.py "A cat playing piano" --json
# Output: {"model": "wan-2.5-preview-text-to-video", "queue_id": "abc123..."}

# Step 2: Retrieve the video
python /a0/usr/skills/venice-video-retrieve/scripts/retrieve_video.py \
  wan-2.5-preview-text-to-video \
  abc123... \
  --output /root/cat_piano.mp4
```

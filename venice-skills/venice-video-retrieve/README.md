# Venice Video Retrieve

Retrieve and download queued videos from [Venice.ai](https://venice.ai/). Polls automatically until generation is complete, then saves the video to disk.

> For a simpler all-in-one workflow, use [venice-video-generate](../venice-video-generate/) instead.

## Features

- **Automatic polling** until video generation completes
- Handles both JSON status responses and binary video data
- Supports video URL download, base64 data URIs, and raw binary responses
- Configurable poll interval and timeout
- JSON output mode for scripting
- Optional server-side deletion after download

## Prerequisites

```bash
pip install requests pydantic
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### Basic retrieval

```bash
python scripts/retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id
```

### Save to specific path

```bash
python scripts/retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id \
  --output /path/to/my_video.mp4
```

### Custom polling settings

```bash
python scripts/retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id \
  --interval 10 --max-wait 900
```

### Quiet mode with JSON

```bash
python scripts/retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id --quiet --json
# Output: {"status": "completed", "path": "/root/venice_videos/video_1234567890.mp4"}
```

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `model` | -- | *(required)* | Model used for generation |
| `queue_id` | -- | *(required)* | Queue ID from `venice-video-queue` |
| `--output` | `-o` | auto | Output file path |
| `--interval` | `-i` | `5` | Poll interval in seconds |
| `--max-wait` | `-w` | `600` | Maximum wait time in seconds |
| `--delete-after` | -- | off | Delete from Venice servers after download |
| `--quiet` | `-q` | off | Suppress progress output |
| `--json` | -- | off | JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | General error (API, network, etc.) |
| `2` | Timeout -- generation took too long |

## Python Import

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
# Access result.video_data or result.video_url
```

## Complete Two-Step Workflow

```bash
# Step 1: Queue
python ../venice-video-queue/scripts/queue_video.py "A cat playing piano" --json
# Output: {"model": "wan-2.5-preview-text-to-video", "queue_id": "abc123..."}

# Step 2: Retrieve
python scripts/retrieve_video.py wan-2.5-preview-text-to-video abc123...
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

# Venice Video Queue

Queue videos for generation on [Venice.ai](https://venice.ai/). Supports text-to-video, image-to-video, and video-to-video. Returns a `queue_id` for later retrieval with `venice-video-retrieve`.

> For a simpler all-in-one workflow, use [venice-video-generate](../venice-video-generate/) instead.

## Features

- **Text-to-video**, **image-to-video**, and **video-to-video** support
- Automatic file-to-base64 encoding for local image/video/audio inputs
- CLI with full argparse support
- JSON output mode for scripting
- Convenience functions for common workflows

## Prerequisites

```bash
pip install requests pydantic
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### Text-to-video

```bash
python scripts/queue_video.py "A cat playing piano in a jazz club" \
  --duration 5s --resolution 720p --aspect-ratio 16:9
```

### Image-to-video

```bash
python scripts/queue_video.py "Animate this scene with gentle motion" \
  --image /path/to/image.png \
  --model wan-2.5-preview-image-to-video
```

### JSON output (for scripting)

```bash
python scripts/queue_video.py "Cinematic sunset" --json
# Output: {"model": "wan-2.5-preview-text-to-video", "queue_id": "abc123..."}
```

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `prompt` | -- | *(required)* | Text description |
| `--model` | `-m` | `wan-2.5-preview-text-to-video` | Model ID |
| `--duration` | `-d` | `5s` | Duration (`5s`, `10s`) |
| `--resolution` | `-r` | `720p` | Resolution |
| `--aspect-ratio` | `-a` | None | Aspect ratio (omit if model doesn't support) |
| `--negative-prompt` | `-n` | None | What to avoid |
| `--image` | `-i` | None | Input image path |
| `--video` | `-v` | None | Input video path |
| `--audio` | -- | None | Audio file path |
| `--with-audio` | -- | off | Enable audio generation |
| `--json` | -- | off | JSON output |

## After Queuing

Use the returned `queue_id` with `venice-video-retrieve`:

```bash
python ../venice-video-retrieve/scripts/retrieve_video.py MODEL QUEUE_ID
```

## Python Import

```python
from queue_video import queue_video, queue_text_to_video, queue_image_to_video

# Text-to-video
result = queue_text_to_video(prompt="A cat playing piano", duration="5s")
print(f"Queue ID: {result.queue_id}")

# Image-to-video
result = queue_image_to_video(prompt="Animate this", image_path="/path/to/img.png")
print(f"Queue ID: {result.queue_id}")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

# Venice Video Generate

Full-lifecycle video generation using [Venice.ai](https://venice.ai/). Combines queue, poll, retrieve, and save into a single operation with progress logging. This is the **recommended approach** for video generation.

## Features

- **Single-call generation** -- queue + poll + retrieve + save in one operation
- **Progress logging** every 20 seconds with progress bars and ETAs
- **Text-to-video** and **image-to-video** support
- **Auto-save** to disk with configurable output paths
- **Timeout protection** -- configurable max wait (default: 15 minutes)
- Handles both JSON status responses and binary video data

## Prerequisites

```bash
pip install requests
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### Basic text-to-video

```bash
python scripts/generate_video.py "A cat playing piano"
```

### With options

```bash
python scripts/generate_video.py "Ocean waves at sunset" \
  --model kling-2.6-pro-text-to-video \
  --duration 10s \
  --resolution 1080p \
  --aspect-ratio 16:9
```

### Image-to-video

```bash
python scripts/generate_video.py "Make this image come alive" \
  --image /path/to/image.png \
  --model wan-2.5-preview-image-to-video
```

### Custom output

```bash
python scripts/generate_video.py "Dancing robot" --output ./my_video.mp4
```

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `prompt` | -- | *(required)* | Text description of the video |
| `--model` | `-m` | `wan-2.5-preview-text-to-video` | Model ID |
| `--duration` | `-d` | `5s` | Duration (e.g., `5s`, `10s`) |
| `--resolution` | `-r` | `720p` | Resolution (e.g., `720p`, `1080p`) |
| `--aspect-ratio` | `-a` | `16:9` | Aspect ratio (e.g., `16:9`, `9:16`, `1:1`) |
| `--audio` | -- | off | Enable audio generation |
| `--no-audio` | -- | -- | Explicitly disable audio |
| `--negative-prompt` | `-n` | None | What to avoid |
| `--image` | `-i` | None | Input image for image-to-video |
| `--output` | `-o` | auto | Output file path |
| `--output-dir` | -- | `/root/venice_videos` | Output directory |
| `--max-wait` | -- | `900` | Max wait seconds (15 min) |
| `--quiet` | `-q` | off | Suppress progress output |

## Common Models

### Text-to-Video

| Model | Quality | Speed |
|-------|---------|-------|
| `wan-2.5-preview-text-to-video` | Good | Fast (30-60s for 5s video) |
| `kling-2.6-pro-text-to-video` | Higher | Slower (60-120s) |
| `veo3.1-full-text-to-video` | Excellent | Slowest (90-180s) |

### Image-to-Video

| Model | Notes |
|-------|-------|
| `wan-2.5-preview-image-to-video` | Fast, reliable |
| `veo3.1-full-image-to-video` | Premium quality |

## Python Import

```python
from generate_video import generate_video

result = generate_video(
    prompt="A beautiful sunset over mountains",
    model="wan-2.5-preview-text-to-video",
    duration="5s",
    verbose=True
)

if result.success:
    print(f"Video saved: {result.video_path}")
    print(f"Took: {result.elapsed_seconds:.1f}s")
else:
    print(f"Failed: {result.error}")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

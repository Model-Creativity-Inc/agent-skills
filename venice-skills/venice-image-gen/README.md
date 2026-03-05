# Venice Image Generation

Generate images from text prompts using the [Venice.ai](https://venice.ai/) image generation API. Supports multiple resolutions, aspect ratios, formats, and up to 4 variants per request.

## Features

- **Text-to-image** generation with customizable prompts
- **Multiple resolutions** -- 1K, 2K, 4K
- **Aspect ratios** -- 1:1, 16:9, 9:16, 4:3, 3:4
- **Negative prompts** -- specify what to avoid
- **Multiple variants** -- generate 1-4 images per request
- **Output formats** -- webp, png, jpeg
- **Reproducible results** with seed parameter

## Prerequisites

```bash
pip install requests
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### Basic

```bash
python scripts/generate_image.py "A beautiful sunset over mountains"
```

### With options

```bash
python scripts/generate_image.py "A futuristic cityscape at night" \
  --resolution 2K \
  --aspect_ratio 16:9 \
  --negative_prompt "blurry, low quality" \
  --variants 2 \
  --format png \
  --output cityscape.png
```

## Options

| Option | Default | Values | Description |
|--------|---------|--------|-------------|
| `prompt` | *(required)* | text | Image description |
| `--model` | `nano-banana-2` | model ID | Generation model |
| `--resolution` | `1K` | `1K`, `2K`, `4K` | Image resolution |
| `--aspect_ratio` | `1:1` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4` | Aspect ratio |
| `--negative_prompt` | None | text | What to avoid |
| `--variants` | `1` | `1`-`4` | Number of images |
| `--format` | `webp` | `webp`, `png`, `jpeg` | Output format |
| `--seed` | None | integer | Random seed for reproducibility |
| `--no-safe-mode` | off | flag | Disable safe mode |
| `--output` / `-o` | auto | path | Output file path |

## Python Import

```python
from generate_image import generate_image

result = generate_image(
    prompt="A cat wearing a top hat",
    resolution="2K",
    aspect_ratio="1:1",
    variants=2
)

for path in result["images"]:
    print(f"Saved: {path}")
```

## Response Format

```python
{
    "success": True,
    "model": "nano-banana-2",
    "prompt": "A cat wearing a top hat",
    "images": ["/path/to/generated_20260305_143200.webp"],
    "count": 1
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

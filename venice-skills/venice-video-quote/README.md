# Venice Video Quote

Get cost estimates for [Venice.ai](https://venice.ai/) video generation before creating. Validates parameters against model capabilities to prevent invalid requests.

## Features

- **Cost estimation** before committing to video generation
- **Parameter validation** -- checks duration, aspect ratio, resolution, and audio against model capabilities
- **Model inspection** -- view valid options for any video model
- Structured Pydantic models for programmatic use

## Prerequisites

```bash
pip install requests pydantic
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

```bash
python scripts/get_video_quote.py
```

The default script demonstrates valid and invalid quote requests with model validation.

## Python Import

```python
from get_video_quote import get_video_quote, show_model_options

# Get a cost quote
quote = get_video_quote(
    model="wan-2.5-preview-text-to-video",
    duration="10s",
    aspect_ratio="16:9",
    resolution="720p",
    audio=True
)
print(f"Estimated cost: ${quote.quote:.2f}")

# View valid options for a model
show_model_options("wan-2.5-preview-text-to-video")

# Skip validation (use at your own risk)
quote = get_video_quote(
    model="wan-2.5-preview-text-to-video",
    duration="5s",
    validate=False
)
```

## Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `model` | Yes | -- | Video model ID |
| `duration` | Yes | -- | Duration (e.g., `5s`, `10s`) |
| `aspect_ratio` | No | `16:9` | Aspect ratio |
| `resolution` | No | `720p` | Resolution |
| `audio` | No | `False` | Include audio |
| `validate` | No | `True` | Validate params against model capabilities |

## Validation

When `validate=True` (default), the function fetches the model's capabilities from the API and checks:

- Duration is in the model's supported list
- Aspect ratio is supported
- Resolution is supported
- Audio is supported (if requested)

Invalid parameters raise a `ValueError` with details about valid options.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

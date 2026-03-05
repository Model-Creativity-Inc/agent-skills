# Venice List Video Models

List all available video generation models from the [Venice.ai](https://venice.ai/) API with complete specifications including durations, resolutions, aspect ratios, audio capabilities, and input requirements.

## Features

- Lists all video models grouped by type (text-to-video, image-to-video, video)
- Shows supported durations, resolutions, aspect ratios
- Displays audio capabilities (generation, configurable, input)
- Detailed per-model specification view
- Example API request generation
- JSON output for programmatic use

## Prerequisites

```bash
pip install requests
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### Summary table (default)

```bash
python scripts/list_video_models.py
```

### Detailed specs for a specific model

```bash
python scripts/list_video_models.py --model kling-2.6-pro-text-to-video
```

### All models detailed

```bash
python scripts/list_video_models.py --detailed
```

### JSON output

```bash
python scripts/list_video_models.py --json
```

## Output Modes

| Flag | Description |
|------|-------------|
| *(default)* | Summary table grouped by model type |
| `--model <id>` | Detailed specs + example API request for one model |
| `--detailed` | Detailed specs for all models |
| `--json` | Full specs as JSON array |

## Important Notes

When generating videos, each model has strict parameter requirements:

- **`duration`** -- Use ONLY the values listed for that model
- **`aspect_ratio`** -- Only include if the model lists supported ratios (causes 400 errors otherwise)
- **`audio`** -- Check `audio_configurable` before including
- **`image_url`** -- REQUIRED for image-to-video models

## Python Import

```python
from list_video_models import fetch_video_models, format_summary_table

models = fetch_video_models()

for m in models:
    print(f"{m.id}: type={m.model_type}, durations={m.durations}")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

---
name: "venice-list-video-models"
description: "List available video generation models from Venice.ai API with complete specifications for successful generation."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - video
  - models
  - generation
trigger_patterns:
  - "list video models"
  - "venice video models"
  - "video generation models"
  - "available video models"
---

# Venice List Video Models

List available video generation models with complete specifications.

## When to Use

Use this skill when you need to:
- List available video generation models
- Check model specifications (durations, resolutions, aspect ratios)
- Find the right model for your video generation task
- Get example API requests

## Usage

### Default - Summary Table
```bash
python /a0/usr/skills/venice-list-video-models/scripts/list_video_models.py
```

### Detailed Model Specs
```bash
python /a0/usr/skills/venice-list-video-models/scripts/list_video_models.py --model kling-2.6-pro-text-to-video
```

### All Models Detailed
```bash
python /a0/usr/skills/venice-list-video-models/scripts/list_video_models.py --detailed
```

### JSON Output
```bash
python /a0/usr/skills/venice-list-video-models/scripts/list_video_models.py --json
```

## Critical Parameters

| Parameter | Guidance |
|-----------|----------|
| `duration` | Use ONLY values listed for the model |
| `resolution` | Use listed values or omit for default |
| `aspect_ratio` | **ONLY include if model lists ratios** - causes 400 errors otherwise! |
| `audio` | Check `audio_configurable` |
| `image_url` | **REQUIRED** for image-to-video models |

## Requirements

- `VENICE_API_KEY` environment variable

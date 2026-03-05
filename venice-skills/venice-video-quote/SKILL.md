---
name: "venice-video-quote"
description: "Get cost estimate for Venice.ai video generation before creating. Validates parameters against model capabilities."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - video
  - cost
  - quote
trigger_patterns:
  - "video quote"
  - "video cost"
  - "estimate video"
  - "video price"
  - "how much video"
---

# Venice Video Quote

Get cost estimate for video generation before creating.

## When to Use

Use this skill when you need to:
- Get cost estimates before generating videos
- Validate parameters against model capabilities
- Compare costs between different configurations

## Usage

```bash
python /a0/usr/skills/venice-video-quote/scripts/get_video_quote.py <model> <duration> [aspect_ratio] [resolution] [audio]
```

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| model | ✅ | - | Model ID |
| duration | ✅ | - | Video duration (5s, 10s, etc.) |
| aspect_ratio | ❌ | 16:9 | Aspect ratio |
| resolution | ❌ | 720p | Resolution |
| audio | ❌ | False | Enable audio |

## Example

```bash
# Get quote for 5-second video
python /a0/usr/skills/venice-video-quote/scripts/get_video_quote.py wan-2.5-preview-text-to-video 5s 16:9 720p false
```

## Requirements

- `VENICE_API_KEY` environment variable

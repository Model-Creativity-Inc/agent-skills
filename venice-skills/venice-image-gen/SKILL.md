---
name: "venice-image-gen"
description: "Generate images using Venice.ai API with customizable resolution, aspect ratio, and variants."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - image
  - generation
  - ai-art
trigger_patterns:
  - "generate image"
  - "venice image"
  - "create image"
  - "ai image"
  - "make image"
---

# Venice Image Generation

Generate images using Venice.ai API.

## When to Use

Use this skill when you need to:
- Generate AI images from text prompts
- Create images with specific resolutions or aspect ratios
- Generate multiple image variants

## Usage

### Basic
```bash
python /a0/usr/skills/venice-image-gen/scripts/generate_image.py "A beautiful sunset over mountains"
```

### With Options
```bash
python /a0/usr/skills/venice-image-gen/scripts/generate_image.py "prompt" --resolution 2K --aspect_ratio 16:9 --variants 2
```

## Options

| Option | Values | Default | Notes |
|--------|--------|---------|-------|
| --resolution | 1K, 2K, 4K | 1K | Higher = more credits |
| --aspect_ratio | 1:1, 16:9, 9:16, 4:3, 3:4 | 1:1 | |
| --variants | 1-4 | 1 | Generate multiple images |
| --negative_prompt | text | None | What to avoid |
| --format | webp, png, jpeg | webp | webp is smallest |
| --output | path | ./generated_image | Output filename |

## Defaults

- **Model:** nano-banana-2 (Google Nano Banana)
- **Resolution:** 1K
- **Aspect Ratio:** 1:1
- **Format:** webp

## Requirements

- `VENICE_API_KEY` environment variable

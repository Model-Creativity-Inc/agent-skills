---
name: "venice-list-image-models"
description: "List available image generation models from Venice.ai API with pricing and constraints."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - image
  - models
  - generation
trigger_patterns:
  - "list image models"
  - "venice image models"
  - "image generation models"
  - "available image models"
---

# Venice List Image Models

List available image generation models from Venice.ai API.

## When to Use

Use this skill when you need to:
- List available image generation models from Venice.ai
- Check model pricing and constraints
- Find suitable models for image generation tasks

## Usage

```bash
python /a0/usr/skills/venice-list-image-models/scripts/list_image_models.py
```

## Output

Returns for each model:
- Model ID and display name
- Pricing per image
- Resolution constraints
- Supported aspect ratios
- Capabilities

## Requirements

- `VENICE_API_KEY` environment variable (configured in Agent Zero secrets)

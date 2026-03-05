---
name: "venice-list-text-models"
description: "List available text/LLM models from Venice.ai API with capabilities, context windows, and pricing."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - llm
  - models
  - text
trigger_patterns:
  - "list text models"
  - "venice text models"
  - "llm models"
  - "available llm models"
  - "venice models"
---

# Venice List Text Models

List available text/LLM models from Venice.ai API.

## When to Use

Use this skill when you need to:
- List available LLM/text models from Venice.ai
- Check model capabilities and context windows
- Compare model pricing
- Find models with specific traits (most_intelligent, default, etc.)

## Usage

### Basic - List All Models
```bash
python /a0/usr/skills/venice-list-text-models/scripts/list_text_models.py
```

### Filter by Trait
```bash
python /a0/usr/skills/venice-list-text-models/scripts/list_text_models.py most_intelligent
python /a0/usr/skills/venice-list-text-models/scripts/list_text_models.py default
```

## Output

Returns for each model:
- Model ID and display name
- Context window size
- Capabilities (vision, reasoning, etc.)
- Pricing (input/output per million tokens)
- Model traits

## Requirements

- `VENICE_API_KEY` environment variable (configured in Agent Zero secrets)

## Example Output

```
Model ID: claude-opus-45
Display Name: Claude Opus 4.5
Context Window: 200000 tokens
Capabilities: vision, reasoning
Pricing: $15.00/$75.00 per 1M tokens
Traits: most_intelligent
```

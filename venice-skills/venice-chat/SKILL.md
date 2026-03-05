---
name: "venice-chat"
description: "Chat with Venice.ai LLM models, analyze images/videos. Supports reasoning mode and web search."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - chat
  - llm
  - vision
  - reasoning
trigger_patterns:
  - "venice chat"
  - "chat with venice"
  - "analyze image with venice"
  - "venice reasoning"
---

# Venice Chat

Chat with Venice.ai LLM models with optional image analysis and reasoning mode.

## When to Use

Use this skill when you need to:
- Chat with Venice.ai models directly
- Analyze images using vision models
- Use reasoning mode for complex problems
- Enable web search for current information

## Usage

### Simple Chat
```bash
python /a0/usr/skills/venice-chat/scripts/chat.py "What is the capital of France?"
```

### With System Prompt
```bash
python /a0/usr/skills/venice-chat/scripts/chat.py "Write a haiku" --system "You are a poet"
```

### Image Analysis
```bash
python /a0/usr/skills/venice-chat/scripts/chat.py "What's in this image?" --image /path/to/image.png
```

### Reasoning Mode
```bash
python /a0/usr/skills/venice-chat/scripts/chat.py "Solve this math problem" --reasoning
```

## Default Models

| Mode | Model | Notes |
|------|-------|-------|
| Default | zai-org-glm-4.7 | GLM 4.7 - most intelligent |
| Vision | qwen3-vl-235b-a22b | Qwen3 VL 235B - 250K context |
| Reasoning | qwen3-235b-a22b-thinking-2507 | Extended thinking |

## Options

| Option | Description |
|--------|-------------|
| --model | Override model ID |
| --system | System prompt |
| --image | Path to image for analysis |
| --reasoning | Enable reasoning mode |
| --temperature | 0.0-2.0 (default: 0.7) |
| --max_tokens | Max response tokens |
| --web_search | Enable web search |

## Requirements

- `VENICE_API_KEY` environment variable

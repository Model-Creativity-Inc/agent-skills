# Venice Chat

Chat with [Venice.ai](https://venice.ai/) LLM models. Supports system prompts, image analysis (vision), reasoning mode, and web search. Auto-selects the best model based on the task.

## Features

- **Text chat** with any Venice.ai LLM model
- **Vision/image analysis** -- describe, analyze, or ask questions about images
- **Reasoning mode** -- extended thinking for complex problems
- **Web search** -- augment responses with live web results
- **Auto model selection** -- picks the optimal model based on task type

## Prerequisites

```bash
pip install requests
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### Simple chat

```bash
python scripts/chat.py "What is the capital of France?"
```

### With system prompt

```bash
python scripts/chat.py "Write a haiku" --system "You are a poet"
```

### Image analysis

```bash
python scripts/chat.py "What's in this image?" --image /path/to/image.png
```

### Reasoning mode

```bash
python scripts/chat.py "Solve this complex math problem" --reasoning
```

### Web search

```bash
python scripts/chat.py "What happened in tech news today?" --web_search
```

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `message` | -- | *(required)* | Your message |
| `--system` | `-s` | None | System prompt |
| `--model` | `-m` | auto | Model ID (auto-selected if not provided) |
| `--image` | `-i` | None | Image path for vision analysis |
| `--reasoning` | `-r` | off | Enable reasoning mode |
| `--temperature` | `-t` | 0.7 | Temperature (0.0-2.0) |
| `--max_tokens` | -- | None | Max response tokens |
| `--web_search` | `-w` | off | Enable web search |

## Default Models

| Task | Model | Notes |
|------|-------|-------|
| General chat | `zai-org-glm-4.7` | GLM 4.7 -- most intelligent |
| Vision/image | `qwen3-vl-235b-a22b` | Qwen3 VL 235B -- 250K context |
| Reasoning | `qwen3-235b-a22b-thinking-2507` | Extended thinking |

## Python Import

```python
from chat import chat

result = chat(
    message="Explain quantum computing",
    system="You are a physics professor",
    temperature=0.5
)
print(result["response"])
```

## Response Format

```python
{
    "success": True,
    "model": "zai-org-glm-4.7",
    "response": "The capital of France is Paris.",
    "usage": {
        "prompt_tokens": 12,
        "completion_tokens": 8,
        "total_tokens": 20
    }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

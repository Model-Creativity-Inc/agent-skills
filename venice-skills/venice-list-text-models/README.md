# Venice List Text Models

List all available text/LLM models from the [Venice.ai](https://venice.ai/) API with context windows, pricing, capabilities, and traits.

## Features

- Lists all available LLM/text models
- Shows context window sizes, input/output pricing per million tokens
- Displays capabilities (vision, reasoning, function calling, code optimization, web search)
- Filter by trait (e.g., `most_intelligent`, `default`, `most_uncensored`)
- Capabilities summary across all models
- Structured Pydantic models for programmatic use

## Prerequisites

```bash
pip install requests pydantic
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### List all models

```bash
python scripts/list_text_models.py
```

### Filter by trait

```bash
python scripts/list_text_models.py most_intelligent
python scripts/list_text_models.py default
```

## Output

Displays a formatted table sorted by context window size:

```
Model ID                            Name                           Context    In $/M   Out $/M  Traits
------------------------------------------------------------------------------------------------------------------------
qwen3-235b-a22b-thinking-2507       Qwen3 235B Thinking            250K       0.50     2.00     most_intelligent
...
```

Plus capabilities summary:

```
=== Capabilities Summary ===
  total: 15
  with_reasoning: 4
  with_vision: 6
  with_function_calling: 8
  with_web_search: 10
  optimized_for_code: 3
```

## Python Import

```python
from list_text_models import list_text_models, get_capabilities_summary

# All models
models = list_text_models()

# Filtered by trait
intelligent = list_text_models(filter_trait="most_intelligent")

# Capabilities summary
summary = get_capabilities_summary(models)
print(f"Models with vision: {summary['with_vision']}")

# Access individual models
for m in models.data:
    cap = m.model_spec.capabilities
    print(f"{m.id}: vision={cap.supportsVision}, reasoning={cap.supportsReasoning}")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

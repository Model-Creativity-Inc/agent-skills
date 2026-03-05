# Venice List Image Models

List all available image generation models from the [Venice.ai](https://venice.ai/) API with pricing, constraints, and capabilities.

## Features

- Lists all available image generation models
- Shows per-generation and upscale pricing (USD)
- Displays constraints (steps, prompt character limits, resolutions)
- Summary statistics (price range, averages)
- Structured Pydantic models for programmatic use

## Prerequisites

```bash
pip install requests pydantic
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

```bash
python scripts/list_image_models.py
```

## Output

Displays a formatted table:

```
Model ID                  Name                      Gen $      2x Up $  4x Up $  Steps        Prompt Limit
-------------------------------------------------------------------------------------------------------------------
nano-banana-2             Nano Banana 2             0.01       0.02     0.04     30/50        1500
...
```

Plus summary statistics:

```
=== Summary ===
  Total models: 8
  Price range: $0.01 - $0.05
  Average price: $0.025
```

## Python Import

```python
from list_image_models import list_image_models, format_models_table, get_models_summary

models = list_image_models()

# Formatted table
print(format_models_table(models))

# Summary stats
summary = get_models_summary(models)
print(f"Total: {summary['total_models']}, cheapest: ${summary['min_price']:.2f}")

# Access individual models
for m in models.data:
    print(f"{m.id}: {m.model_spec.name}")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

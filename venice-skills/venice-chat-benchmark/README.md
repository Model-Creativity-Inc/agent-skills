# Venice Chat Benchmark

Benchmark [Venice.ai](https://venice.ai/) chat completion models with complex `tool_choice` payloads. Runs N iterations, captures detailed timing and reliability metrics, and optionally generates a 4K infographic summary.

## Features

- **Stress testing** -- run configurable iterations against any Venice chat model
- **Tool choice analysis** -- measures tool call rate, distribution across 7 defined tools, and JSON argument validity
- **Timing statistics** -- average, median, min, max, standard deviation, P90, P95, and P99
- **Error categorization** -- groups failures by type (HTTP, timeout, connection, JSON decode)
- **Token tracking** -- per-run and aggregate prompt, completion, and total token usage
- **Finish reason tracking** -- counts of `tool_calls`, `stop`, and other finish reasons
- **4K infographic** -- optional visual summary generated via the `venice-image-gen` skill
- **Intermediate saves** -- results are written to disk after every run so data is preserved if interrupted

## Prerequisites

```bash
pip install requests
export VENICE_API_KEY="your_venice_api_key"
```

For infographic generation, the `venice-image-gen` skill must be available.

## Usage

### Basic benchmark (50 runs, default model)

```bash
python scripts/benchmark.py --model minimax-m27 --runs 50 --output ./chat_benchmark
```

### Custom run count and timeout

```bash
python scripts/benchmark.py --model minimax-m27 --runs 100 --timeout 60 --output ./chat_benchmark
```

### With infographic generation

```bash
python scripts/benchmark.py --model minimax-m27 --runs 50 --output ./chat_benchmark --infographic
```

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--model` | -- | `minimax-m27` | Model ID to benchmark |
| `--runs` | -- | `50` | Number of test iterations |
| `--timeout` | -- | `120` | Request timeout in seconds |
| `--output` | -- | `/a0/usr/workdir/chat_benchmark` | Output directory for results |
| `--infographic` | -- | off | Generate a 4K infographic summary when done |

## Test Payload

The benchmark sends a fixed travel planning scenario to every run:

- **System prompt** enforces tool-only responses (no plain text)
- **7 function tools** defined: `set_travel_dates`, `set_secondary_destinations`, `set_traveler_info`, `set_travel_priorities`, `set_budget`, `present_choices`, `suggest_primary_destinations`
- **User message** contains multiple extractable data points (dates, destinations, interests, budget)
- **`tool_choice: auto`** lets the model decide which tool(s) to call

## Python Import

```python
from benchmark import run_benchmark

results = run_benchmark(
    api_key="your_key",
    model="minimax-m27",
    num_runs=10,
    output_dir="./benchmark_output",
    timeout=120
)
print(results["stats"]["success_rate"])
```

## Response Format

The benchmark writes `benchmark_results.json` to the output directory:

```json
{
  "metadata": {
    "model": "minimax-m27",
    "num_runs": 50,
    "timeout": 120,
    "num_tools": 7,
    "tool_names": ["set_travel_dates", "..."],
    "tool_choice": "auto",
    "start_time": "2026-03-20T12:00:00",
    "end_time": "2026-03-20T12:15:00"
  },
  "runs": [
    {
      "run": 1,
      "success": true,
      "duration_seconds": 2.451,
      "finish_reason": "tool_calls",
      "has_tool_calls": true,
      "tool_calls": [{"name": "set_travel_dates", "args_valid_json": true}],
      "usage": {"prompt_tokens": 850, "completion_tokens": 120, "total_tokens": 970}
    }
  ],
  "stats": {
    "total_runs": 50,
    "success_rate": 98.0,
    "tool_call_rate": 95.0,
    "json_validity_rate": 100.0,
    "timing": {"avg": 2.5, "median": 2.3, "min": 1.1, "max": 5.2, "stdev": 0.8},
    "tool_call_distribution": {"set_travel_dates": 40, "set_budget": 8},
    "token_usage": {"avg_total_tokens": 970, "total_all_tokens": 48500}
  }
}
```

With the `--infographic` flag, a `benchmark_infographic.png` file is also generated.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

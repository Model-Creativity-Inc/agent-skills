---
name: "venice-chat-benchmark"
description: "Benchmark Venice.ai chat models with complex tool_choice payloads. Runs N iterations, captures timing, tool call distribution, JSON validity, errors, token usage, and generates a 4K infographic."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - benchmark
  - chat
  - tool_choice
  - testing
trigger_patterns:
  - "benchmark chat"
  - "test model"
  - "venice benchmark"
  - "tool choice test"
---

# Venice Chat Model Benchmark

Benchmark Venice.ai chat completion models with complex tool_choice payloads.

## When to Use

Use this skill when you need to:
- Stress test a Venice chat model with tool calling
- Measure response time, reliability, and tool call accuracy
- Compare model behavior across many runs
- Generate visual benchmark reports

## Usage

### Basic (50 runs, minimax-m27)
```bash
export VENICE_API_KEY="your-key"
python /a0/usr/skills/venice-chat-benchmark/scripts/benchmark.py --model minimax-m27 --runs 50 --output /a0/usr/workdir/chat_benchmark
```

### With Infographic
```bash
python /a0/usr/skills/venice-chat-benchmark/scripts/benchmark.py --model minimax-m27 --runs 50 --output /a0/usr/workdir/chat_benchmark --infographic
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| --model | minimax-m27 | Model ID to benchmark |
| --runs | 50 | Number of test iterations |
| --timeout | 120 | Request timeout in seconds |
| --output | /a0/usr/workdir/chat_benchmark | Output directory |
| --infographic | off | Generate 4K infographic when done |

## What It Measures

- **Response time** (avg, median, min, max, stdev, P90, P95)
- **Success rate** (HTTP errors, timeouts, connection errors)
- **Tool call rate** (% of responses that include tool calls)
- **Tool call distribution** (which tools get selected)
- **JSON validity** (whether tool call arguments parse correctly)
- **Token usage** (prompt, completion, total)
- **Finish reasons** (tool_calls vs stop vs other)
- **Error categorization** (by type, with details)

## Test Payload

The benchmark uses a complex travel planning scenario with:
- Detailed system prompt enforcing tool-only responses
- 7 function tools defined (dates, destinations, traveler info, priorities, budget, choices, suggestions)
- A rich user message with multiple extractable data points
- `tool_choice: auto`

## Output

- `benchmark_results.json` — Full results with all run data and computed stats
- `benchmark_infographic.png` — 4K visual summary (with --infographic flag)

## Requirements

- `VENICE_API_KEY` environment variable
- `requests` Python package
- `venice-image-gen` skill (for infographic generation, optional)

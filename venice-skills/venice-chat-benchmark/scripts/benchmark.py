#!/usr/bin/env python3
"""Venice Chat Model Benchmark - Tests chat completions with tool_choice.

Usage:
    python benchmark.py --model minimax-m27 --runs 50 --output /path/to/output_dir
    python benchmark.py --model minimax-m27 --runs 50 --output /path/to/output_dir --infographic
"""

import argparse
import json
import os
import subprocess
import sys
import time
import statistics
from datetime import datetime

import requests

API_URL = "https://api.venice.ai/api/v1/chat/completions"

# === COMPLEX TOOL_CHOICE PAYLOAD (Travel Planning) ===

SYSTEM_PROMPT = """You are an expert travel planning assistant. You MUST call exactly ONE tool on every response. Never respond with plain text. Your response IS the tool call.

Available tools:
- set_travel_dates: Record travel dates
- set_secondary_destinations: Record destinations
- set_traveler_info: Record traveler details
- set_travel_priorities: Record priorities
- set_budget: Record budget
- present_choices: Show clickable choices
- suggest_primary_destinations: Show destination cards

Collect dates first, then travelers, then destinations. Pre-fill from conversation context.

Current itinerary context:
No itinerary data yet."""

USER_MESSAGE = "My wife and I want to plan a 2-week trip to Japan this October. We love food, temples, and hiking. Mid-range budget around $6000."

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "set_travel_dates",
            "description": "Set the travel dates for the trip. Opens an interactive date picker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Trip start date YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "Trip end date YYYY-MM-DD"},
                    "flexible": {"type": "boolean", "description": "Whether dates are flexible"}
                },
                "required": ["start_date", "end_date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_secondary_destinations",
            "description": "Set trip destinations with secondary options.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Overview of why these destinations fit"},
                    "primary": {"type": "string", "description": "Primary destination"},
                    "secondary": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "transit": {"type": "string"}
                            },
                            "required": ["name", "transit"]
                        },
                        "description": "4-5 nearby destinations"
                    }
                },
                "required": ["description", "primary", "secondary"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_traveler_info",
            "description": "Capture traveler information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Trip vibe and goals"},
                    "count": {"type": "integer", "description": "Number of travelers"},
                    "interests": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Interest IDs: adventure, hiking, culture, food, street_food, fine_dining, nature, romantic, etc."
                    }
                },
                "required": ["count"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_travel_priorities",
            "description": "Set what matters most for this trip.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ranked": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Priorities in order: comfort, budget, adventure, culture, food, nature, romantic"
                    }
                },
                "required": ["ranked"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_budget",
            "description": "Set the trip budget.",
            "parameters": {
                "type": "object",
                "properties": {
                    "total": {"type": "number", "description": "Total budget"},
                    "currency": {"type": "string", "description": "Currency code"}
                },
                "required": ["total", "currency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "present_choices",
            "description": "Present clickable choices to the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Question to display"},
                    "choices": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["label"]
                        }
                    }
                },
                "required": ["message", "choices"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "suggest_primary_destinations",
            "description": "Present rich destination suggestions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Heading above cards"},
                    "destinations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "tagline": {"type": "string"}
                            },
                            "required": ["name", "tagline"]
                        }
                    }
                },
                "required": ["message", "destinations"]
            }
        }
    }
]


def make_request(api_key, model, timeout=120):
    """Make a single chat completion request with tools."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_MESSAGE}
        ],
        "tools": TOOLS,
        "tool_choice": "auto",
        "temperature": 0.7,
        "stream": False
    }

    resp = requests.post(API_URL, headers=headers, json=payload, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def parse_response(data):
    """Parse the API response and extract key info."""
    choice = data.get("choices", [{}])[0]
    msg = choice.get("message", {})
    finish_reason = choice.get("finish_reason") or "unknown"
    usage = data.get("usage", {})

    result = {
        "finish_reason": finish_reason,
        "has_tool_calls": bool(msg.get("tool_calls")),
        "tool_calls": [],
        "content": msg.get("content"),
        "usage": usage,
    }

    if msg.get("tool_calls"):
        for tc in msg["tool_calls"]:
            tool_info = {
                "id": tc.get("id", ""),
                "name": tc["function"]["name"],
                "arguments_raw": tc["function"]["arguments"],
            }
            try:
                tool_info["arguments_parsed"] = json.loads(tc["function"]["arguments"])
                tool_info["args_valid_json"] = True
            except (json.JSONDecodeError, TypeError) as e:
                tool_info["arguments_parsed"] = None
                tool_info["args_valid_json"] = False
                tool_info["json_error"] = str(e)
            result["tool_calls"].append(tool_info)

    return result


def run_benchmark(api_key, model, num_runs, output_dir, timeout=120):
    """Run the full benchmark."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"{'='*70}")
    print(f"VENICE CHAT BENCHMARK — Tool Choice Stress Test")
    print(f"{'='*70}")
    print(f"Model:        {model}")
    print(f"Runs:         {num_runs}")
    print(f"Timeout:      {timeout}s per request")
    print(f"Tools:        {len(TOOLS)} tools defined")
    print(f"Tool choice:  auto")
    print(f"Started:      {datetime.now().isoformat()}")
    print(f"{'='*70}\n")

    results = {
        "metadata": {
            "model": model,
            "num_runs": num_runs,
            "timeout": timeout,
            "num_tools": len(TOOLS),
            "tool_names": [t["function"]["name"] for t in TOOLS],
            "tool_choice": "auto",
            "system_prompt": SYSTEM_PROMPT,
            "user_message": USER_MESSAGE,
            "start_time": datetime.now().isoformat(),
        },
        "runs": [],
        "stats": {},
    }

    successful_times = []
    tool_call_counts = {}  # which tools get called
    finish_reasons = {}
    errors_list = []

    for run_num in range(1, num_runs + 1):
        run_data = {
            "run": run_num,
            "start_time": datetime.now().isoformat(),
            "success": False,
            "duration_seconds": None,
            "error": None,
            "error_type": None,
            "http_status": None,
            "finish_reason": None,
            "has_tool_calls": False,
            "tool_calls": [],
            "content": None,
            "usage": {},
            "args_valid_json": True,
        }

        try:
            start = time.time()
            raw_response = make_request(api_key, model, timeout=timeout)
            elapsed = time.time() - start

            parsed = parse_response(raw_response)

            run_data["success"] = True
            run_data["duration_seconds"] = round(elapsed, 3)
            run_data["http_status"] = 200
            run_data["finish_reason"] = parsed["finish_reason"] or "none"
            run_data["has_tool_calls"] = parsed["has_tool_calls"]
            run_data["tool_calls"] = parsed["tool_calls"]
            run_data["content"] = parsed["content"]
            run_data["usage"] = parsed["usage"]

            # Check if all tool call args are valid JSON
            all_valid = all(tc.get("args_valid_json", False) for tc in parsed["tool_calls"]) if parsed["tool_calls"] else True
            run_data["args_valid_json"] = all_valid

            successful_times.append(elapsed)

            # Track tool call distribution
            fr = parsed["finish_reason"] or "none"
            finish_reasons[fr] = finish_reasons.get(fr, 0) + 1

            for tc in parsed["tool_calls"]:
                tn = tc["name"]
                tool_call_counts[tn] = tool_call_counts.get(tn, 0) + 1

            # Display
            tool_names = ", ".join(tc["name"] for tc in parsed["tool_calls"]) if parsed["tool_calls"] else "NONE"
            json_ok = "✓" if all_valid else "✗ BAD JSON"
            content_flag = " +content" if parsed["content"] else ""
            print(f"  ✅ Run {run_num:3d}/{num_runs}: {elapsed:6.2f}s | {str(fr):<12} | tools: {tool_names} | json: {json_ok}{content_flag}")

        except requests.exceptions.HTTPError as e:
            elapsed = time.time() - start
            run_data["duration_seconds"] = round(elapsed, 3)
            run_data["error"] = str(e)[:500]
            run_data["error_type"] = "http_error"
            status = None
            try:
                status = e.response.status_code if e.response is not None else None
            except:
                pass
            run_data["http_status"] = status
            try:
                err_body = e.response.json() if e.response is not None else {}
                run_data["error_body"] = err_body
                run_data["error"] = json.dumps(err_body)[:500]
            except:
                run_data["error_body"] = {}
            errors_list.append({"run": run_num, "type": "http_error", "status": status, "error": run_data["error"][:200]})
            print(f"  ❌ Run {run_num:3d}/{num_runs}: {elapsed:6.2f}s | HTTP {status or "???"} - {run_data['error'][:100]}")

        except requests.exceptions.Timeout as e:
            elapsed = time.time() - start
            run_data["duration_seconds"] = round(elapsed, 3)
            run_data["error"] = f"Request timed out after {timeout}s"
            run_data["error_type"] = "timeout"
            errors_list.append({"run": run_num, "type": "timeout", "error": run_data["error"]})
            print(f"  ❌ Run {run_num:3d}/{num_runs}: {elapsed:6.2f}s | TIMEOUT")

        except requests.exceptions.ConnectionError as e:
            elapsed = time.time() - start
            run_data["duration_seconds"] = round(elapsed, 3)
            run_data["error"] = str(e)[:500]
            run_data["error_type"] = "connection_error"
            errors_list.append({"run": run_num, "type": "connection_error", "error": str(e)[:200]})
            print(f"  ❌ Run {run_num:3d}/{num_runs}: {elapsed:6.2f}s | CONNECTION ERROR - {str(e)[:80]}")

        except json.JSONDecodeError as e:
            elapsed = time.time() - start
            run_data["duration_seconds"] = round(elapsed, 3)
            run_data["error"] = f"Invalid JSON response: {str(e)[:200]}"
            run_data["error_type"] = "json_decode_error"
            errors_list.append({"run": run_num, "type": "json_decode_error", "error": str(e)[:200]})
            print(f"  ❌ Run {run_num:3d}/{num_runs}: {elapsed:6.2f}s | JSON DECODE ERROR")

        except Exception as e:
            elapsed = time.time() - start
            run_data["duration_seconds"] = round(elapsed, 3)
            run_data["error"] = str(e)[:500]
            run_data["error_type"] = type(e).__name__
            errors_list.append({"run": run_num, "type": type(e).__name__, "error": str(e)[:200]})
            print(f"  ❌ Run {run_num:3d}/{num_runs}: {elapsed:6.2f}s | {type(e).__name__}: {str(e)[:80]}")

        run_data["end_time"] = datetime.now().isoformat()
        results["runs"].append(run_data)

        # Save intermediate results
        with open(f"{output_dir}/benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2)

    # === COMPUTE STATS ===
    successful_runs = [r for r in results["runs"] if r["success"]]
    failed_runs = [r for r in results["runs"] if not r["success"]]
    tool_call_runs = [r for r in successful_runs if r["has_tool_calls"]]
    no_tool_runs = [r for r in successful_runs if not r["has_tool_calls"]]
    bad_json_runs = [r for r in successful_runs if not r["args_valid_json"]]
    content_runs = [r for r in successful_runs if r["content"]]

    stats = {
        "total_runs": num_runs,
        "successful_runs": len(successful_runs),
        "failed_runs": len(failed_runs),
        "success_rate": round(len(successful_runs) / num_runs * 100, 1),
        "tool_call_runs": len(tool_call_runs),
        "tool_call_rate": round(len(tool_call_runs) / len(successful_runs) * 100, 1) if successful_runs else 0,
        "no_tool_runs": len(no_tool_runs),
        "bad_json_runs": len(bad_json_runs),
        "json_validity_rate": round((len(tool_call_runs) - len(bad_json_runs)) / len(tool_call_runs) * 100, 1) if tool_call_runs else 0,
        "content_with_tool_calls": len([r for r in tool_call_runs if r["content"]]),
        "tool_call_distribution": tool_call_counts,
        "finish_reasons": finish_reasons,
        "errors": errors_list,
    }

    if successful_times:
        stats["timing"] = {
            "avg": round(statistics.mean(successful_times), 3),
            "median": round(statistics.median(successful_times), 3),
            "min": round(min(successful_times), 3),
            "max": round(max(successful_times), 3),
            "stdev": round(statistics.stdev(successful_times), 3) if len(successful_times) > 1 else 0,
            "p90": round(sorted(successful_times)[int(len(successful_times) * 0.9)], 3) if len(successful_times) >= 10 else None,
            "p95": round(sorted(successful_times)[int(len(successful_times) * 0.95)], 3) if len(successful_times) >= 20 else None,
            "p99": round(sorted(successful_times)[int(len(successful_times) * 0.99)], 3) if len(successful_times) >= 100 else None,
        }

    # Usage stats
    if successful_runs:
        prompt_tokens = [r["usage"].get("prompt_tokens", 0) for r in successful_runs if r["usage"]]
        completion_tokens = [r["usage"].get("completion_tokens", 0) for r in successful_runs if r["usage"]]
        total_tokens = [r["usage"].get("total_tokens", 0) for r in successful_runs if r["usage"]]
        if prompt_tokens:
            stats["token_usage"] = {
                "avg_prompt_tokens": round(statistics.mean(prompt_tokens)),
                "avg_completion_tokens": round(statistics.mean(completion_tokens)),
                "avg_total_tokens": round(statistics.mean(total_tokens)),
                "total_prompt_tokens": sum(prompt_tokens),
                "total_completion_tokens": sum(completion_tokens),
                "total_all_tokens": sum(total_tokens),
            }

    results["stats"] = stats
    results["metadata"]["end_time"] = datetime.now().isoformat()

    # Save final results
    with open(f"{output_dir}/benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # === PRINT SUMMARY ===
    print(f"\n{'='*70}")
    print(f"BENCHMARK COMPLETE — {model}")
    print(f"{'='*70}")
    print(f"\n📊 Results Summary:")
    print(f"  Total runs:           {num_runs}")
    print(f"  Successful:           {stats['successful_runs']} ({stats['success_rate']}%)")
    print(f"  Failed:               {stats['failed_runs']}")
    print(f"  Tool call rate:       {stats['tool_call_rate']}% of successful runs")
    print(f"  JSON validity:        {stats['json_validity_rate']}% of tool calls")
    print(f"  Bad JSON args:        {stats['bad_json_runs']}")
    print(f"  Content + tool call:  {stats['content_with_tool_calls']} (ideally 0)")

    if "timing" in stats:
        t = stats["timing"]
        print(f"\n⏱️  Timing:")
        print(f"  Average:    {t['avg']}s")
        print(f"  Median:     {t['median']}s")
        print(f"  Min:        {t['min']}s")
        print(f"  Max:        {t['max']}s")
        print(f"  Std Dev:    {t['stdev']}s")
        if t.get("p90"): print(f"  P90:        {t['p90']}s")
        if t.get("p95"): print(f"  P95:        {t['p95']}s")

    if tool_call_counts:
        print(f"\n🔧 Tool Call Distribution:")
        for tn, count in sorted(tool_call_counts.items(), key=lambda x: x[1], reverse=True):
            pct = round(count / sum(tool_call_counts.values()) * 100, 1)
            bar = "█" * int(pct / 2)
            print(f"  {tn:<35} {count:3d} ({pct:5.1f}%) {bar}")

    if finish_reasons:
        print(f"\n🏁 Finish Reasons:")
        for fr, count in sorted(finish_reasons.items(), key=lambda x: x[1], reverse=True):
            print(f"  {str(fr or "none"):<20} {count:3d}")

    if errors_list:
        print(f"\n⚠️  Errors ({len(errors_list)}):")
        # Group by type
        error_types = {}
        for e in errors_list:
            et = e["type"]
            error_types[et] = error_types.get(et, 0) + 1
        for et, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {et}: {count}")
        # Show first 5 unique errors
        seen = set()
        for e in errors_list:
            key = e["error"][:100]
            if key not in seen:
                seen.add(key)
                print(f"  Run {e['run']}: [{e['type']}] {e['error'][:150]}")
                if len(seen) >= 5:
                    break

    if "token_usage" in stats:
        tu = stats["token_usage"]
        print(f"\n🪙 Token Usage:")
        print(f"  Avg prompt:     {tu['avg_prompt_tokens']}")
        print(f"  Avg completion: {tu['avg_completion_tokens']}")
        print(f"  Avg total:      {tu['avg_total_tokens']}")
        print(f"  Grand total:    {tu['total_all_tokens']}")

    print(f"\n📁 Results: {output_dir}/benchmark_results.json")
    return results


def generate_infographic(output_dir, api_key):
    """Generate a 4K infographic from benchmark results."""
    with open(f"{output_dir}/benchmark_results.json") as f:
        data = json.load(f)

    stats = data["stats"]
    meta = data["metadata"]
    timing = stats.get("timing", {})
    tool_dist = stats.get("tool_call_distribution", {})
    token_usage = stats.get("token_usage", {})
    errors = stats.get("errors", [])
    finish_reasons = stats.get("finish_reasons", {})

    # Build tool distribution text
    tool_lines = []
    if tool_dist:
        total_calls = sum(tool_dist.values())
        for tn, count in sorted(tool_dist.items(), key=lambda x: x[1], reverse=True):
            pct = round(count / total_calls * 100, 1)
            tool_lines.append(f"{tn}: {count} calls ({pct}%)")
    tool_text = ", ".join(tool_lines) if tool_lines else "No tool calls"

    # Finish reasons text
    fr_text = ", ".join(f"{k}: {v}" for k, v in sorted(finish_reasons.items(), key=lambda x: x[1], reverse=True))

    # Error summary
    error_types = {}
    for e in errors:
        error_types[e["type"]] = error_types.get(e["type"], 0) + 1
    error_text = ", ".join(f"{k}: {v}" for k, v in error_types.items()) if error_types else "No errors"

    prompt = f"""Premium dark-themed data infographic titled 'VENICE AI CHAT BENCHMARK' with subtitle 'Tool Choice Stress Test — {meta["model"]} — {stats["total_runs"]} Runs — {meta.get("start_time","")[:10]}'. Sleek modern design with dark navy-black background, neon green and electric cyan accent colors, glowing AI circuit patterns. 

Layout: TOP SECTION: Large glowing title banner with AI brain icon. Key stats row: '{stats["total_runs"]} Total Runs' '{stats["success_rate"]}% Success Rate' '{stats["tool_call_rate"]}% Tool Call Rate' '{stats["json_validity_rate"]}% JSON Valid' '{len(meta.get("tool_names",[]))} Tools Defined'. 

MIDDLE LEFT: Performance gauge showing Average Response Time {timing.get("avg","N/A")}s, Median {timing.get("median","N/A")}s, Min {timing.get("min","N/A")}s, Max {timing.get("max","N/A")}s, StdDev {timing.get("stdev","N/A")}s, P90 {timing.get("p90","N/A")}s. 

MIDDLE RIGHT: Horizontal bar chart of Tool Call Distribution: {tool_text}. Bars in gradient neon colors. 

BOTTOM LEFT: Reliability metrics: {stats["successful_runs"]} successful, {stats["failed_runs"]} failed, {stats["bad_json_runs"]} bad JSON responses, {stats["content_with_tool_calls"]} responses had content alongside tool calls. Finish reasons: {fr_text}. 

BOTTOM CENTER: Token usage stats: Avg prompt {token_usage.get("avg_prompt_tokens","N/A")} tokens, Avg completion {token_usage.get("avg_completion_tokens","N/A")} tokens, Total {token_usage.get("total_all_tokens","N/A")} tokens across all runs. 

BOTTOM RIGHT: Error breakdown: {error_text}. 

All text crisp and legible, professional data dashboard style, glowing neon data points, subtle encryption circuit patterns in background. Model name '{meta["model"]}' prominently displayed."""

    print(f"\n🎨 Generating 4K infographic...")
    img_output = f"{output_dir}/benchmark_infographic"

    cmd = [
        "python", "/a0/usr/skills/venice-image-gen/scripts/generate_image.py",
        prompt,
        "--resolution", "4K",
        "--aspect_ratio", "16:9",
        "--format", "png",
        "--output", img_output
    ]

    env = os.environ.copy()
    env["VENICE_API_KEY"] = api_key

    result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=120)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode == 0:
        print(f"✅ Infographic saved to: {img_output}.png")
    else:
        print(f"❌ Infographic generation failed (exit code {result.returncode})")

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Venice Chat Model Benchmark")
    parser.add_argument("--model", default="minimax-m27", help="Model ID to test")
    parser.add_argument("--runs", type=int, default=50, help="Number of runs")
    parser.add_argument("--timeout", type=int, default=120, help="Request timeout in seconds")
    parser.add_argument("--output", default="/a0/usr/workdir/chat_benchmark", help="Output directory")
    parser.add_argument("--infographic", action="store_true", help="Generate 4K infographic")
    args = parser.parse_args()

    api_key = os.environ.get("VENICE_API_KEY", "")
    if not api_key:
        print("ERROR: VENICE_API_KEY environment variable not set")
        sys.exit(1)

    results = run_benchmark(api_key, args.model, args.runs, args.output, args.timeout)

    if args.infographic:
        generate_infographic(args.output, api_key)


if __name__ == "__main__":
    main()

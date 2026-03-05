"""# Venice.ai Chat Instrument
Chat with Venice.ai LLM models, analyze images.
Usage: chat(message, system=None, image=None, reasoning=False, ...)

NOTE: Most parameters are NOT needed for typical use.
Just provide a message and let defaults handle the rest.

VISION SUPPORT:
  Models with vision capability (can analyze images):
  - qwen3-vl-235b-a22b (Qwen3 VL 235B) - RECOMMENDED, best value, 250K context
  - mistral-31-24b (Venice Medium) - reliable alternative
  Other models like Claude, Gemini, GPT may also support vision.
"""

import os
import sys
import base64
import argparse
import requests
from pathlib import Path

# API Configuration
VENICE_API_URL = "https://api.venice.ai/api/v1/chat/completions"
VENICE_API_KEY = os.getenv("VENICE_API_KEY")

# Default Models
DEFAULT_MODEL = "zai-org-glm-4.7"  # GLM 4.7 - most intelligent
DEFAULT_VISION_MODEL = "qwen3-vl-235b-a22b"  # Qwen3 VL 235B - best value vision model, 250K context
DEFAULT_REASONING_MODEL = "qwen3-235b-a22b-thinking-2507"  # Reasoning default


def encode_image(image_path: str) -> tuple[str, str]:
    """Encode image to base64 with mime type."""
    path = Path(image_path)
    suffix = path.suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    mime_type = mime_types.get(suffix, "image/png")
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    return data, mime_type


def chat(
    message: str,
    system: str = None,
    model: str = None,
    image: str = None,
    reasoning: bool = False,
    temperature: float = 0.7,
    max_tokens: int = None,
    web_search: bool = False,
) -> dict:
    """
    Chat with Venice.ai LLM.

    Args:
        message: User message (required)
        system: System prompt
        model: Model ID (auto-selected based on task if not provided)
        image: Path to image for vision analysis
        reasoning: Enable reasoning mode
        temperature: 0.0-2.0 (default: 0.7)
        max_tokens: Max response tokens
        web_search: Enable web search

    Returns:
        dict with response text and metadata
    """
    if not VENICE_API_KEY:
        raise ValueError("VENICE_API_KEY environment variable not set")

    # Auto-select model based on task
    if model is None:
        if image:
            model = DEFAULT_VISION_MODEL
        elif reasoning:
            model = DEFAULT_REASONING_MODEL
        else:
            model = DEFAULT_MODEL

    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build messages
    messages = []
    if system:
        messages.append({"role": "system", "content": system})

    # Build user message content
    if image:
        img_data, mime_type = encode_image(image)
        content = [
            {"type": "text", "text": message},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{img_data}"
                }
            }
        ]
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": message})

    # Build payload
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }

    if max_tokens:
        payload["max_tokens"] = max_tokens

    if reasoning:
        payload["reasoning"] = {"effort": "medium"}

    if web_search:
        payload["venice_parameters"] = {"enable_web_search": "on"}

    print(f"Chatting with {model}...")

    response = requests.post(VENICE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    # Extract response
    choices = data.get("choices", [])
    if not choices:
        return {"success": False, "error": "No response from model"}

    reply = choices[0].get("message", {}).get("content", "")
    usage = data.get("usage", {})

    return {
        "success": True,
        "model": model,
        "response": reply,
        "usage": {
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Chat with Venice.ai LLM")
    parser.add_argument("message", help="Your message")
    parser.add_argument("--system", "-s", help="System prompt")
    parser.add_argument("--model", "-m", help="Model ID")
    parser.add_argument("--image", "-i", help="Image path for vision analysis")
    parser.add_argument("--reasoning", "-r", action="store_true", help="Enable reasoning mode")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, help="Temperature (0.0-2.0)")
    parser.add_argument("--max_tokens", type=int, help="Max response tokens")
    parser.add_argument("--web_search", "-w", action="store_true", help="Enable web search")

    args = parser.parse_args()

    result = chat(
        message=args.message,
        system=args.system,
        model=args.model,
        image=args.image,
        reasoning=args.reasoning,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        web_search=args.web_search,
    )

    if result["success"]:
        print(f"\n--- Response from {result['model']} ---\n")
        print(result["response"])
        print(f"\n--- Tokens: {result['usage']['total_tokens']} ---")
    else:
        print(f"\nError: {result.get('error')}") 
        sys.exit(1)


if __name__ == "__main__":
    main()

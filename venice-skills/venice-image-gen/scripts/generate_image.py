"""# Venice.ai Image Generation Instrument
Generate images using Venice.ai API.
Usage: generate_image(prompt, model="nano-banana-2", resolution="1K", ...)

NOTE: Most parameters are NOT needed for typical use.
Just provide a good prompt and let defaults handle the rest.
"""

import os
import sys
import base64
import argparse
import requests
from pathlib import Path
from datetime import datetime

# API Configuration
VENICE_API_URL = "https://api.venice.ai/api/v1/image/generate"
VENICE_API_KEY = os.getenv("VENICE_API_KEY")

# Defaults
DEFAULT_MODEL = "nano-banana-2"  # Google Nano Banana - fast & good quality
DEFAULT_RESOLUTION = "1K"
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_FORMAT = "webp"


def generate_image(
    prompt: str,
    model: str = DEFAULT_MODEL,
    resolution: str = DEFAULT_RESOLUTION,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    negative_prompt: str = None,
    variants: int = 1,
    format: str = DEFAULT_FORMAT,
    seed: int = None,
    safe_mode: bool = True,
    output_path: str = None,
) -> dict:
    """
    Generate image(s) using Venice.ai API.

    Args:
        prompt: Image description (required)
        model: Model ID (default: nano-banana-2)
        resolution: 1K, 2K, or 4K (default: 1K)
        aspect_ratio: e.g. 1:1, 16:9, 9:16 (default: 1:1)
        negative_prompt: What to avoid in the image
        variants: Number of images 1-4 (default: 1)
        format: webp, png, or jpeg (default: webp)
        seed: Random seed for reproducibility
        safe_mode: Blur adult content (default: True)
        output_path: Save path (auto-generated if not provided)

    Returns:
        dict with image paths and generation info
    """
    if not VENICE_API_KEY:
        raise ValueError("VENICE_API_KEY environment variable not set")

    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Build request payload - only include non-default/set values
    payload = {
        "model": model,
        "prompt": prompt,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "format": format,
        "safe_mode": safe_mode,
        "return_binary": False,  # Get base64 for easier handling
    }

    if negative_prompt:
        payload["negative_prompt"] = negative_prompt
    if variants > 1:
        payload["variants"] = variants
    if seed is not None:
        payload["seed"] = seed

    print(f"Generating image with {model}...")
    print(f"Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")

    response = requests.post(VENICE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()

    # Save images
    saved_files = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    images = data.get("images", [])
    if not images:
        print("No images returned")
        return {"success": False, "error": "No images in response"}

    for i, img_data in enumerate(images):
        # Determine output filename
        if output_path:
            if len(images) > 1:
                base = Path(output_path)
                filepath = base.parent / f"{base.stem}_{i+1}{base.suffix or '.' + format}"
            else:
                filepath = Path(output_path)
                if not filepath.suffix:
                    filepath = Path(f"{output_path}.{format}")
        else:
            suffix = f"_{i+1}" if len(images) > 1 else ""
            filepath = Path(f"generated_{timestamp}{suffix}.{format}")

        # Decode and save
        img_bytes = base64.b64decode(img_data)
        filepath.write_bytes(img_bytes)
        saved_files.append(str(filepath.absolute()))
        print(f"Saved: {filepath.absolute()}")

    return {
        "success": True,
        "model": model,
        "prompt": prompt,
        "images": saved_files,
        "count": len(saved_files),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate images with Venice.ai")
    parser.add_argument("prompt", help="Image description")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION, choices=["1K", "2K", "4K"], help="Resolution")
    parser.add_argument("--aspect_ratio", default=DEFAULT_ASPECT_RATIO, help="Aspect ratio (e.g. 1:1, 16:9)")
    parser.add_argument("--negative_prompt", help="What to avoid")
    parser.add_argument("--variants", type=int, default=1, choices=[1,2,3,4], help="Number of images")
    parser.add_argument("--format", default=DEFAULT_FORMAT, choices=["webp", "png", "jpeg"], help="Image format")
    parser.add_argument("--seed", type=int, help="Random seed")
    parser.add_argument("--no-safe-mode", action="store_true", help="Disable safe mode")
    parser.add_argument("--output", "-o", help="Output path")

    args = parser.parse_args()

    result = generate_image(
        prompt=args.prompt,
        model=args.model,
        resolution=args.resolution,
        aspect_ratio=args.aspect_ratio,
        negative_prompt=args.negative_prompt,
        variants=args.variants,
        format=args.format,
        seed=args.seed,
        safe_mode=not args.no_safe_mode,
        output_path=args.output,
    )

    if result["success"]:
        print(f"\nGenerated {result['count']} image(s)")
    else:
        print(f"\nFailed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

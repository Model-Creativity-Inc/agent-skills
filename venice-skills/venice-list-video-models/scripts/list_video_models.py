"""List Venice.ai Video Models

This instrument fetches and displays all available video generation models from Venice.ai API
with comprehensive specifications for each model including:
- Supported durations
- Valid resolutions  
- Aspect ratios (if configurable)
- Audio capabilities (generation, input, configurable)
- Video input support
- Beta/offline status

This information is CRITICAL for video generation - each model has different valid
parameter combinations that must be respected.

Usage:
    python list_video_models.py              # List all models
    python list_video_models.py --detailed   # Show full specs for each model
    python list_video_models.py --model <id> # Show specs for specific model
    python list_video_models.py --json       # Output as JSON
"""

import os
import sys
import json
import requests
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class VideoModelSpec:
    """Complete specification for a video generation model."""
    id: str
    name: str
    model_type: str  # text-to-video, image-to-video, video
    
    # Generation constraints
    durations: list = field(default_factory=list)
    resolutions: list = field(default_factory=list)
    aspect_ratios: list = field(default_factory=list)
    
    # Audio capabilities
    audio: bool = False
    audio_configurable: bool = False
    audio_input: bool = False
    
    # Input requirements
    video_input: bool = False
    requires_image: bool = False
    
    # Status
    beta: bool = False
    offline: bool = False
    privacy: str = "anonymized"


VENICE_API_URL = "https://api.venice.ai/api/v1/models"
VENICE_API_KEY = os.getenv("VENICE_API_KEY")


def fetch_video_models():
    """Fetch all video models from Venice.ai API."""
    if not VENICE_API_KEY:
        raise ValueError("VENICE_API_KEY environment variable not set")
    
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(VENICE_API_URL, headers=headers, params={"type": "video"}, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    models = []
    
    for item in data.get("data", []):
        spec = item.get("model_spec", {})
        constraints = spec.get("constraints", {})
        model_type = constraints.get("model_type", "unknown")
        
        models.append(VideoModelSpec(
            id=item.get("id", ""),
            name=spec.get("name", item.get("id", "Unknown")),
            model_type=model_type,
            durations=constraints.get("durations", []),
            resolutions=constraints.get("resolutions", []),
            aspect_ratios=constraints.get("aspect_ratios", []),
            audio=constraints.get("audio", False),
            audio_configurable=constraints.get("audio_configurable", False),
            audio_input=constraints.get("audio_input", False),
            video_input=constraints.get("video_input", False),
            requires_image=(model_type == "image-to-video"),
            beta=spec.get("beta", False),
            offline=spec.get("offline", False),
            privacy=spec.get("privacy", "anonymized")
        ))
    
    return models


def format_summary_table(models):
    """Format models as summary table grouped by type."""
    lines = []

    by_type = {}
    for m in models:
        by_type.setdefault(m.model_type, []).append(m)

    for mtype in ["text-to-video", "image-to-video", "video"]:
        if mtype not in by_type:
            continue

        type_models = by_type[mtype]
        lines.append("")
        lines.append("=" * 115)
        lines.append(f" {mtype.upper()} MODELS ({len(type_models)})")
        lines.append("=" * 115)
        lines.append("")
        lines.append(f" {'Model ID':<40} {'Durations':<25} {'Res':<12} {'Audio':<12} {'Audio In'}")
        lines.append(f" {'-'*40} {'-'*25} {'-'*12} {'-'*12} {'-'*10}")

        for m in sorted(type_models, key=lambda x: x.name):
            durations = ", ".join(m.durations) if m.durations else "N/A"
            resolutions = ", ".join(m.resolutions) if m.resolutions else "default"
            audio = "Yes" if m.audio else "No"
            if m.audio_configurable:
                audio += " (cfg)"
            audio_in = "Yes" if m.audio_input else "No"
            status = ""
            if m.beta:
                status = " [BETA]"
            if m.offline:
                status = " [OFFLINE]"

            lines.append(f" {m.id:<40} {durations:<25} {resolutions:<12} {audio:<12} {audio_in}{status}")

    return "\n".join(lines)


def format_detailed_spec(model):
    """Format detailed specs for a single model."""
    lines = []
    lines.append("")
    lines.append("=" * 75)
    lines.append(f" {model.name}")
    lines.append(f" ID: {model.id}")
    lines.append("=" * 75)
    lines.append("")
    lines.append(f"  Type:        {model.model_type}")
    
    status = []
    if model.beta:
        status.append("BETA")
    if model.offline:
        status.append("OFFLINE")
    if status:
        lines.append(f"  Status:      {', '.join(status)}")
    
    lines.append("")
    lines.append("  GENERATION PARAMETERS:")
    lines.append("  " + "-" * 40)
    
    if model.durations:
        lines.append(f"  duration:      {' | '.join(model.durations)}")
    else:
        lines.append(f"  duration:      (not configurable)")
    
    if model.resolutions:
        lines.append(f"  resolution:    {' | '.join(model.resolutions)}")
    else:
        lines.append(f"  resolution:    (model default)")
    
    if model.aspect_ratios:
        lines.append(f"  aspect_ratio:  {' | '.join(model.aspect_ratios)}")
    else:
        lines.append(f"  aspect_ratio:  (NOT SUPPORTED - do not include in request)")
    
    lines.append("")
    lines.append("  AUDIO CAPABILITIES:")
    lines.append("  " + "-" * 40)
    lines.append(f"  audio:              {'Yes - generates audio' if model.audio else 'No'}")
    lines.append(f"  audio_configurable: {'Yes - can toggle on/off' if model.audio_configurable else 'No'}")
    lines.append(f"  audio_input:        {'Yes - accepts audio' if model.audio_input else 'No'}")
    
    lines.append("")
    lines.append("  INPUT REQUIREMENTS:")
    lines.append("  " + "-" * 40)
    if model.model_type == "text-to-video":
        lines.append(f"  prompt:     Required (text description)")
        lines.append(f"  image_url:  Not used")
    elif model.model_type == "image-to-video":
        lines.append(f"  prompt:     Required (text description)")
        lines.append(f"  image_url:  REQUIRED (base64 data URL or HTTP URL)")
    elif model.model_type == "video":
        lines.append(f"  prompt:     Required (text description)")
        lines.append(f"  video_url:  {'Required' if model.video_input else 'Optional'}")
    
    return "\n".join(lines)


def format_generation_example(model):
    """Generate example API call for this model."""
    example = {
        "model": model.id,
        "prompt": "Your detailed prompt here"
    }
    
    if model.durations:
        example["duration"] = model.durations[0]
    
    if model.resolutions:
        example["resolution"] = model.resolutions[0]
    
    if model.aspect_ratios:
        example["aspect_ratio"] = model.aspect_ratios[0]
    
    if model.audio_configurable:
        example["audio"] = True
    
    if model.model_type == "image-to-video":
        example["image_url"] = "data:image/jpeg;base64,... OR https://..."
    
    return json.dumps(example, indent=2)


def output_json(models):
    """Output all models as JSON."""
    return json.dumps([asdict(m) for m in models], indent=2)


def main():
    args = sys.argv[1:]
    
    print("Fetching Venice.ai video models...")
    print()
    
    try:
        models = fetch_video_models()
        
        if "--json" in args:
            print(output_json(models))
            return
        
        if "--model" in args:
            idx = args.index("--model")
            if idx + 1 < len(args):
                model_id = args[idx + 1]
                matching = [m for m in models if m.id == model_id or model_id in m.id]
                if matching:
                    for m in matching:
                        print(format_detailed_spec(m))
                        print("\n  EXAMPLE API REQUEST:")
                        print("  " + "-" * 40)
                        for line in format_generation_example(m).split("\n"):
                            print(f"    {line}")
                else:
                    print(f"No model found matching: {model_id}")
                return
        
        if "--detailed" in args:
            for m in models:
                print(format_detailed_spec(m))
            return
        
        print(f"Total video models available: {len(models)}")
        print(format_summary_table(models))
        
        print()
        print("=" * 100)
        print(" USAGE")
        print("=" * 100)
        print("""
  --model <id>   Show detailed specs for a specific model
  --detailed     Show specs for all models
  --json         Output as JSON

  CRITICAL FOR VIDEO GENERATION:
  * Each model has specific valid durations - use ONLY listed values
  * aspect_ratio: ONLY include if model lists them (otherwise causes 400 errors)
  * audio: check audio_configurable before including
  * image-to-video models REQUIRE image_url parameter
""")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

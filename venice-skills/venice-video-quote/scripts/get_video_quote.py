"""# Venice.ai Video Quote Instrument
Get cost estimate for video generation before creating.
Validates parameters against model capabilities from the video models endpoint.
Usage: get_video_quote(model, duration, aspect_ratio="16:9", resolution="720p", audio=False)
"""

import os
import requests
from typing import Optional
from pydantic import BaseModel, Field

# API Configuration
VENICE_QUOTE_URL = "https://api.venice.ai/api/v1/video/quote"
VENICE_MODELS_URL = "https://api.venice.ai/api/v1/models"
VENICE_API_KEY = os.getenv("VENICE_API_KEY")

# Pydantic Models
class VideoQuoteRequest(BaseModel):
    model: str
    duration: str
    aspect_ratio: str = "16:9"
    resolution: str = "720p"
    audio: bool = False

class VideoQuoteResponse(BaseModel):
    quote: float
    model: Optional[str] = None
    config: Optional[dict] = None

class ModelCapabilities(BaseModel):
    """Extracted capabilities for a video model."""
    model_id: str
    name: str
    model_type: str
    durations: list[str]
    aspect_ratios: list[str]
    resolutions: list[str]
    supports_audio: bool


def get_video_model_capabilities(model_id: str) -> Optional[ModelCapabilities]:
    """Fetch capabilities for a specific video model."""
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        VENICE_MODELS_URL,
        headers=headers,
        params={"type": "video"},
        timeout=30
    )
    response.raise_for_status()
    
    data = response.json()
    for model in data.get("data", []):
        if model["id"] == model_id:
            spec = model.get("model_spec", {})
            constraints = spec.get("constraints", {})
            return ModelCapabilities(
                model_id=model["id"],
                name=spec.get("name", model["id"]),
                model_type=constraints.get("model_type", "unknown"),
                durations=constraints.get("durations", []),
                aspect_ratios=constraints.get("aspect_ratios", []),
                resolutions=constraints.get("resolutions", []),
                supports_audio=constraints.get("supported_audio", {}).get("configurable", False)
            )
    return None


def validate_quote_params(caps: ModelCapabilities, duration: str, aspect_ratio: str, resolution: str, audio: bool) -> list[str]:
    """Validate quote parameters against model capabilities."""
    errors = []
    
    if duration not in caps.durations:
        errors.append(f"Invalid duration '{duration}'. Valid: {caps.durations}")
    
    if aspect_ratio not in caps.aspect_ratios:
        errors.append(f"Invalid aspect_ratio '{aspect_ratio}'. Valid: {caps.aspect_ratios}")
    
    if resolution not in caps.resolutions:
        errors.append(f"Invalid resolution '{resolution}'. Valid: {caps.resolutions}")
    
    if audio and not caps.supports_audio:
        errors.append(f"Model '{caps.model_id}' does not support audio")
    
    return errors


def get_video_quote(
    model: str,
    duration: str,
    aspect_ratio: str = "16:9",
    resolution: str = "720p",
    audio: bool = False,
    validate: bool = True
) -> VideoQuoteResponse:
    """Get price quote for video generation with optional validation."""
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Validate against model capabilities
    if validate:
        caps = get_video_model_capabilities(model)
        if caps is None:
            raise ValueError(f"Model '{model}' not found. Use list_video_models() to see available models.")
        
        errors = validate_quote_params(caps, duration, aspect_ratio, resolution, audio)
        if errors:
            error_msg = f"Invalid parameters for model '{model}': " + "; ".join(errors)
            raise ValueError(error_msg)
    
    request = VideoQuoteRequest(
        model=model,
        duration=duration,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        audio=audio
    )
    
    response = requests.post(
        VENICE_QUOTE_URL,
        headers=headers,
        json=request.model_dump(),
        timeout=30
    )
    response.raise_for_status()
    
    result = VideoQuoteResponse(**response.json())
    result.model = model
    result.config = request.model_dump()
    return result


def show_model_options(model_id: str) -> None:
    """Print valid options for a video model."""
    caps = get_video_model_capabilities(model_id)
    if caps is None:
        print(f"Model '{model_id}' not found")
        return
    
    print(f"Model: {caps.name} ({caps.model_id})")
    print(f"Type: {caps.model_type}")
    print(f"Durations: {', '.join(caps.durations)}")
    print(f"Aspect Ratios: {', '.join(caps.aspect_ratios)}")
    print(f"Resolutions: {', '.join(caps.resolutions)}")
    print(f"Audio: {'Yes' if caps.supports_audio else 'No'}")


if __name__ == "__main__":
    print("=" * 70)
    print("Venice.ai Video Quote - With Model Validation")
    print("=" * 70)
    
    # Show options for models
    print("\n>>> Model: wan-2.5-preview-text-to-video")
    show_model_options("wan-2.5-preview-text-to-video")
    
    print("\n>>> Model: ltx-2-fast-text-to-video")
    show_model_options("ltx-2-fast-text-to-video")
    
    # Valid quote
    print("\n" + "-" * 70)
    print("Testing VALID quote request:")
    try:
        quote = get_video_quote(
            model="wan-2.5-preview-text-to-video",
            duration="10s",
            aspect_ratio="16:9",
            resolution="720p",
            audio=True
        )
        print(f"  ✅ Quote: ${quote.quote:.2f}")
    except ValueError as e:
        print(f"  ❌ {e}")
    
    # Invalid quote (wrong resolution for LTX)
    print("\nTesting INVALID quote request (720p on LTX model):")
    try:
        quote = get_video_quote(
            model="ltx-2-fast-text-to-video",
            duration="10s",
            aspect_ratio="16:9",
            resolution="720p",
            audio=True
        )
        print(f"  Quote: ${quote.quote:.2f}")
    except ValueError as e:
        print(f"  ✅ Caught validation error: {e}")

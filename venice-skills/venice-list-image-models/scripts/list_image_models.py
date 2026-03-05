"""# Venice.ai List Image Models Instrument
List available image generation models from Venice.ai API.
Returns model names, pricing, constraints, and capabilities.
Usage: list_image_models() - returns all image models with pricing and constraints
"""

import os
import requests
from typing import Optional
from pydantic import BaseModel, Field

# API Configuration
VENICE_API_URL = "https://api.venice.ai/api/v1/models"
VENICE_API_KEY = os.getenv("VENICE_API_KEY")

# Pydantic Models
class PricePoint(BaseModel):
    usd: float
    diem: float

class UpscalePricing(BaseModel):
    x2: Optional[PricePoint] = Field(default=None, alias="2x")
    x4: Optional[PricePoint] = Field(default=None, alias="4x")

class ResolutionPricing(BaseModel):
    r1k: Optional[PricePoint] = Field(default=None, alias="1K")
    r2k: Optional[PricePoint] = Field(default=None, alias="2K")
    r4k: Optional[PricePoint] = Field(default=None, alias="4K")

class ImagePricing(BaseModel):
    generation: Optional[PricePoint] = None
    resolutions: Optional[ResolutionPricing] = None
    upscale: Optional[UpscalePricing] = None

class StepsConstraint(BaseModel):
    default: int
    max: int

class ImageConstraints(BaseModel):
    promptCharacterLimit: int = 1500
    steps: Optional[StepsConstraint] = None
    widthHeightDivisor: int = 1
    defaultResolution: Optional[str] = None
    resolutions: Optional[list[str]] = None

class ImageModelSpec(BaseModel):
    pricing: ImagePricing
    constraints: ImageConstraints
    supportsWebSearch: bool = False
    name: str
    modelSource: Optional[str] = None
    offline: bool = False
    privacy: str = "private"
    traits: list[str] = Field(default_factory=list)

class ImageModel(BaseModel):
    created: int
    id: str
    model_spec: ImageModelSpec
    object: str = "model"
    owned_by: str = ""
    type: str = "image"

class ImageModelsResponse(BaseModel):
    data: list[ImageModel]
    object: str = "list"
    type: str = "image"


def list_image_models() -> ImageModelsResponse:
    """
    Fetch image generation models from Venice.ai API.

    Returns:
        ImageModelsResponse with list of available image models
    """
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }
    params = {"type": "image"}

    response = requests.get(VENICE_API_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return ImageModelsResponse(**data)


def get_generation_price(spec: ImageModelSpec) -> float:
    """Get the base generation price (handles both flat and resolution-based pricing)."""
    if spec.pricing.generation:
        return spec.pricing.generation.usd
    elif spec.pricing.resolutions and spec.pricing.resolutions.r1k:
        return spec.pricing.resolutions.r1k.usd
    return 0.0


def format_models_table(models: ImageModelsResponse) -> str:
    """Format models as a readable table."""
    lines = []
    lines.append(f"{'Model ID':<25} {'Name':<25} {'Gen $':<10} {'2x Up $':<8} {'4x Up $':<8} {'Steps':<12} {'Prompt Limit'}")
    lines.append("-" * 115)

    for m in sorted(models.data, key=lambda x: get_generation_price(x.model_spec)):
        spec = m.model_spec

        # Handle both pricing formats
        if spec.pricing.generation:
            gen_price = f"{spec.pricing.generation.usd:.2f}"
        elif spec.pricing.resolutions:
            prices = []
            if spec.pricing.resolutions.r1k: prices.append(f"1K:{spec.pricing.resolutions.r1k.usd:.2f}")
            if spec.pricing.resolutions.r2k: prices.append(f"2K:{spec.pricing.resolutions.r2k.usd:.2f}")
            if spec.pricing.resolutions.r4k: prices.append(f"4K:{spec.pricing.resolutions.r4k.usd:.2f}")
            gen_price = ",".join(prices) if prices else "-"
        else:
            gen_price = "-"

        up2x = f"{spec.pricing.upscale.x2.usd:.2f}" if spec.pricing.upscale and spec.pricing.upscale.x2 else "-"
        up4x = f"{spec.pricing.upscale.x4.usd:.2f}" if spec.pricing.upscale and spec.pricing.upscale.x4 else "-"
        steps = f"{spec.constraints.steps.default}/{spec.constraints.steps.max}" if spec.constraints.steps else "-"
        prompt_limit = spec.constraints.promptCharacterLimit

        lines.append(
            f"{m.id:<25} {spec.name:<25} {gen_price:<10} {up2x:<8} {up4x:<8} {steps:<12} {prompt_limit}"
        )

    return "\n".join(lines)


def get_models_summary(models: ImageModelsResponse) -> dict:
    """Get summary statistics for image models."""
    prices = [get_generation_price(m.model_spec) for m in models.data]
    return {
        "total_models": len(models.data),
        "min_price": min(prices),
        "max_price": max(prices),
        "avg_price": sum(prices) / len(prices),
        "with_web_search": sum(1 for m in models.data if m.model_spec.supportsWebSearch),
        "offline_models": sum(1 for m in models.data if m.model_spec.offline)
    }


if __name__ == "__main__":
    print("Fetching Venice.ai image models...\n")
    models = list_image_models()

    print(f"Total image models available: {len(models.data)}\n")
    print(format_models_table(models))

    print("\n=== Summary ===")
    summary = get_models_summary(models)
    print(f"  Total models: {summary['total_models']}")
    print(f"  Price range: ${summary['min_price']:.2f} - ${summary['max_price']:.2f}")
    print(f"  Average price: ${summary['avg_price']:.3f}")

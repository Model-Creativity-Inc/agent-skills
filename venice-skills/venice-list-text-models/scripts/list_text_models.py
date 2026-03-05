"""# Venice.ai List Text Models Instrument
List available text/LLM models from Venice.ai API.
Returns model names, capabilities, context windows, and pricing.
Usage: list_text_models(filter_trait=None) - optionally filter by trait like "most_intelligent", "default"
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

class Pricing(BaseModel):
    input: PricePoint
    output: PricePoint
    cache_input: Optional[PricePoint] = None

class Capabilities(BaseModel):
    optimizedForCode: bool = False
    quantization: Optional[str] = None
    supportsAudioInput: bool = False
    supportsFunctionCalling: bool = False
    supportsLogProbs: bool = False
    supportsReasoning: bool = False
    supportsResponseSchema: bool = False
    supportsVideoInput: bool = False
    supportsVision: bool = False
    supportsWebSearch: bool = False

class ParameterConstraint(BaseModel):
    default: float

class Constraints(BaseModel):
    temperature: Optional[ParameterConstraint] = None
    top_p: Optional[ParameterConstraint] = None

class TextModelSpec(BaseModel):
    pricing: Pricing
    availableContextTokens: int
    capabilities: Capabilities
    constraints: Optional[Constraints] = None
    description: str = ""
    name: str
    modelSource: Optional[str] = None
    offline: bool = False
    privacy: str = "private"
    traits: list[str] = Field(default_factory=list)

class TextModel(BaseModel):
    created: int
    id: str
    model_spec: TextModelSpec
    object: str = "model"
    owned_by: str = ""
    type: str = "text"

class TextModelsResponse(BaseModel):
    data: list[TextModel]
    object: str = "list"
    type: str = "text"


def list_text_models(filter_trait: Optional[str] = None) -> TextModelsResponse:
    """
    Fetch text models from Venice.ai API.

    Args:
        filter_trait: Optional trait to filter by (e.g., "most_intelligent", "default", "most_uncensored")

    Returns:
        TextModelsResponse with list of available text models
    """
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }
    params = {"type": "text"}

    response = requests.get(VENICE_API_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    result = TextModelsResponse(**data)

    if filter_trait:
        result.data = [m for m in result.data if filter_trait in m.model_spec.traits]

    return result


def format_models_table(models: TextModelsResponse) -> str:
    """Format models as a readable table."""
    lines = []
    lines.append(f"{'Model ID':<35} {'Name':<30} {'Context':<10} {'In $/M':<8} {'Out $/M':<8} {'Traits'}")
    lines.append("-" * 120)

    for m in sorted(models.data, key=lambda x: x.model_spec.availableContextTokens, reverse=True):
        spec = m.model_spec
        ctx = f"{spec.availableContextTokens // 1024}K"
        traits = ", ".join(spec.traits) if spec.traits else "-"
        lines.append(
            f"{m.id:<35} {spec.name:<30} {ctx:<10} {spec.pricing.input.usd:<8.2f} {spec.pricing.output.usd:<8.2f} {traits}"
        )

    return "\n".join(lines)


def get_capabilities_summary(models: TextModelsResponse) -> dict:
    """Summarize capabilities across all models."""
    summary = {
        "total": len(models.data),
        "with_reasoning": 0,
        "with_vision": 0,
        "with_function_calling": 0,
        "with_web_search": 0,
        "optimized_for_code": 0
    }
    for m in models.data:
        cap = m.model_spec.capabilities
        if cap.supportsReasoning: summary["with_reasoning"] += 1
        if cap.supportsVision: summary["with_vision"] += 1
        if cap.supportsFunctionCalling: summary["with_function_calling"] += 1
        if cap.supportsWebSearch: summary["with_web_search"] += 1
        if cap.optimizedForCode: summary["optimized_for_code"] += 1
    return summary


if __name__ == "__main__":
    print("Fetching Venice.ai text models...\n")
    models = list_text_models()

    print(f"Total text models available: {len(models.data)}\n")
    print(format_models_table(models))

    print("\n=== Capabilities Summary ===")
    summary = get_capabilities_summary(models)
    for key, val in summary.items():
        print(f"  {key}: {val}")

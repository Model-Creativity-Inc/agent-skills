# Venice Skills

A collection of skills that wrap the [Venice.ai](https://venice.ai/) API for chat, image generation, video generation, text-to-speech, and model discovery. All skills require the `VENICE_API_KEY` environment variable.

## Skills

| Skill | Description |
|-------|-------------|
| [venice-chat](./venice-chat/) | Chat with Venice.ai LLMs with vision, reasoning mode, and web search |
| [venice-chat-benchmark](./venice-chat-benchmark/) | Benchmark Venice.ai chat models with tool_choice stress testing, timing stats, and 4K infographic |
| [venice-image-gen](./venice-image-gen/) | Generate images from text prompts (1K/2K/4K, multiple formats and aspect ratios) |
| [venice-tts](./venice-tts/) | Text-to-speech with 50+ voices across 9 languages |
| [venice-video-generate](./venice-video-generate/) | Full-lifecycle video generation (queue + poll + retrieve + save) |
| [venice-video-queue](./venice-video-queue/) | Queue a video for generation (text/image/video-to-video) |
| [venice-video-retrieve](./venice-video-retrieve/) | Retrieve and download a queued video by polling until complete |
| [venice-video-quote](./venice-video-quote/) | Get cost estimates for video generation with parameter validation |
| [venice-list-text-models](./venice-list-text-models/) | List available LLM models with capabilities, context windows, and pricing |
| [venice-list-image-models](./venice-list-image-models/) | List available image generation models with pricing and constraints |
| [venice-list-video-models](./venice-list-video-models/) | List available video models with durations, resolutions, and audio capabilities |

## Prerequisites

- Python 3.10+
- `requests` (`pip install requests`)
- `pydantic` (required by video and model-listing skills)
- `VENICE_API_KEY` environment variable set to your Venice.ai API key

```bash
pip install requests pydantic
export VENICE_API_KEY="your_venice_api_key"
```

## Structure

Each skill follows a consistent layout:

```
skill-name/
  SKILL.md          # Agent-facing documentation (frontmatter + usage)
  README.md         # Human-facing GitHub documentation
  scripts/          # Executable Python scripts
```

- **`SKILL.md`** -- YAML frontmatter (name, description, version, tags, trigger patterns) plus agent-facing usage instructions.
- **`README.md`** -- Human-readable documentation with examples.
- **`scripts/`** -- Python scripts that work both as CLI tools (via `argparse`) and as importable modules.

## Quick Start

### Chat

```bash
python venice-chat/scripts/chat.py "What is the capital of France?"
```

### Generate an image

```bash
python venice-image-gen/scripts/generate_image.py "A sunset over mountains"
```

### Generate a video

```bash
python venice-video-generate/scripts/generate_video.py "A timelapse of a blooming flower"
```

### Text-to-speech

```bash
python venice-tts/scripts/text_to_speech.py "Hello, world!"
```

### List available models

```bash
python venice-list-text-models/scripts/list_text_models.py
python venice-list-image-models/scripts/list_image_models.py
python venice-list-video-models/scripts/list_video_models.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

# Venice Text-to-Speech

Convert text to speech using the [Venice.ai](https://venice.ai/) TTS API. Supports 50+ voices across 9 languages with multiple audio formats and adjustable speed.

## Features

- **50+ voices** across American English, British English, Chinese, French, Hindi, Italian, Japanese, Portuguese
- **Multiple formats** -- mp3, opus, aac, flac, wav, pcm
- **Adjustable speed** -- 0.25x to 4.0x
- **Max 4096 characters** per request
- Model: `tts-kokoro`

## Prerequisites

```bash
pip install requests
export VENICE_API_KEY="your_venice_api_key"
```

## Usage

### Basic

```bash
python scripts/text_to_speech.py "Hello, welcome to Venice Voice."
```

### With voice selection

```bash
python scripts/text_to_speech.py "Hello world" --voice am_adam
```

### All options

```bash
python scripts/text_to_speech.py "Your text here" \
  --voice af_bella \
  --speed 1.2 \
  --format wav \
  --output greeting.wav
```

### List all voices

```bash
python scripts/text_to_speech.py "" --list-voices
```

## Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `text` | -- | *(required)* | Text to convert (max 4096 chars) |
| `--voice` | `-v` | `af_sky` | Voice ID |
| `--format` | `-f` | `mp3` | Audio format |
| `--speed` | `-s` | `1.0` | Speed (0.25-4.0) |
| `--output` | `-o` | auto | Output file path |
| `--list-voices` | -- | -- | List all available voices |

## Available Voices

| Prefix | Language | Voices |
|--------|----------|--------|
| `af_` | American Female | alloy, aoede, bella, heart, jadzia, jessica, kore, nicole, nova, river, sarah, sky |
| `am_` | American Male | adam, echo, eric, fenrir, liam, michael, onyx, puck, santa |
| `bf_` | British Female | alice, emma, lily |
| `bm_` | British Male | daniel, fable, george, lewis |
| `zf_` | Chinese Female | xiaobei, xiaoni, xiaoxiao, xiaoyi |
| `zm_` | Chinese Male | yunjian, yunxi, yunxia, yunyang |
| `ff_` | French Female | siwis |
| `hf_`/`hm_` | Hindi | alpha, beta, omega, psi |
| `if_`/`im_` | Italian | sara, nicola |
| `jf_`/`jm_` | Japanese | alpha, gongitsune, nezumi, tebukuro, kumo |
| `pf_`/`pm_` | Portuguese | dora, alex, santa |

## Python Import

```python
from text_to_speech import text_to_speech

result = text_to_speech(
    text="Hello, this is a test.",
    voice="am_adam",
    format="mp3",
    speed=1.0
)
print(f"Audio saved to: {result['output']}")
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VENICE_API_KEY` | Yes | Venice.ai API key |

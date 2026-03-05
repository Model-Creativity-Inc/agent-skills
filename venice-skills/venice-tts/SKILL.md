---
name: "venice-tts"
description: "Convert text to speech using Venice.ai TTS API with multiple voices and languages."
version: "1.0.0"
author: "Agent Zero"
tags:
  - venice
  - api
  - tts
  - speech
  - audio
  - voice
trigger_patterns:
  - "text to speech"
  - "tts"
  - "venice voice"
  - "generate speech"
  - "speak text"
  - "convert to audio"
---

# Venice Text-to-Speech

Convert text to speech using Venice.ai TTS API.

## When to Use

Use this skill when you need to:
- Convert text to audio/speech
- Generate voiceovers
- Create audio content in multiple languages

## Usage

### Basic
```bash
python /a0/usr/skills/venice-tts/scripts/text_to_speech.py "Hello, welcome to Venice Voice."
```

### With Voice Selection
```bash
python /a0/usr/skills/venice-tts/scripts/text_to_speech.py "Hello world" --voice am_adam
```

### All Options
```bash
python /a0/usr/skills/venice-tts/scripts/text_to_speech.py "Your text" --voice af_bella --speed 1.2 --format wav --output greeting.wav
```

## Available Voices

| Prefix | Language | Example Voices |
|--------|----------|----------------|
| af_ | American Female | alloy, bella, sky, nova, sarah |
| am_ | American Male | adam, echo, eric, liam, michael |
| bf_ | British Female | alice, emma, lily |
| bm_ | British Male | daniel, fable, george |
| jf_ | Japanese Female | alpha, gongitsune, nezumi |
| zf_ | Chinese Female | xiaobei, xiaoni, xiaoxiao |

## Options

| Option | Values | Default |
|--------|--------|--------|
| --voice | See table above | af_sky |
| --format | mp3, opus, aac, flac, wav, pcm | mp3 |
| --speed | 0.25 - 4.0 | 1.0 |
| --output | filename | auto-generated |

## Notes

- Max input: 4096 characters
- Requires `VENICE_API_KEY` environment variable

"""# Venice.ai Text-to-Speech Instrument
Convert text to speech using Venice.ai TTS API.
Usage: text_to_speech(text, voice="af_sky", format="mp3", speed=1.0)

NOTE: Max input 4096 characters.
"""

import os
import sys
import argparse
import requests
from pathlib import Path
from datetime import datetime

# API Configuration
VENICE_API_URL = "https://api.venice.ai/api/v1/audio/speech"
VENICE_API_KEY = os.getenv("VENICE_API_KEY")

# Defaults
DEFAULT_MODEL = "tts-kokoro"  # Only option currently
DEFAULT_VOICE = "af_sky"  # American female
DEFAULT_FORMAT = "mp3"
DEFAULT_SPEED = 1.0

# All available voices
VOICES = [
    # American Female
    "af_alloy", "af_aoede", "af_bella", "af_heart", "af_jadzia", "af_jessica",
    "af_kore", "af_nicole", "af_nova", "af_river", "af_sarah", "af_sky",
    # American Male
    "am_adam", "am_echo", "am_eric", "am_fenrir", "am_liam", "am_michael",
    "am_onyx", "am_puck", "am_santa",
    # British Female
    "bf_alice", "bf_emma", "bf_lily",
    # British Male
    "bm_daniel", "bm_fable", "bm_george", "bm_lewis",
    # Chinese Female
    "zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi",
    # Chinese Male
    "zm_yunjian", "zm_yunxi", "zm_yunxia", "zm_yunyang",
    # French Female
    "ff_siwis",
    # Hindi
    "hf_alpha", "hf_beta", "hm_omega", "hm_psi",
    # Italian
    "if_sara", "im_nicola",
    # Japanese
    "jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro", "jm_kumo",
    # Portuguese
    "pf_dora", "pm_alex", "pm_santa",
    # English (generic)
    "ef_dora", "em_alex", "em_santa",
]

FORMATS = ["mp3", "opus", "aac", "flac", "wav", "pcm"]


def text_to_speech(
    text: str,
    voice: str = DEFAULT_VOICE,
    format: str = DEFAULT_FORMAT,
    speed: float = DEFAULT_SPEED,
    output_path: str = None,
) -> dict:
    """
    Convert text to speech using Venice.ai TTS.

    Args:
        text: Text to convert (max 4096 characters)
        voice: Voice ID (default: af_sky)
        format: mp3, opus, aac, flac, wav, pcm (default: mp3)
        speed: 0.25-4.0 (default: 1.0)
        output_path: Save path (auto-generated if not provided)

    Returns:
        dict with audio path and metadata
    """
    if not VENICE_API_KEY:
        raise ValueError("VENICE_API_KEY environment variable not set")

    if len(text) > 4096:
        raise ValueError(f"Text too long: {len(text)} chars (max 4096)")

    if voice not in VOICES:
        print(f"Warning: Unknown voice '{voice}', using {DEFAULT_VOICE}")
        voice = DEFAULT_VOICE

    if format not in FORMATS:
        print(f"Warning: Unknown format '{format}', using {DEFAULT_FORMAT}")
        format = DEFAULT_FORMAT

    if not (0.25 <= speed <= 4.0):
        print(f"Warning: Speed {speed} out of range, clamping to [0.25, 4.0]")
        speed = max(0.25, min(4.0, speed))

    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "input": text,
        "model": DEFAULT_MODEL,
        "voice": voice,
        "response_format": format,
        "speed": speed,
        "streaming": False,
    }

    print(f"Generating speech with voice '{voice}'...")
    print(f"Text: {text[:80]}{'...' if len(text) > 80 else ''}")

    response = requests.post(VENICE_API_URL, headers=headers, json=payload)
    response.raise_for_status()

    # Response is binary audio data
    audio_data = response.content

    # Determine output path
    if output_path:
        filepath = Path(output_path)
        if not filepath.suffix:
            filepath = Path(f"{output_path}.{format}")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path(f"speech_{timestamp}.{format}")

    # Save audio
    filepath.write_bytes(audio_data)
    print(f"Saved: {filepath.absolute()}")

    return {
        "success": True,
        "voice": voice,
        "format": format,
        "speed": speed,
        "text_length": len(text),
        "audio_size": len(audio_data),
        "output": str(filepath.absolute()),
    }


def main():
    parser = argparse.ArgumentParser(description="Venice.ai Text-to-Speech")
    parser.add_argument("text", help="Text to convert (max 4096 chars)")
    parser.add_argument("--voice", "-v", default=DEFAULT_VOICE, help=f"Voice (default: {DEFAULT_VOICE})")
    parser.add_argument("--format", "-f", default=DEFAULT_FORMAT, choices=FORMATS, help="Audio format")
    parser.add_argument("--speed", "-s", type=float, default=DEFAULT_SPEED, help="Speed 0.25-4.0")
    parser.add_argument("--output", "-o", help="Output path")
    parser.add_argument("--list-voices", action="store_true", help="List all voices")

    args = parser.parse_args()

    if args.list_voices:
        print("Available voices:")
        for v in VOICES:
            print(f"  {v}")
        return

    result = text_to_speech(
        text=args.text,
        voice=args.voice,
        format=args.format,
        speed=args.speed,
        output_path=args.output,
    )

    if result["success"]:
        print(f"\nGenerated {result['audio_size']} bytes of audio")
    else:
        print(f"\nError: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""# Venice.ai Video Queue Skill
Queue a video for generation (text-to-video, image-to-video, or video-to-video).

Usage:
  python queue_video.py "prompt" [options]

Examples:
  # Text-to-video
  python queue_video.py "A cat playing piano" --model wan-2.5-preview-text-to-video --duration 5s

  # Image-to-video
  python queue_video.py "Make this image come alive" --image /path/to/image.png --model wan-2.5-preview-image-to-video
"""

import os
import sys
import json
import base64
import argparse
import requests
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

# API Configuration
VENICE_QUEUE_URL = "https://api.venice.ai/api/v1/video/queue"
VENICE_API_KEY = os.getenv("VENICE_API_KEY")


class VideoQueueResponse(BaseModel):
    """Response from video queue endpoint."""
    model: str
    queue_id: str


def encode_file_to_base64(file_path: str) -> str:
    """Read a file and return base64-encoded data URI."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    mime_types = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.webp': 'image/webp', '.mp4': 'video/mp4',
        '.webm': 'video/webm', '.mp3': 'audio/mpeg', '.wav': 'audio/wav',
    }
    mime = mime_types.get(suffix, 'application/octet-stream')

    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')

    return f"data:{mime};base64,{data}"


def queue_video(
    model: str,
    prompt: str,
    duration: str = "5s",
    aspect_ratio: Optional[str] = None,
    resolution: str = "720p",
    audio: Optional[bool] = None,
    negative_prompt: Optional[str] = None,
    image_path: Optional[str] = None,
    video_path: Optional[str] = None,
    audio_path: Optional[str] = None,
    image_url: Optional[str] = None,
    video_url: Optional[str] = None,
    audio_url: Optional[str] = None,
) -> VideoQueueResponse:
    """
    Queue a video for generation.
    Only sends fields that are explicitly provided.

    Note: aspect_ratio is only included if explicitly set.
    Some models (e.g., veo3.1-full-image-to-video) do NOT support aspect_ratio.
    """
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Encode files if paths provided
    if image_path and not image_url:
        image_url = encode_file_to_base64(image_path)
    if video_path and not video_url:
        video_url = encode_file_to_base64(video_path)
    if audio_path and not audio_url:
        audio_url = encode_file_to_base64(audio_path)

    # Build request - only include required and explicitly provided fields
    request_data = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
    }

    # aspect_ratio - only add if explicitly provided (some models don't support it)
    if aspect_ratio is not None:
        request_data["aspect_ratio"] = aspect_ratio

    # Optional fields - only add if explicitly set
    if audio is not None:
        request_data["audio"] = audio
    if negative_prompt:
        request_data["negative_prompt"] = negative_prompt
    if image_url:
        request_data["image_url"] = image_url
    if video_url:
        request_data["video_url"] = video_url
    if audio_url:
        request_data["audio_url"] = audio_url

    response = requests.post(
        VENICE_QUEUE_URL,
        headers=headers,
        json=request_data,
        timeout=60
    )

    # Better error handling
    if not response.ok:
        try:
            error_detail = response.json()
        except:
            error_detail = response.text
        raise RuntimeError(f"API Error {response.status_code}: {error_detail}")

    return VideoQueueResponse(**response.json())


def queue_text_to_video(
    prompt: str,
    model: str = "wan-2.5-preview-text-to-video",
    duration: str = "5s",
    resolution: str = "720p",
    aspect_ratio: str = "16:9",
    negative_prompt: Optional[str] = None,
) -> VideoQueueResponse:
    """Queue text-to-video generation."""
    return queue_video(
        model=model,
        prompt=prompt,
        duration=duration,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        negative_prompt=negative_prompt,
    )


def queue_image_to_video(
    prompt: str,
    image_path: str,
    model: str = "wan-2.5-preview-image-to-video",
    duration: str = "5s",
    resolution: str = "720p",
    aspect_ratio: Optional[str] = None,
    negative_prompt: Optional[str] = None,
) -> VideoQueueResponse:
    """Queue image-to-video generation."""
    return queue_video(
        model=model,
        prompt=prompt,
        duration=duration,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        image_path=image_path,
        negative_prompt=negative_prompt,
    )


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Queue a video for generation on Venice.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Text-to-video (default)
  python queue_video.py "A cat playing piano" --duration 5s

  # Image-to-video
  python queue_video.py "Animate this scene" --image /path/to/image.png

  # Custom model and settings
  python queue_video.py "Cinematic landscape" --model wan-2.5-preview-text-to-video --duration 10s --resolution 1080p --aspect-ratio 16:9
"""
    )

    parser.add_argument("prompt", help="Text prompt describing the video to generate")
    parser.add_argument("--model", "-m", default="wan-2.5-preview-text-to-video",
                       help="Model to use (default: wan-2.5-preview-text-to-video)")
    parser.add_argument("--duration", "-d", default="5s",
                       help="Video duration: 5s or 10s (default: 5s)")
    parser.add_argument("--resolution", "-r", default="720p",
                       help="Resolution: 480p, 720p, 1080p (default: 720p)")
    parser.add_argument("--aspect-ratio", "-a", default=None,
                       help="Aspect ratio e.g. 16:9, 9:16, 1:1 (optional, not all models support)")
    parser.add_argument("--negative-prompt", "-n", default=None,
                       help="Negative prompt - things to avoid")
    parser.add_argument("--image", "-i", default=None,
                       help="Path to input image for image-to-video")
    parser.add_argument("--video", "-v", default=None,
                       help="Path to input video for video-to-video")
    parser.add_argument("--audio", default=None,
                       help="Path to audio file to include")
    parser.add_argument("--with-audio", action="store_true",
                       help="Enable audio generation (if model supports)")
    parser.add_argument("--json", action="store_true",
                       help="Output result as JSON")

    args = parser.parse_args()

    # Check API key
    if not VENICE_API_KEY:
        print("Error: VENICE_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    try:
        result = queue_video(
            model=args.model,
            prompt=args.prompt,
            duration=args.duration,
            resolution=args.resolution,
            aspect_ratio=args.aspect_ratio,
            negative_prompt=args.negative_prompt,
            image_path=args.image,
            video_path=args.video,
            audio_path=args.audio,
            audio=True if args.with_audio else None,
        )

        if args.json:
            print(json.dumps({"model": result.model, "queue_id": result.queue_id}))
        else:
            print(f"✅ Video queued successfully!")
            print(f"   Model:    {result.model}")
            print(f"   Queue ID: {result.queue_id}")
            print(f"")
            print(f"To retrieve, run:")
            print(f"   python retrieve_video.py {result.model} {result.queue_id}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

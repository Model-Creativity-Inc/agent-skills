"""# Venice.ai Video Retrieve Skill
Retrieve a queued video by polling until complete.

Usage:
  python retrieve_video.py MODEL QUEUE_ID [options]

Examples:
  # Basic retrieval
  python retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id

  # Save to specific path
  python retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id --output /path/to/video.mp4
"""

import os
import sys
import time
import json
import base64
import argparse
import requests
from pathlib import Path
from typing import Optional, Union
from pydantic import BaseModel

VENICE_RETRIEVE_URL = "https://api.venice.ai/api/v1/video/retrieve"
VENICE_API_KEY = os.getenv("VENICE_API_KEY")
DEFAULT_OUTPUT_DIR = "/root/venice_videos"


class VideoRetrieveResponse(BaseModel):
    status: str = "unknown"
    video_url: Optional[str] = None
    video_data: Optional[bytes] = None
    error: Optional[str] = None
    progress: Optional[float] = None
    eta: Optional[int] = None


def retrieve_video(
    model: str,
    queue_id: str,
    delete_media_on_completion: bool = False
) -> VideoRetrieveResponse:
    """Single retrieve request - handles JSON or binary video response."""
    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }

    request_data = {
        "model": model,
        "queue_id": queue_id,
        "delete_media_on_completion": delete_media_on_completion
    }

    response = requests.post(
        VENICE_RETRIEVE_URL,
        headers=headers,
        json=request_data,
        timeout=120
    )

    if not response.ok:
        return VideoRetrieveResponse(
            status="error",
            error=f"HTTP {response.status_code}: {response.text[:200]}"
        )

    content_type = response.headers.get("Content-Type", "")

    # If response is video data (MP4), return as completed
    if "video" in content_type or b'ftyp' in response.content[:20]:
        return VideoRetrieveResponse(
            status="completed",
            video_data=response.content
        )

    # Try to parse as JSON
    if not response.text or response.text.strip() == "":
        return VideoRetrieveResponse(
            status="pending",
            error="Empty response"
        )

    try:
        data = response.json()
        return VideoRetrieveResponse(**data)
    except Exception as e:
        # Might be binary video without proper content-type
        if len(response.content) > 1000:  # Probably video data
            return VideoRetrieveResponse(
                status="completed",
                video_data=response.content
            )
        return VideoRetrieveResponse(
            status="error",
            error=f"Parse error: {e}"
        )


def poll_until_complete(
    model: str,
    queue_id: str,
    poll_interval: int = 5,
    max_wait: int = 600,
    delete_media_on_completion: bool = False,
    verbose: bool = True
) -> VideoRetrieveResponse:
    """Poll until video is complete or failed."""
    start_time = time.time()
    error_count = 0

    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            raise TimeoutError(f"Timed out after {max_wait}s")

        result = retrieve_video(model, queue_id, delete_media_on_completion)
        status = result.status.lower() if result.status else "unknown"

        if verbose:
            progress_str = f"{result.progress:.0f}%" if result.progress else "?"
            eta_str = f"ETA {result.eta}s" if result.eta else ""
            print(f"  [{elapsed:.0f}s] Status: {status} | Progress: {progress_str} {eta_str}")

        if status in ["completed", "complete"]:
            if verbose:
                print(f"  ✅ Video ready!")
            return result

        if status == "failed":
            raise RuntimeError(f"Generation failed: {result.error}")

        if status == "error":
            error_count += 1
            if error_count > 10:
                raise RuntimeError(f"Too many errors: {result.error}")
            if verbose:
                print(f"  ⚠️ Retrying...")
        else:
            error_count = 0

        time.sleep(poll_interval)


def save_video(
    video_url: Optional[str] = None,
    video_data: Optional[bytes] = None,
    output_path: Optional[str] = None,
    filename: Optional[str] = None
) -> str:
    """Save video from URL, base64, or raw bytes to disk."""
    if output_path:
        path = Path(output_path)
    elif filename:
        path = Path(DEFAULT_OUTPUT_DIR) / filename
    else:
        path = Path(DEFAULT_OUTPUT_DIR) / f"video_{int(time.time())}.mp4"

    path.parent.mkdir(parents=True, exist_ok=True)

    if video_data:
        # Direct binary data
        with open(path, "wb") as f:
            f.write(video_data)
    elif video_url:
        if video_url.startswith("data:"):
            # Base64 data URI
            header, encoded = video_url.split(",", 1)
            data = base64.b64decode(encoded)
            with open(path, "wb") as f:
                f.write(data)
        else:
            # URL download
            response = requests.get(video_url, timeout=120)
            response.raise_for_status()
            with open(path, "wb") as f:
                f.write(response.content)
    else:
        raise ValueError("No video_url or video_data provided")

    return str(path)


def retrieve_and_save(
    model: str,
    queue_id: str,
    output_path: Optional[str] = None,
    filename: Optional[str] = None,
    poll_interval: int = 5,
    max_wait: int = 600,
    verbose: bool = True
) -> str:
    """Poll until complete, then save to disk."""
    result = poll_until_complete(
        model=model,
        queue_id=queue_id,
        poll_interval=poll_interval,
        max_wait=max_wait,
        verbose=verbose
    )

    saved_path = save_video(
        video_url=result.video_url,
        video_data=result.video_data,
        output_path=output_path,
        filename=filename
    )

    if verbose:
        print(f"  💾 Saved to: {saved_path}")

    return saved_path


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Retrieve a queued video from Venice.ai",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Basic retrieval (saves to default location)
  python retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id

  # Save to specific path
  python retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id -o /path/to/video.mp4

  # Custom polling settings
  python retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id --interval 10 --max-wait 900

  # Quiet mode (no progress output)
  python retrieve_video.py wan-2.5-preview-text-to-video abc123-queue-id --quiet
"""
    )

    parser.add_argument("model", help="Model that was used for generation")
    parser.add_argument("queue_id", help="Queue ID returned from queue_video")
    parser.add_argument("--output", "-o", default=None,
                       help="Output path for the video file (default: /root/venice_videos/video_<timestamp>.mp4)")
    parser.add_argument("--interval", "-i", type=int, default=5,
                       help="Polling interval in seconds (default: 5)")
    parser.add_argument("--max-wait", "-w", type=int, default=600,
                       help="Maximum wait time in seconds (default: 600)")
    parser.add_argument("--delete-after", action="store_true",
                       help="Delete video from Venice servers after download")
    parser.add_argument("--quiet", "-q", action="store_true",
                       help="Suppress progress output")
    parser.add_argument("--json", action="store_true",
                       help="Output result as JSON")

    args = parser.parse_args()

    # Check API key
    if not VENICE_API_KEY:
        print("Error: VENICE_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    verbose = not args.quiet

    try:
        if verbose:
            print(f"🎬 Retrieving video...")
            print(f"   Model:    {args.model}")
            print(f"   Queue ID: {args.queue_id}")
            print(f"")

        saved_path = retrieve_and_save(
            model=args.model,
            queue_id=args.queue_id,
            output_path=args.output,
            poll_interval=args.interval,
            max_wait=args.max_wait,
            verbose=verbose
        )

        if args.json:
            print(json.dumps({"status": "completed", "path": saved_path}))
        elif verbose:
            print(f"")
            print(f"✅ Video saved to: {saved_path}")

    except TimeoutError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

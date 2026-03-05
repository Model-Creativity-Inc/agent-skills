"""Venice.ai Full Lifecycle Video Generation

Combines video queue and retrieve into a single operation with progress logging.
Optimized for Agent Zero environment - clear output, efficient polling, agent-friendly responses.

Usage:
    # CLI
    python generate_video.py "A cat playing piano" --model wan-2.5-preview-text-to-video --duration 5s

    # Python import
    from generate_video import generate_video
    result = generate_video(prompt="A cat playing piano", model="wan-2.5-preview-text-to-video")
"""

import os
import sys
import time
import argparse
import base64
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

# ============================================================================
# CONFIGURATION
# ============================================================================

VENICE_API_KEY = os.getenv("VENICE_API_KEY")
VENICE_QUEUE_URL = "https://api.venice.ai/api/v1/video/queue"
VENICE_RETRIEVE_URL = "https://api.venice.ai/api/v1/video/retrieve"
DEFAULT_OUTPUT_DIR = "/root/venice_videos"
DEFAULT_MODEL = "wan-2.5-preview-text-to-video"
PROGRESS_LOG_INTERVAL = 20  # seconds between progress logs
DEFAULT_POLL_INTERVAL = 5   # seconds between API polls
DEFAULT_MAX_WAIT = 900      # 15 minutes max wait


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class GenerationResult:
    """Result of a full video generation lifecycle."""
    success: bool
    video_path: Optional[str] = None
    queue_id: Optional[str] = None
    model: Optional[str] = None
    elapsed_seconds: float = 0.0
    error: Optional[str] = None

    # Timing statistics from API
    api_eta_seconds: Optional[int] = None
    api_progress: Optional[float] = None

    def __str__(self):
        if self.success:
            return f"SUCCESS: Video saved to {self.video_path} (took {self.elapsed_seconds:.1f}s)"
        return f"FAILED: {self.error}"


@dataclass 
class ProgressInfo:
    """Progress information for logging."""
    elapsed_seconds: float
    status: str
    api_progress: Optional[float] = None
    api_eta_seconds: Optional[int] = None
    poll_count: int = 0

    def format_progress_bar(self, width: int = 20) -> str:
        """Generate a text progress bar."""
        if self.api_progress is None:
            return "[" + "?" * width + "]"
        pct = min(100, max(0, self.api_progress))
        filled = int(width * pct / 100)
        return "[" + "=" * filled + "-" * (width - filled) + "]"

    def format_eta(self) -> str:
        """Format ETA as human-readable string."""
        if self.api_eta_seconds is None:
            return "ETA: unknown"
        if self.api_eta_seconds <= 0:
            return "ETA: completing..."
        mins, secs = divmod(self.api_eta_seconds, 60)
        if mins > 0:
            return f"ETA: {mins}m {secs}s"
        return f"ETA: {secs}s"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

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


def log_progress(info: ProgressInfo) -> None:
    """Log progress in agent-friendly format."""
    progress_str = f"{info.api_progress:.0f}%" if info.api_progress is not None else "---%"
    bar = info.format_progress_bar()
    eta = info.format_eta()

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"[{timestamp}] PROGRESS: {info.elapsed_seconds:>6.0f}s elapsed | "
          f"{bar} {progress_str:>4} | {eta} | status: {info.status}")
    sys.stdout.flush()


def log_event(event_type: str, message: str) -> None:
    """Log an event in agent-friendly format."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {event_type}: {message}")
    sys.stdout.flush()


# ============================================================================
# CORE API FUNCTIONS
# ============================================================================

def queue_video(
    model: str,
    prompt: str,
    duration: str = "5s",
    aspect_ratio: Optional[str] = None,
    resolution: str = "720p",
    audio: Optional[bool] = None,
    negative_prompt: Optional[str] = None,
    image_path: Optional[str] = None,
    image_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Queue a video for generation. Returns dict with model and queue_id."""

    if not VENICE_API_KEY:
        raise ValueError("VENICE_API_KEY environment variable not set")

    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }

    # Handle image input
    if image_path and not image_url:
        image_url = encode_file_to_base64(image_path)

    # Build request with only provided fields
    request_data = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
    }

    if aspect_ratio is not None:
        request_data["aspect_ratio"] = aspect_ratio
    if audio is not None:
        request_data["audio"] = audio
    if negative_prompt:
        request_data["negative_prompt"] = negative_prompt
    if image_url:
        request_data["image_url"] = image_url

    response = requests.post(
        VENICE_QUEUE_URL,
        headers=headers,
        json=request_data,
        timeout=60
    )

    if not response.ok:
        try:
            error_detail = response.json()
        except:
            error_detail = response.text
        raise RuntimeError(f"Queue API Error {response.status_code}: {error_detail}")

    return response.json()


def retrieve_video_status(
    model: str,
    queue_id: str,
    delete_on_completion: bool = False
) -> Dict[str, Any]:
    """Single retrieve request. Returns status dict or video bytes."""

    headers = {
        "Authorization": f"Bearer {VENICE_API_KEY}",
        "Content-Type": "application/json"
    }

    request_data = {
        "model": model,
        "queue_id": queue_id,
        "delete_media_on_completion": delete_on_completion
    }

    response = requests.post(
        VENICE_RETRIEVE_URL,
        headers=headers,
        json=request_data,
        timeout=120
    )

    if not response.ok:
        return {
            "status": "error",
            "error": f"HTTP {response.status_code}: {response.text[:200]}"
        }

    content_type = response.headers.get("Content-Type", "")

    # Check if response is video data (binary)
    if "video" in content_type or response.content[:4] == b'\x00\x00\x00' or b'ftyp' in response.content[:20]:
        return {
            "status": "completed",
            "video_data": response.content
        }

    # Try to parse as JSON
    try:
        data = response.json()
        # Normalize status to lowercase
        if "status" in data:
            data["status"] = data["status"].lower()
        return data
    except:
        # Might be binary video without proper content-type
        if len(response.content) > 1000:
            return {
                "status": "completed",
                "video_data": response.content
            }
        return {
            "status": "error",
            "error": "Failed to parse response"
        }


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_video(
    prompt: str,
    model: str = DEFAULT_MODEL,
    duration: str = "5s",
    aspect_ratio: Optional[str] = "16:9",
    resolution: str = "720p",
    audio: Optional[bool] = None,
    negative_prompt: Optional[str] = None,
    image_path: Optional[str] = None,
    image_url: Optional[str] = None,
    output_path: Optional[str] = None,
    output_dir: str = DEFAULT_OUTPUT_DIR,
    max_wait: int = DEFAULT_MAX_WAIT,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    progress_interval: int = PROGRESS_LOG_INTERVAL,
    verbose: bool = True,
    delete_on_completion: bool = False,
) -> GenerationResult:
    """
    Full lifecycle video generation: queue, poll with progress, retrieve, save.

    Args:
        prompt: Text description of the video to generate
        model: Venice model ID (default: wan-2.5-preview-text-to-video)
        duration: Video duration (e.g., "5s", "10s")
        aspect_ratio: Aspect ratio (e.g., "16:9", "9:16", "1:1") - omit for some models
        resolution: Video resolution (e.g., "720p", "1080p")
        audio: Enable audio generation (model-dependent)
        negative_prompt: What to avoid in generation
        image_path: Local path to input image (for image-to-video)
        image_url: URL/base64 of input image (for image-to-video)
        output_path: Full path for output video (auto-generated if not provided)
        output_dir: Directory for output (default: /root/venice_videos)
        max_wait: Maximum seconds to wait for completion (default: 900)
        poll_interval: Seconds between API polls (default: 5)
        progress_interval: Seconds between progress logs (default: 20)
        verbose: Print progress logs (default: True)
        delete_on_completion: Delete from Venice servers after download

    Returns:
        GenerationResult with success status, video path, timing info
    """

    start_time = time.time()
    result = GenerationResult(success=False, model=model)

    # ========== PHASE 1: QUEUE ==========
    if verbose:
        log_event("START", f"Queueing video generation with model: {model}")
        log_event("CONFIG", f"duration={duration}, resolution={resolution}, aspect_ratio={aspect_ratio}")

    try:
        queue_response = queue_video(
            model=model,
            prompt=prompt,
            duration=duration,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            audio=audio,
            negative_prompt=negative_prompt,
            image_path=image_path,
            image_url=image_url,
        )

        queue_id = queue_response.get("queue_id")
        if not queue_id:
            result.error = f"No queue_id in response: {queue_response}"
            return result

        result.queue_id = queue_id

        if verbose:
            log_event("QUEUED", f"queue_id={queue_id}")

    except Exception as e:
        result.error = f"Queue failed: {e}"
        result.elapsed_seconds = time.time() - start_time
        if verbose:
            log_event("ERROR", result.error)
        return result

    # ========== PHASE 2: POLL WITH PROGRESS ==========
    poll_count = 0
    error_count = 0
    last_progress_log = 0

    if verbose:
        log_event("POLLING", f"Waiting for video completion (max {max_wait}s, logging every {progress_interval}s)")

    while True:
        elapsed = time.time() - start_time

        # Check timeout
        if elapsed > max_wait:
            result.error = f"Timeout after {max_wait}s"
            result.elapsed_seconds = elapsed
            if verbose:
                log_event("TIMEOUT", result.error)
            return result

        # Poll API
        poll_count += 1
        status_response = retrieve_video_status(model, queue_id, delete_on_completion)

        status = status_response.get("status", "unknown").lower()
        api_progress = status_response.get("progress")
        api_eta = status_response.get("eta")

        # Update result with latest API timing info
        result.api_progress = api_progress
        result.api_eta_seconds = api_eta

        # Log progress at intervals
        if verbose and (elapsed - last_progress_log >= progress_interval):
            info = ProgressInfo(
                elapsed_seconds=elapsed,
                status=status,
                api_progress=api_progress,
                api_eta_seconds=api_eta,
                poll_count=poll_count
            )
            log_progress(info)
            last_progress_log = elapsed

        # Check completion
        if status in ["completed", "complete"]:
            video_data = status_response.get("video_data")
            video_url = status_response.get("video_url")

            if video_data or video_url:
                # Save video
                if output_path:
                    save_path = Path(output_path)
                else:
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = Path(output_dir) / f"video_{timestamp}_{queue_id[:8]}.mp4"

                save_path.parent.mkdir(parents=True, exist_ok=True)

                if video_data:
                    with open(save_path, "wb") as f:
                        f.write(video_data)
                elif video_url:
                    if video_url.startswith("data:"):
                        header, encoded = video_url.split(",", 1)
                        with open(save_path, "wb") as f:
                            f.write(base64.b64decode(encoded))
                    else:
                        dl_response = requests.get(video_url, timeout=120)
                        dl_response.raise_for_status()
                        with open(save_path, "wb") as f:
                            f.write(dl_response.content)

                result.success = True
                result.video_path = str(save_path)
                result.elapsed_seconds = time.time() - start_time

                if verbose:
                    log_event("COMPLETE", f"Video saved to {save_path}")
                    log_event("TIMING", f"Total time: {result.elapsed_seconds:.1f}s")

                return result
            else:
                result.error = "Completed but no video data received"
                result.elapsed_seconds = time.time() - start_time
                return result

        # Check failure
        if status == "failed":
            result.error = f"Generation failed: {status_response.get('error', 'unknown')}"
            result.elapsed_seconds = time.time() - start_time
            if verbose:
                log_event("FAILED", result.error)
            return result

        # Handle transient errors
        if status == "error":
            error_count += 1
            if error_count > 10:
                result.error = f"Too many API errors: {status_response.get('error')}"
                result.elapsed_seconds = time.time() - start_time
                return result
            if verbose and error_count == 1:
                log_event("RETRY", f"API error, retrying... ({status_response.get('error', '')})") 
        else:
            error_count = 0

        # Wait before next poll
        time.sleep(poll_interval)


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Venice.ai Full Lifecycle Video Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic text-to-video
  python generate_video.py "A cat playing piano"

  # With specific model and duration  
  python generate_video.py "Ocean waves at sunset" --model kling-2.6-pro-text-to-video --duration 10s

  # Image-to-video
  python generate_video.py "Make this image come alive" --image /path/to/image.png --model wan-2.5-preview-image-to-video

  # Custom output path
  python generate_video.py "Dancing robot" --output /root/my_video.mp4
"""
    )

    parser.add_argument("prompt", help="Text description of the video to generate")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, 
                        help=f"Venice model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--duration", "-d", default="5s",
                        help="Video duration, e.g., 5s, 10s (default: 5s)")
    parser.add_argument("--resolution", "-r", default="720p",
                        help="Video resolution (default: 720p)")
    parser.add_argument("--aspect-ratio", "-a", default="16:9",
                        help="Aspect ratio, e.g., 16:9, 9:16, 1:1 (default: 16:9)")
    parser.add_argument("--audio", action="store_true", default=None,
                        help="Enable audio generation")
    parser.add_argument("--no-audio", action="store_true",
                        help="Disable audio generation")
    parser.add_argument("--negative-prompt", "-n",
                        help="What to avoid in generation")
    parser.add_argument("--image", "-i",
                        help="Input image path (for image-to-video models)")
    parser.add_argument("--output", "-o",
                        help="Output video file path")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--max-wait", type=int, default=DEFAULT_MAX_WAIT,
                        help=f"Maximum wait time in seconds (default: {DEFAULT_MAX_WAIT})")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress progress output")

    args = parser.parse_args()

    # Handle audio flag
    audio = None
    if args.audio:
        audio = True
    elif args.no_audio:
        audio = False

    # Run generation
    result = generate_video(
        prompt=args.prompt,
        model=args.model,
        duration=args.duration,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        audio=audio,
        negative_prompt=args.negative_prompt,
        image_path=args.image,
        output_path=args.output,
        output_dir=args.output_dir,
        max_wait=args.max_wait,
        verbose=not args.quiet,
    )

    # Final output for agent parsing
    print("")
    print("=" * 70)
    if result.success:
        print(f"RESULT: SUCCESS")
        print(f"VIDEO_PATH: {result.video_path}")
        print(f"ELAPSED_SECONDS: {result.elapsed_seconds:.1f}")
        print(f"QUEUE_ID: {result.queue_id}")
        print(f"MODEL: {result.model}")
    else:
        print(f"RESULT: FAILED")
        print(f"ERROR: {result.error}")
        print(f"ELAPSED_SECONDS: {result.elapsed_seconds:.1f}")
    print("=" * 70)

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())

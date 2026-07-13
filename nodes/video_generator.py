"""
LangGraph LocalAI TV Pipeline — Video Generator Node
Generates raw video segments from approved headlines (mock + real API hook).
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Optional


def generate_video_script(headline: dict) -> dict:
    """
    Generate a video script from a headline.

    Args:
        headline: Headline dict with title, summary, source.

    Returns:
        Script dict with intro, body, outro, and metadata.
    """
    title = headline.get("title", "Breaking News")
    summary = headline.get("summary", "")
    source = headline.get("source", "Unknown")

    script = {
        "headline_id": hashlib.md5(title.encode()).hexdigest()[:8],
        "intro": f"Breaking news from {source}. {title}.",
        "body": summary if summary else f"More details emerging about {title}. "
                "Our team is following this developing story.",
        "outro": f"That was the latest on {title}. Stay tuned for more updates.",
        "duration_estimate_seconds": max(15, len(summary) // 10),
        "generated_at": datetime.now().isoformat(),
    }

    return script


def generate_raw_video(
    script: dict,
    output_dir: str = "./output/videos",
    use_api: bool = False,
    api_key: Optional[str] = None,
) -> dict:
    """
    Generate a raw video segment from a script.
    Uses mock generation by default; set use_api=True for real API.

    Args:
        script: Script dict from generate_video_script.
        output_dir: Directory to save video metadata.
        use_api: Whether to use a real video generation API.
        api_key: API key for video generation service.

    Returns:
        Video metadata dict with path, duration, status.
    """
    os.makedirs(output_dir, exist_ok=True)

    video_id = script["headline_id"]
    video_metadata = {
        "video_id": video_id,
        "script": script,
        "status": "generated",
        "output_path": f"{output_dir}/{video_id}_raw.mp4",
        "duration_seconds": script["duration_estimate_seconds"],
        "generated_at": datetime.now().isoformat(),
        "method": "api" if use_api else "mock",
    }

    if use_api and api_key:
        # Hook for real video generation API (e.g., Synthesia, D-ID, HeyGen)
        # Replace this with actual API integration
        video_metadata["api_response"] = {
            "status": "pending",
            "message": "Real API integration — replace with your provider",
        }
    else:
        # Mock: create a metadata file simulating video generation
        meta_path = f"{output_dir}/{video_id}_meta.json"
        with open(meta_path, "w") as f:
            json.dump(video_metadata, f, indent=2)
        video_metadata["meta_path"] = meta_path

    return video_metadata


def batch_generate_videos(
    headlines: list[dict],
    output_dir: str = "./output/videos",
) -> list[dict]:
    """
    Generate raw video segments for a batch of approved headlines.

    Args:
        headlines: List of approved headline dicts.
        output_dir: Directory for video output.

    Returns:
        List of video metadata dicts.
    """
    videos = []
    api_key = os.getenv("VIDEO_API_KEY")
    use_api = bool(api_key)

    for headline in headlines:
        try:
            script = generate_video_script(headline)
            video = generate_raw_video(
                script, output_dir=output_dir,
                use_api=use_api, api_key=api_key,
            )
            videos.append(video)
            print(f"  ✓ Generated video for: {headline['title'][:50]}...")
        except Exception as e:
            print(f"  ✗ Failed to generate video: {e}")
            videos.append({
                "headline": headline["title"],
                "status": "failed",
                "error": str(e),
            })

    return videos

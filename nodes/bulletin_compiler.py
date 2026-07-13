"""
LangGraph LocalAI TV Pipeline — Bulletin Compiler Node
Compiles approved video segments into a final news bulletin.
"""

import json
import os
from datetime import datetime
from typing import Optional


def compile_bulletin(
    videos: list[dict],
    bulletin_title: Optional[str] = None,
    output_dir: str = "./output/bulletins",
) -> dict:
    """
    Compile approved video segments into a final news bulletin.

    Args:
        videos: List of video metadata dicts (only 'generated' status).
        bulletin_title: Optional title for the bulletin.
        output_dir: Directory to save bulletin output.

    Returns:
        Bulletin metadata dict with segments, duration, and output path.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Filter to only successfully generated videos
    approved = [v for v in videos if v.get("status") == "generated"]

    if not approved:
        return {
            "status": "empty",
            "message": "No approved video segments to compile.",
            "generated_at": datetime.now().isoformat(),
        }

    # Build bulletin structure
    date_str = datetime.now().strftime("%Y-%m-%d")
    title = bulletin_title or f"LocalAI TV News Bulletin — {date_str}"

    total_duration = sum(v.get("duration_seconds", 0) for v in approved)

    bulletin = {
        "title": title,
        "date": date_str,
        "segment_count": len(approved),
        "total_duration_seconds": total_duration,
        "total_duration_display": f"{total_duration // 60}m {total_duration % 60}s",
        "segments": [],
        "status": "compiled",
        "generated_at": datetime.now().isoformat(),
    }

    # Add intro
    bulletin["intro"] = (
        f"Good evening. Welcome to LocalAI TV News. "
        f"Tonight we have {len(approved)} stories for you. "
        f"Here are today's top headlines."
    )

    # Add each segment
    for i, video in enumerate(approved, 1):
        script = video.get("script", {})
        segment = {
            "position": i,
            "video_id": video.get("video_id", f"seg_{i}"),
            "headline": script.get("intro", ""),
            "body": script.get("body", ""),
            "duration_seconds": video.get("duration_seconds", 0),
            "source_video": video.get("output_path", ""),
        }
        bulletin["segments"].append(segment)

    # Add outro
    bulletin["outro"] = (
        f"That's all for tonight's bulletin. "
        f"We covered {len(approved)} stories in "
        f"{bulletin['total_duration_display']}. "
        f"Thank you for watching LocalAI TV News."
    )

    # Save bulletin
    output_path = f"{output_dir}/bulletin_{date_str}.json"
    with open(output_path, "w") as f:
        json.dump(bulletin, f, indent=2)

    bulletin["output_path"] = output_path

    return bulletin


def format_bulletin_text(bulletin: dict) -> str:
    """
    Format a bulletin as readable text output.

    Args:
        bulletin: Bulletin metadata dict.

    Returns:
        Formatted text string.
    """
    if bulletin.get("status") == "empty":
        return "⚠ No bulletin generated — no approved segments."

    lines = [
        f"{'=' * 60}",
        f"📺  {bulletin['title']}",
        f"{'=' * 60}",
        "",
        f"🎙  {bulletin.get('intro', '')}",
        "",
    ]

    for seg in bulletin.get("segments", []):
        lines.extend([
            f"--- Segment {seg['position']} ---",
            f"📰  {seg['headline']}",
            f"    {seg['body']}",
            f"    ⏱  {seg['duration_seconds']}s",
            "",
        ])

    lines.extend([
        f"🎬  {bulletin.get('outro', '')}",
        "",
        f"📊  Total: {bulletin['segment_count']} segments, "
        f"{bulletin['total_duration_display']}",
        f"{'=' * 60}",
    ])

    return "\n".join(lines)

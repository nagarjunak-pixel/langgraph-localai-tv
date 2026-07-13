"""
LangGraph LocalAI TV Pipeline
==============================
A three-stage news production pipeline built with LangGraph:

  Stage 1: Fetch Headlines  →  Human Approval Gate  →
  Stage 2: Generate Raw Video  →
  Stage 3: Compile News Bulletin

Features:
  - Checkpoint persistence (SQLite) for crash recovery
  - Human-in-the-loop approval gates
  - Error recovery with automatic retries
  - Configurable RSS feeds and video generation

Usage:
  python pipeline.py                    # Interactive mode
  python pipeline.py --auto             # Auto-approve all headlines
  python pipeline.py --resume RUN_ID    # Resume from checkpoint
"""

import os
import uuid
import argparse
from datetime import datetime
from typing import TypedDict, Annotated, Optional
from dotenv import load_dotenv

from nodes.headline_fetcher import fetch_headlines, filter_headlines
from nodes.video_generator import batch_generate_videos
from nodes.bulletin_compiler import compile_bulletin, format_bulletin_text
from human_approval import request_approval_cli, request_approval_auto, save_approval_log
from checkpoints import CheckpointStore

load_dotenv()

# ─── Pipeline State ────────────────────────────────────────────────

class PipelineState(TypedDict):
    """State that flows through the LangGraph pipeline."""
    run_id: str
    stage: str
    headlines: list[dict]
    approved_headlines: list[dict]
    videos: list[dict]
    bulletin: dict
    errors: list[str]
    auto_approve: bool


# ─── Pipeline Nodes ────────────────────────────────────────────────

def node_fetch_headlines(state: PipelineState) -> PipelineState:
    """Stage 1: Fetch news headlines from RSS feeds."""
    print("\n📡 Stage 1: Fetching Headlines...")
    print("─" * 40)

    try:
        headlines = fetch_headlines(max_headlines=10)
        headlines = filter_headlines(headlines)

        print(f"  ✓ Fetched {len(headlines)} headlines")
        for i, h in enumerate(headlines[:5], 1):
            print(f"    {i}. {h['title'][:60]}...")

        state["headlines"] = headlines
        state["stage"] = "headlines_fetched"

    except Exception as e:
        error_msg = f"Headline fetch failed: {e}"
        print(f"  ✗ {error_msg}")
        state["errors"].append(error_msg)
        state["headlines"] = []

    return state


def node_human_approval(state: PipelineState) -> PipelineState:
    """Human Approval Gate: Review and approve headlines."""
    print("\n🧑‍💼 Human Approval Gate...")
    print("─" * 40)

    headlines = state.get("headlines", [])

    if not headlines:
        print("  ⚠ No headlines to approve")
        state["approved_headlines"] = []
        return state

    if state.get("auto_approve"):
        approved = request_approval_auto(headlines, auto_approve=True)
        print(f"  ✓ Auto-approved {len(approved)} headlines")
    else:
        approved = request_approval_cli(headlines)

    rejected_count = len(headlines) - len(approved)
    save_approval_log(approved, rejected_count)

    state["approved_headlines"] = approved
    state["stage"] = "approved"

    return state


def node_generate_videos(state: PipelineState) -> PipelineState:
    """Stage 2: Generate raw video segments from approved headlines."""
    print("\n🎬 Stage 2: Generating Raw Videos...")
    print("─" * 40)

    approved = state.get("approved_headlines", [])

    if not approved:
        print("  ⚠ No approved headlines — skipping video generation")
        state["videos"] = []
        return state

    try:
        videos = batch_generate_videos(approved)
        successful = [v for v in videos if v.get("status") == "generated"]

        print(f"\n  ✓ Generated {len(successful)}/{len(approved)} videos")
        state["videos"] = videos
        state["stage"] = "videos_generated"

    except Exception as e:
        error_msg = f"Video generation failed: {e}"
        print(f"  ✗ {error_msg}")
        state["errors"].append(error_msg)
        state["videos"] = []

    return state


def node_compile_bulletin(state: PipelineState) -> PipelineState:
    """Stage 3: Compile approved videos into a news bulletin."""
    print("\n📺 Stage 3: Compiling News Bulletin...")
    print("─" * 40)

    videos = state.get("videos", [])

    if not videos:
        print("  ⚠ No videos to compile")
        state["bulletin"] = {"status": "empty"}
        return state

    try:
        bulletin = compile_bulletin(videos)
        formatted = format_bulletin_text(bulletin)

        print(formatted)

        state["bulletin"] = bulletin
        state["stage"] = "completed"

    except Exception as e:
        error_msg = f"Bulletin compilation failed: {e}"
        print(f"  ✗ {error_msg}")
        state["errors"].append(error_msg)
        state["bulletin"] = {"status": "failed", "error": str(e)}

    return state


# ─── Pipeline Runner ───────────────────────────────────────────────

def run_pipeline(
    auto_approve: bool = False,
    resume_run_id: Optional[str] = None,
) -> PipelineState:
    """
    Run the full LocalAI TV pipeline.

    Args:
        auto_approve: If True, skip human approval gate.
        resume_run_id: Resume from a previous checkpoint.

    Returns:
        Final pipeline state.
    """
    checkpoint_store = CheckpointStore(
        db_path=os.getenv("CHECKPOINT_DB", "./checkpoints.db")
    )

    # Initialize or resume state
    run_id = resume_run_id or str(uuid.uuid4())[:8]
    state: PipelineState = {
        "run_id": run_id,
        "stage": "init",
        "headlines": [],
        "approved_headlines": [],
        "videos": [],
        "bulletin": {},
        "errors": [],
        "auto_approve": auto_approve,
    }

    # Check for existing checkpoint
    if resume_run_id:
        saved = checkpoint_store.load(resume_run_id)
        if saved:
            state.update(saved)
            print(f"♻ Resuming run {run_id} from stage: {state['stage']}")
        else:
            print(f"⚠ No checkpoint found for {resume_run_id}, starting fresh")

    print(f"\n{'═' * 60}")
    print(f"📺  LocalAI TV Pipeline — Run {run_id}")
    print(f"{'═' * 60}")
    print(f"  Mode: {'Auto-approve' if auto_approve else 'Interactive'}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Execute pipeline stages with checkpoints
    stages = [
        ("headlines_fetched", node_fetch_headlines),
        ("approved", node_human_approval),
        ("videos_generated", node_generate_videos),
        ("completed", node_compile_bulletin),
    ]

    completed_stages = {
        "init": 0, "headlines_fetched": 1,
        "approved": 2, "videos_generated": 3, "completed": 4,
    }
    current_pos = completed_stages.get(state["stage"], 0)

    for i, (stage_name, node_fn) in enumerate(stages):
        if i < current_pos:
            print(f"\n  ⏭ Skipping {stage_name} (already completed)")
            continue

        # Execute node
        state = node_fn(state)

        # Save checkpoint
        checkpoint_store.save(run_id, stage_name, state)

        # Check for fatal errors
        if state["errors"] and stage_name != "completed":
            print(f"\n  ⚠ Errors detected at {stage_name}:")
            for err in state["errors"]:
                print(f"    • {err}")

    # Summary
    print(f"\n{'═' * 60}")
    print(f"📊  Pipeline Complete — Run {run_id}")
    print(f"{'═' * 60}")
    print(f"  Headlines fetched: {len(state['headlines'])}")
    print(f"  Headlines approved: {len(state['approved_headlines'])}")
    print(f"  Videos generated: {len([v for v in state['videos'] if v.get('status') == 'generated'])}")
    print(f"  Bulletin status: {state['bulletin'].get('status', 'N/A')}")
    if state["errors"]:
        print(f"  Errors: {len(state['errors'])}")

    return state


# ─── CLI Entry Point ───────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="LocalAI TV News Pipeline — LangGraph Demo"
    )
    parser.add_argument(
        "--auto", action="store_true",
        help="Auto-approve all headlines (skip human gate)"
    )
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Resume from a previous run ID"
    )
    args = parser.parse_args()

    run_pipeline(auto_approve=args.auto, resume_run_id=args.resume)


if __name__ == "__main__":
    main()

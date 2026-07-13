"""
LangGraph LocalAI TV Pipeline — Human Approval Gate
Implements human-in-the-loop approval for headlines before video generation.
Supports CLI interactive mode and webhook mode.
"""

import json
import os
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

console = Console()


def request_approval_cli(headlines: list[dict]) -> list[dict]:
    """
    Interactive CLI approval gate — presents headlines and asks for approval.

    Args:
        headlines: List of headline dicts to approve.

    Returns:
        List of approved headline dicts.
    """
    if not headlines:
        console.print("[yellow]⚠ No headlines to approve.[/yellow]")
        return []

    console.print("\n[bold cyan]═══ HUMAN APPROVAL GATE ═══[/bold cyan]")
    console.print(f"[dim]{len(headlines)} headlines pending review[/dim]\n")

    # Display headlines in a table
    table = Table(title="Headlines for Approval", show_lines=True)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Title", style="white", max_width=50)
    table.add_column("Source", style="green", max_width=20)
    table.add_column("Published", style="dim", max_width=20)

    for i, h in enumerate(headlines, 1):
        table.add_row(
            str(i),
            h.get("title", "Untitled")[:50],
            h.get("source", "Unknown")[:20],
            h.get("published", "")[:20],
        )

    console.print(table)

    # Ask for approval
    approved = []
    for i, h in enumerate(headlines, 1):
        title = h.get("title", "Untitled")[:60]
        if Confirm.ask(f"\n  [cyan]#{i}[/cyan] Approve [bold]{title}[/bold]?"):
            h["approved"] = True
            h["approved_at"] = datetime.now().isoformat()
            approved.append(h)
            console.print(f"    [green]✓ Approved[/green]")
        else:
            console.print(f"    [red]✗ Rejected[/red]")

    console.print(
        f"\n[bold green]✓ {len(approved)}/{len(headlines)} "
        f"headlines approved[/bold green]\n"
    )

    return approved


def request_approval_auto(
    headlines: list[dict],
    auto_approve: bool = True,
) -> list[dict]:
    """
    Auto-approval mode for CI/CD or testing.

    Args:
        headlines: List of headline dicts.
        auto_approve: If True, approves all headlines automatically.

    Returns:
        List of approved headline dicts.
    """
    if auto_approve:
        for h in headlines:
            h["approved"] = True
            h["approved_at"] = datetime.now().isoformat()
            h["approved_by"] = "auto"
        return headlines

    return []


def save_approval_log(
    approved: list[dict],
    rejected_count: int,
    output_dir: str = "./output/logs",
) -> str:
    """
    Save approval decisions to a log file.

    Args:
        approved: List of approved headlines.
        rejected_count: Number of rejected headlines.
        output_dir: Directory for log files.

    Returns:
        Path to the log file.
    """
    os.makedirs(output_dir, exist_ok=True)

    log = {
        "timestamp": datetime.now().isoformat(),
        "total_reviewed": len(approved) + rejected_count,
        "approved_count": len(approved),
        "rejected_count": rejected_count,
        "approved_headlines": [
            {"title": h["title"], "approved_at": h.get("approved_at")}
            for h in approved
        ],
    }

    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"{output_dir}/approval_{date_str}.json"

    with open(log_path, "w") as f:
        json.dump(log, f, indent=2)

    return log_path

"""
Decision reviewer module for reviewing and providing feedback on proxy decisions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import questionary
from rich.console import Console
from rich.table import Table

from cinder_cli.database import DecisionDatabase

console = Console()


class DecisionReviewer:
    """Manages decision review workflow."""

    def __init__(self, db_path: Path):
        self.db = DecisionDatabase(db_path)

    def review_pending(self) -> None:
        """Review pending decisions."""
        decisions = self.db.list_decisions(limit=100)
        unreviewed = [d for d in decisions if not d["reviewed"]]

        if not unreviewed:
            console.print("[green]没有待审查的决策[/green]")
            return

        console.print(f"\n[bold cyan]待审查决策: {len(unreviewed)}[/bold cyan]\n")

        for decision in unreviewed[:10]:
            self._review_single(decision)

    def review_specific(self, decision_id: int) -> None:
        """Review a specific decision."""
        decision = self.db.get_decision(decision_id)

        if not decision:
            console.print(f"[red]决策 {decision_id} 不存在[/red]")
            return

        self._review_single(decision)

    def _review_single(self, decision: dict[str, Any]) -> None:
        """Review a single decision."""
        console.print(f"\n[bold]决策 #{decision['id']}[/bold]")
        console.print(f"时间: {decision['timestamp']}")
        console.print(f"置信度: {decision['confidence']:.2f}")
        console.print(f"需要人工确认: {decision['requires_human']}")

        console.print("\n[bold]上下文:[/bold]")
        console.print(str(decision["context"])[:200])

        console.print("\n[bold]应用的规则:[/bold]")
        rules = decision["soul_rules"]
        if isinstance(rules, dict) and "applied" in rules:
            for rule in rules["applied"]:
                console.print(f"  • {rule}")

        console.print("\n[bold]决策结果:[/bold]")
        console.print(str(decision["decision"])[:200])

        action = questionary.select(
            "审查结果:",
            choices=[
                "正确 - 决策符合预期",
                "错误 - 决策不符合预期",
                "跳过 - 稍后再审查",
            ],
        ).ask()

        if not action or "跳过" in action:
            return

        if "正确" in action:
            self.db.update_review(
                decision["id"],
                reviewed=True,
                review_result="correct",
            )
            console.print("[green]✓ 已标记为正确[/green]")

        elif "错误" in action:
            reason = questionary.text(
                "请说明错误原因:"
            ).ask()

            self.db.update_review(
                decision["id"],
                reviewed=True,
                review_result="incorrect",
                review_reason=reason,
            )
            console.print("[yellow]✓ 已标记为错误并记录原因[/yellow]")

    def show_statistics(self) -> None:
        """Show decision review statistics."""
        stats = self.db.get_statistics()

        console.print("\n[bold cyan]决策审查统计[/bold cyan]\n")

        table = Table()
        table.add_column("指标", style="cyan")
        table.add_column("值", style="magenta")

        table.add_row("总决策数", str(stats["total"]))
        table.add_row("平均置信度", f"{stats['avg_confidence']:.2f}")
        table.add_row("需要人工确认", str(stats["requires_human_count"]))
        table.add_row("已审查", str(stats["reviewed_count"]))

        if stats["total"] > 0:
            review_rate = stats["reviewed_count"] / stats["total"] * 100
            table.add_row("审查率", f"{review_rate:.1f}%")

        console.print(table)

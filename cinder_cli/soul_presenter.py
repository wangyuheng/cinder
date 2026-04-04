"""
Soul presenter module for displaying and confirming soul profiles.
"""

from __future__ import annotations

from pathlib import Path

import questionary
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class SoulPresenter:
    """Displays and manages soul profile confirmation."""

    def __init__(self, soul_path: str):
        self.soul_path = Path(soul_path).expanduser().resolve()
        self.meta_path = self.soul_path.with_suffix(".meta.yaml")
        self.soul_content = ""
        self.meta_content: dict = {}

    def present_and_confirm(self, skip_confirmation: bool = False) -> bool:
        """Present soul profile and get user confirmation."""
        self._load_soul()

        if skip_confirmation:
            return True

        self._display_summary()

        while True:
            action = questionary.select(
                "请选择操作：",
                choices=[
                    "确认 - 画像准确，继续",
                    "查看详情 - 查看完整画像",
                    "查看维度说明 - 了解各维度含义",
                    "调整 - 重新回答问题或调整分数",
                    "取消 - 放弃当前画像",
                ],
            ).ask()

            if action is None or "取消" in action:
                return False
            elif "确认" in action:
                self._mark_confirmed()
                console.print("[green]✓ Soul 画像已确认[/green]")
                return True
            elif "查看详情" in action:
                self._display_full()
            elif "查看维度说明" in action:
                self._explain_dimensions()
            elif "调整" in action:
                if self._adjust():
                    self._load_soul()
                    self._display_summary()

        return False

    def _load_soul(self) -> None:
        """Load soul.md and soul.meta.yaml."""
        if self.soul_path.exists():
            with open(self.soul_path, encoding="utf-8") as f:
                self.soul_content = f.read()

        if self.meta_path.exists():
            with open(self.meta_path, encoding="utf-8") as f:
                self.meta_content = yaml.safe_load(f) or {}

    def _display_summary(self) -> None:
        """Display soul profile summary."""
        console.print("\n[bold cyan]═══ Soul 画像摘要 ═══[/bold cyan]\n")

        if "core_traits" in self.meta_content:
            console.print("[bold]核心特质:[/bold]")
            for trait in self.meta_content["core_traits"]:
                console.print(f"  • {trait}")
            console.print()

        if "decision_profile" in self.meta_content:
            console.print("[bold]决策画像:[/bold]")
            profile = self.meta_content["decision_profile"]
            for key, value in profile.items():
                label = key.replace("_", " ").title()
                console.print(f"  • {label}: {value}")
            console.print()

        if "traits" in self.meta_content:
            table = Table(title="Trait Vector")
            table.add_column("特质", style="cyan")
            table.add_column("分数", style="magenta")

            trait_labels = {
                "exploration": "探索倾向",
                "structure": "结构需求",
                "risk_tolerance": "风险偏好",
                "evidence_orientation": "证据导向",
                "relationship_orientation": "关系导向",
                "action_bias": "行动偏好",
                "social_energy": "社交能量",
                "meaning_drive": "意义驱动",
                "discipline_drive": "纪律驱动",
                "adaptability": "适应弹性",
                "emotional_reactivity": "情绪反应强度",
                "recovery_speed": "情绪恢复速度",
                "reassurance_need": "外部确认需求",
            }

            for trait, score in self.meta_content["traits"].items():
                label = trait_labels.get(trait, trait)
                table.add_row(label, str(score))

            console.print(table)

    def _adjust(self) -> bool:
        """Allow user to adjust soul profile."""
        from cinder_cli.soul_adjuster import SoulAdjuster

        adjuster = SoulAdjuster(str(self.soul_path))
        return adjuster.run()

    def _explain_dimensions(self) -> None:
        """Explain all dimensions."""
        from cinder_cli.dimension_explainer import DimensionExplainer

        explanation = DimensionExplainer.explain_all_dimensions()
        
        from rich.prompt import Prompt
        lines = explanation.split("\n")
        page_size = 20
        current_line = 0

        while current_line < len(lines):
            end_line = min(current_line + page_size, len(lines))
            page = "\n".join(lines[current_line:end_line])
            console.print(page)

            current_line = end_line
            if current_line < len(lines):
                console.print("\n[dim]按 Enter 继续查看，输入 q 返回[/dim]")
                response = Prompt.ask("", default="")
                if response.lower() == "q":
                    break

    def _display_full(self) -> None:
        """Display full soul profile with pagination."""
        from rich.prompt import Prompt

        lines = self.soul_content.split("\n")
        page_size = 30
        current_line = 0

        while current_line < len(lines):
            end_line = min(current_line + page_size, len(lines))
            page = "\n".join(lines[current_line:end_line])
            console.print(Panel(page, title="[bold cyan]Soul Profile[/bold cyan]"))

            current_line = end_line
            if current_line < len(lines):
                console.print("\n[dim]按 Enter 继续查看，输入 q 返回[/dim]")
                response = Prompt.ask("", default="")
                if response.lower() == "q":
                    break

    def _mark_confirmed(self) -> None:
        """Mark soul profile as confirmed in meta file."""
        from datetime import datetime

        if self.meta_path.exists():
            with open(self.meta_path, encoding="utf-8") as f:
                meta = yaml.safe_load(f) or {}
        else:
            meta = {}

        meta["confirmed"] = True
        meta["confirmed_at"] = datetime.now().isoformat(timespec="seconds")

        with open(self.meta_path, "w", encoding="utf-8") as f:
            yaml.dump(meta, f, default_flow_style=False, allow_unicode=True)

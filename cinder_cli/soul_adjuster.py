"""
Soul adjuster module for modifying soul profiles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import questionary
import yaml
from rich.console import Console
from rich.table import Table

console = Console()


class SoulAdjuster:
    """Allows users to adjust their soul profile."""

    def __init__(self, soul_path: str):
        self.soul_path = Path(soul_path).expanduser().resolve()
        self.meta_path = self.soul_path.with_suffix(".meta.yaml")
        self.soul_content = ""
        self.meta_content: dict[str, Any] = {}

    def load(self) -> None:
        """Load soul files."""
        if self.meta_path.exists():
            with open(self.meta_path, encoding="utf-8") as f:
                self.meta_content = yaml.safe_load(f) or {}

    def save(self) -> None:
        """Save meta file."""
        with open(self.meta_path, "w", encoding="utf-8") as f:
            yaml.dump(self.meta_content, f, default_flow_style=False, allow_unicode=True)

    def adjust_traits(self) -> bool:
        """Allow manual adjustment of trait scores."""
        self.load()

        if "traits" not in self.meta_content:
            console.print("[red]未找到 trait 数据[/red]")
            return False

        console.print("\n[bold cyan]调整 Trait 分数[/bold cyan]")
        console.print("当前分数 (0-100):")

        table = Table()
        table.add_column("特质", style="cyan")
        table.add_column("当前分数", style="magenta")

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

        trait_choices = list(trait_labels.values())
        selected = questionary.select(
            "选择要调整的特质:",
            choices=trait_choices + ["完成调整"],
        ).ask()

        if not selected or selected == "完成调整":
            return False

        trait_key = None
        for key, label in trait_labels.items():
            if label == selected:
                trait_key = key
                break

        if not trait_key:
            return False

        current_score = self.meta_content["traits"].get(trait_key, 50)
        new_score = questionary.text(
            f"输入新的分数 (当前: {current_score}, 范围 0-100):",
            default=str(current_score),
        ).ask()

        if not new_score:
            return False

        try:
            score = int(new_score)
            if 0 <= score <= 100:
                self.meta_content["traits"][trait_key] = score
                self.save()
                console.print(f"[green]✓ 已更新 {selected} 为 {score}[/green]")
                return True
            else:
                console.print("[red]分数必须在 0-100 之间[/red]")
                return False
        except ValueError:
            console.print("[red]请输入有效的数字[/red]")
            return False

    def add_custom_rule(self) -> bool:
        """Add a custom decision rule."""
        self.load()

        console.print("\n[bold cyan]添加自定义决策规则[/bold cyan]")
        console.print("自定义规则将优先于自动推断的规则。")

        rule_name = questionary.text(
            "规则名称 (例如: '投资决策', '职业选择'):"
        ).ask()

        if not rule_name:
            return False

        rule_description = questionary.text(
            "规则描述 (例如: '在投资决策中，优先选择低风险选项'):"
        ).ask()

        if not rule_description:
            return False

        if "custom_rules" not in self.meta_content:
            self.meta_content["custom_rules"] = []

        self.meta_content["custom_rules"].append({
            "name": rule_name,
            "description": rule_description,
            "priority": 100,  # High priority
        })

        self.save()
        console.print(f"[green]✓ 已添加自定义规则: {rule_name}[/green]")
        return True

    def reanswer_question(self, question_key: str) -> bool:
        """Reanswer a specific question."""
        self.load()

        if "raw_answers" not in self.meta_content:
            console.print("[red]未找到原始答案数据[/red]")
            return False

        console.print(f"\n[bold cyan]重新回答问题 {question_key}[/bold cyan]")

        from cinder_cli.question_guide import QUESTIONS

        question = None
        for q in QUESTIONS:
            if q.key == question_key:
                question = q
                break

        if not question:
            console.print(f"[red]未找到问题: {question_key}[/red]")
            return False

        console.print(f"\n[bold]{question.title}[/bold]")
        console.print(question.prompt)

        for opt in question.options:
            console.print(f"  {opt.key}. {opt.text}")

        choice = questionary.select(
            "请选择:",
            choices=[opt.key for opt in question.options],
        ).ask()

        if not choice:
            return False

        reason = questionary.text(
            "可选：补充原因 (直接回车跳过):"
        ).ask() or ""

        self.meta_content["raw_answers"][question_key] = {
            "choice": choice,
            "reason": reason,
        }

        self._recalculate_traits()

        self.save()
        console.print(f"[green]✓ 已更新问题 {question_key} 的答案[/green]")
        return True

    def _recalculate_traits(self) -> None:
        """Recalculate trait scores based on updated answers."""
        from cinder_cli.question_guide import QUESTIONS, TRAITS

        scores = {trait: 50 for trait in TRAITS}

        for question in QUESTIONS:
            if question.key not in self.meta_content["raw_answers"]:
                continue

            choice = self.meta_content["raw_answers"][question.key]["choice"]
            option = next(opt for opt in question.options if opt.key == choice)

            for trait, delta in option.effects.items():
                scores[trait] = max(0, min(100, scores[trait] + delta))

        self.meta_content["traits"] = scores

    def run(self) -> bool:
        """Run the adjustment interface."""
        while True:
            action = questionary.select(
                "选择调整方式:",
                choices=[
                    "重新回答某个问题",
                    "手动调整 trait 分数",
                    "添加自定义决策规则",
                    "查看当前配置",
                    "返回",
                ],
            ).ask()

            if not action or "返回" in action:
                return False

            if "重新回答" in action:
                self._reanswer_menu()
            elif "手动调整" in action:
                self.adjust_traits()
            elif "添加自定义" in action:
                self.add_custom_rule()
            elif "查看当前" in action:
                self._show_current_config()

        return False

    def _reanswer_menu(self) -> None:
        """Show menu for selecting which question to reanswer."""
        from cinder_cli.question_guide import QUESTIONS

        choices = [f"{q.key}: {q.title}" for q in QUESTIONS] + ["返回"]

        selected = questionary.select(
            "选择要重新回答的问题:",
            choices=choices,
        ).ask()

        if not selected or "返回" in selected:
            return

        question_key = selected.split(":")[0]
        self.reanswer_question(question_key)

    def _show_current_config(self) -> None:
        """Show current configuration."""
        self.load()

        console.print("\n[bold cyan]当前配置[/bold cyan]")

        if "traits" in self.meta_content:
            console.print("\n[bold]Trait 分数:[/bold]")
            for trait, score in self.meta_content["traits"].items():
                console.print(f"  {trait}: {score}")

        if "custom_rules" in self.meta_content:
            console.print("\n[bold]自定义规则:[/bold]")
            for rule in self.meta_content["custom_rules"]:
                console.print(f"  - {rule['name']}: {rule['description']}")

        if not self.meta_content.get("traits") and not self.meta_content.get("custom_rules"):
            console.print("[dim]暂无配置[/dim]")

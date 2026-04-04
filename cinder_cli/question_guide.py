"""
Question guidance module for interactive soul profile generation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import questionary
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@dataclass(frozen=True)
class Option:
    key: str
    text: str
    effects: dict[str, int]
    summary: str


@dataclass(frozen=True)
class Question:
    key: str
    title: str
    prompt: str
    dimension: str
    options: tuple[Option, ...]


QUESTIONS = (
    Question(
        key="q1",
        title="面对陌生任务，你的第一反应是什么？",
        prompt="你接手一个重要但信息不完整的新任务，只能先做一件事。你最可能：",
        dimension="未知应对",
        options=(
            Option("A", "先把问题拆开，建立一个清晰框架，再行动", {"structure": 14, "evidence_orientation": 10, "action_bias": -4}, "先建结构，降低不确定性"),
            Option("B", "先做一个很小的实验，用反馈倒逼理解", {"exploration": 14, "adaptability": 12, "action_bias": 6, "structure": -4}, "先试错，用反馈逼近问题"),
            Option("C", "先找关键人聊，尽快知道真实约束和机会", {"relationship_orientation": 14, "social_energy": 10, "adaptability": 6}, "先摸清关系与现实约束"),
            Option("D", "先识别风险和底线，避免一开始走错", {"risk_tolerance": -12, "structure": 8, "evidence_orientation": 6}, "先守住风险边界"),
        ),
    ),
    Question(
        key="q2",
        title="当计划好的事情被突然打断时，你第一反应更接近哪一种？",
        prompt="比如临时加任务、约定取消、节奏被打乱。你更常见的反应是：",
        dimension="情绪调节",
        options=(
            Option("A", "会有明显烦躁，但能较快调整并重新进入状态", {"emotional_reactivity": 8, "recovery_speed": 8}, "会波动，但恢复较快"),
            Option("B", "基本不受影响，立刻切换状态，优先处理变化本身", {"emotional_reactivity": -10, "recovery_speed": 14, "action_bias": 6}, "情绪稳定，快速切换"),
            Option("C", "会焦虑并担心连锁影响，需要一点外部安抚或确认", {"emotional_reactivity": 14, "recovery_speed": -8, "reassurance_need": 16, "risk_tolerance": -4}, "容易焦虑，需要确认感"),
            Option("D", "表面继续推进，但情绪会滞留，后面容易累积消耗", {"emotional_reactivity": 10, "recovery_speed": -10, "reassurance_need": 6}, "外表稳定，内部消耗"),
        ),
    ),
    Question(
        key="q3",
        title="当你和重要的人意见强烈不一致时，你更倾向怎么处理？",
        prompt="发生冲突时，你更自然的处理方式是：",
        dimension="冲突处理",
        options=(
            Option("A", "先保护关系，避免把场面弄僵", {"relationship_orientation": 14, "evidence_orientation": -6, "action_bias": -4}, "先稳住关系"),
            Option("B", "先把事实和逻辑讲清楚，对事不对人", {"evidence_orientation": 14, "structure": 6, "relationship_orientation": -4}, "先求真，再处理情绪"),
            Option("C", "先暂停争论，回头找更好的机制避免重复冲突", {"structure": 10, "adaptability": 8, "evidence_orientation": 6}, "优先找机制而非纠缠当下"),
            Option("D", "先快速定方向，宁可事后再修正", {"action_bias": 14, "risk_tolerance": 8, "structure": -4}, "先推进，后修正"),
        ),
    ),
    Question(
        key="q4",
        title="在"稳妥收益"和"高波动高回报"之间，你通常怎么选？",
        prompt="面对收益与风险的权衡时，你更常见的选择是：",
        dimension="风险偏好",
        options=(
            Option("A", "选稳妥的，先把确定性拿到手", {"risk_tolerance": -16, "structure": 6, "exploration": -6}, "优先确定性"),
            Option("B", "主体选稳妥，同时留一小部分试错空间", {"risk_tolerance": 2, "exploration": 8, "structure": 8, "adaptability": 6}, "稳健主策略，加一点探索"),
            Option("C", "倾向高回报，只要上限足够值得", {"risk_tolerance": 16, "exploration": 10, "action_bias": 6, "structure": -6}, "为了上限愿意承受波动"),
            Option("D", "先暂停，继续找能兼顾两者的新方案", {"adaptability": 12, "structure": 8, "action_bias": -4}, "继续优化，不急着二选一"),
        ),
    ),
    Question(
        key="q5",
        title="你最自然的"恢复能量"方式是什么？",
        prompt="经历一周高压后，你终于有一个完整空档。你更想：",
        dimension="能量恢复",
        options=(
            Option("A", "一个人安静做点有沉浸感的事", {"social_energy": -16, "meaning_drive": 6, "structure": 4}, "独处沉浸恢复"),
            Option("B", "和少数熟悉的人待在一起", {"social_energy": -4, "relationship_orientation": 10, "meaning_drive": 4}, "熟人连接恢复"),
            Option("C", "去新地方、见新的人、换新刺激", {"social_energy": 16, "exploration": 10, "risk_tolerance": 4}, "通过新刺激恢复"),
            Option("D", "什么都不预设，到时候看感觉", {"adaptability": 12, "structure": -8, "exploration": 4}, "保持自由流动恢复"),
        ),
    ),
    Question(
        key="q6",
        title="当一件你很在意的目标长期推进不顺时，你最可能怎么调整？",
        prompt="长期受阻时，你最自然的重启方式是：",
        dimension="长期动力",
        options=(
            Option("A", "把目标拆得更细，靠纪律和系统继续推进", {"discipline_drive": 16, "structure": 10, "meaning_drive": -4}, "靠纪律和节奏维持推进"),
            Option("B", "重新定义目标，但保留前进节奏", {"adaptability": 14, "exploration": 8, "discipline_drive": 4}, "换路径，不轻易停下"),
            Option("C", "找外部监督或伙伴，让自己被推动", {"relationship_orientation": 10, "social_energy": 8, "discipline_drive": 6, "reassurance_need": 4}, "借助他律和陪伴重启"),
            Option("D", "先回到"我为什么想要它"，重新确认意义", {"meaning_drive": 18, "evidence_orientation": 4, "discipline_drive": -4}, "先重连意义，再恢复投入"),
        ),
    ),
)

TRAITS = (
    "exploration",
    "structure",
    "risk_tolerance",
    "evidence_orientation",
    "relationship_orientation",
    "action_bias",
    "social_energy",
    "meaning_drive",
    "discipline_drive",
    "adaptability",
    "emotional_reactivity",
    "recovery_speed",
    "reassurance_need",
)

TRAIT_LABELS = {
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


class QuestionGuide:
    """Manages interactive question guidance for soul profile generation."""

    def __init__(
        self,
        output_path: str = "soul.md",
        name: str = "",
        quick_mode: bool = False,
    ):
        self.output_path = Path(output_path).expanduser().resolve()
        self.name = name
        self.quick_mode = quick_mode
        self.answers: dict[str, dict[str, str]] = {}
        self.session_file = self.output_path.parent / ".cinder_session.json"

    def run(self) -> None:
        """Run the interactive question guidance."""
        console.print("\n[bold cyan]欢迎使用 soul 画像生成器[/bold cyan]")
        console.print("请根据第一直觉作答，每题只能选一个最像你的答案。\n")

        for i, question in enumerate(QUESTIONS, 1):
            console.print(f"[dim]问题 {i}/{len(QUESTIONS)}[/dim]")
            answer = self._ask_question(question)
            self.answers[question.key] = answer
            self._save_session()

        self._generate_soul()

    def resume_session(self) -> None:
        """Resume an incomplete session."""
        if not self.session_file.exists():
            console.print("[yellow]未找到未完成的会话，开始新会话[/yellow]")
            self.run()
            return

        with open(self.session_file, encoding="utf-8") as f:
            self.answers = json.load(f)

        console.print(f"[green]已恢复之前的进度，已完成 {len(self.answers)}/{len(QUESTIONS)} 题[/green]")

        for i, question in enumerate(QUESTIONS, 1):
            if question.key in self.answers:
                continue

            console.print(f"[dim]问题 {i}/{len(QUESTIONS)}[/dim]")
            answer = self._ask_question(question)
            self.answers[question.key] = answer
            self._save_session()

        self._generate_soul()

    def _ask_question(self, question: Question) -> dict[str, str]:
        """Ask a single question and return the answer."""
        console.print(f"\n[bold]{question.title}[/bold]")
        console.print(question.prompt)

        choices = [f"{opt.key}. {opt.text}" for opt in question.options]
        
        if self.quick_mode:
            choice_key = question.options[0].key
            console.print(f"[dim]快速模式：自动选择 {choice_key}[/dim]")
        else:
            choice = questionary.select(
                "请选择最符合你的选项：",
                choices=choices,
            ).ask()

            if choice is None:
                raise KeyboardInterrupt("用户取消")

            choice_key = choice[0]

        if self.quick_mode:
            reason = ""
        else:
            reason = questionary.text(
                "可选：用一句话补充原因，直接回车可跳过："
            ).ask() or ""

        return {"choice": choice_key, "reason": reason}

    def _save_session(self) -> None:
        """Save current session to file."""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(self.answers, f, ensure_ascii=False, indent=2)

    def _generate_soul(self) -> None:
        """Generate soul.md and soul.meta.yaml from answers."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("生成 soul 画像...", total=None)
            
            scores = self._score_answers()
            self._write_soul_md(scores)
            self._write_soul_meta(scores)
            
            progress.remove_task(task)

        console.print(f"\n[green]✓ 已生成: {self.output_path}[/green]")
        console.print(f"[green]✓ 已生成: {self.output_path.with_suffix('.meta.yaml')}[/green]")

        if self.session_file.exists():
            self.session_file.unlink()

    def _score_answers(self) -> dict[str, int]:
        """Calculate trait scores from answers."""
        scores = {trait: 50 for trait in TRAITS}
        
        for question in QUESTIONS:
            if question.key not in self.answers:
                continue
            
            choice = self.answers[question.key]["choice"]
            option = next(opt for opt in question.options if opt.key == choice)
            
            for trait, delta in option.effects.items():
                scores[trait] = max(0, min(100, scores[trait] + delta))
        
        return scores

    def _write_soul_md(self, scores: dict[str, int]) -> None:
        """Write soul.md file."""
        from cli import render_markdown
        
        content = render_markdown(self.name, self.answers, scores)
        
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _write_soul_meta(self, scores: dict[str, int]) -> None:
        """Write soul.meta.yaml file."""
        from cli import render_metadata
        
        content = render_metadata(self.name, self.answers, scores)
        
        meta_path = self.output_path.with_suffix(".meta.yaml")
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(content)

#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated and will be removed in a future version.
Please use the new cinder command instead:

    cinder init [OPTIONS]

For more information, run: cinder --help
"""
from __future__ import annotations

import argparse
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from textwrap import fill

warnings.warn(
    "cli.py is deprecated. Please use 'cinder init' instead. "
    "Run 'cinder --help' for more information.",
    DeprecationWarning,
    stacklevel=2,
)

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
        title="在“稳妥收益”和“高波动高回报”之间，你通常怎么选？",
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
        title="你最自然的“恢复能量”方式是什么？",
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
            Option("D", "先回到“我为什么想要它”，重新确认意义", {"meaning_drive": 18, "evidence_orientation": 4, "discipline_drive": -4}, "先重连意义，再恢复投入"),
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

def clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, value))

def escape_yaml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="通过 6 个问题生成 soul.md")
    parser.add_argument("--output", default="soul.md", help="输出文件路径，默认 soul.md")
    parser.add_argument("--name", default="", help="可选，被分析者名字")
    return parser.parse_args()

def prompt_choice(question: Question) -> tuple[str, str]:
    print()
    print(question.title)
    print(fill(question.prompt, width=80))
    for option in question.options:
        print(f"  {option.key}. {option.text}")

    valid_choices = {option.key for option in question.options}
    while True:
        choice = input("请输入选项字母（A-D）: ").strip().upper()
        if choice in valid_choices:
            break
        print("输入无效，请输入 A、B、C 或 D。")

    reason = input("可选：用一句话补充原因，直接回车可跳过: ").strip()
    return choice, reason

def collect_answers() -> dict[str, dict[str, str]]:
    answers: dict[str, dict[str, str]] = {}
    print("欢迎使用 soul 画像生成器。")
    print("请根据第一直觉作答，每题只能选一个最像你的答案。")
    for question in QUESTIONS:
        choice, reason = prompt_choice(question)
        answers[question.key] = {"choice": choice, "reason": reason}
    return answers

def score_answers(answers: dict[str, dict[str, str]]) -> dict[str, int]:
    scores = {trait: 50 for trait in TRAITS}
    for question in QUESTIONS:
        selected_key = answers[question.key]["choice"]
        option = next(item for item in question.options if item.key == selected_key)
        for trait, delta in option.effects.items():
            scores[trait] = clamp(scores[trait] + delta)
    return scores

def select_option(question: Question, choice: str) -> Option:
    return next(item for item in question.options if item.key == choice)

def uncertainty_mode(scores: dict[str, int]) -> str:
    if scores["structure"] >= 68 and scores["action_bias"] <= 52:
        return "先建框架，再小步验证"
    if scores["exploration"] >= 68 and scores["action_bias"] >= 56:
        return "先试错拿反馈，再快速迭代"
    if scores["relationship_orientation"] >= 66:
        return "先摸清关键关系和现实约束"
    return "先明确边界，再选择可逆行动"

def emotion_mode(scores: dict[str, int]) -> str:
    if scores["emotional_reactivity"] <= 40 and scores["recovery_speed"] >= 62:
        return "波动低，能快速切换状态"
    if scores["emotional_reactivity"] >= 64 and scores["reassurance_need"] >= 62:
        return "容易焦虑，需要确认感和外部稳定器"
    if scores["recovery_speed"] <= 42:
        return "表面可推进，但情绪恢复较慢"
    return "会有波动，但整体能逐步回稳"

def conflict_mode(scores: dict[str, int]) -> str:
    if scores["relationship_orientation"] >= 70 and scores["evidence_orientation"] < 60:
        return "优先稳住关系，再推进分歧处理"
    if scores["evidence_orientation"] >= 70:
        return "对事求真，强调事实与逻辑"
    if scores["action_bias"] >= 65:
        return "先定方向，再在执行中修正"
    return "先降温，再通过机制避免重复摩擦"

def risk_mode(scores: dict[str, int]) -> str:
    if scores["risk_tolerance"] <= 38:
        return "总体保守，优先确定性与下行保护"
    if scores["risk_tolerance"] >= 66:
        return "愿意为上限承担波动，但要看到明显赔率"
    return "稳健主策略 + 局部探索"

def motivation_mode(scores: dict[str, int]) -> str:
    if scores["meaning_drive"] >= 72:
        return "确认意义后能长期投入"
    if scores["discipline_drive"] >= 72:
        return "依赖纪律、节奏和系统维持推进"
    if scores["relationship_orientation"] >= 66 or scores["reassurance_need"] >= 60:
        return "借助责任感、伙伴或外部确认推进"
    return "通过阶段反馈与调整保持动力"

def energy_style(scores: dict[str, int]) -> str:
    if scores["social_energy"] <= 35:
        return "独处沉浸恢复"
    if scores["social_energy"] >= 65:
        return "新刺激与外部互动恢复"
    return "熟悉关系与适度独处混合恢复"

def recommendation_style(scores: dict[str, int]) -> str:
    if scores["structure"] >= 65:
        return "先给结构化方案，再给备选分支"
    if scores["exploration"] >= 65:
        return "优先给可快速试错的方案，再补充收敛路径"
    return "先给结论，再给关键依据与取舍"

def persuasion_style(scores: dict[str, int]) -> str:
    if scores["evidence_orientation"] >= 68:
        return "用逻辑、证据和长期收益说服"
    if scores["relationship_orientation"] >= 68:
        return "结合关系影响与合作成本沟通"
    if scores["meaning_drive"] >= 70:
        return "把选择与长期价值和自我一致性连接"
    return "用可执行步骤和实际收益推动决策"

def warning_style(scores: dict[str, int]) -> str:
    if scores["risk_tolerance"] <= 40:
        return "提前标出风险边界、损失上限和回退方式"
    if scores["risk_tolerance"] >= 66:
        return "提醒高赔率方案的失败代价与止损条件"
    if scores["emotional_reactivity"] >= 64:
        return "优先降低干扰与认知负担，再展示关键取舍"
    return "并列展示保守方案与探索方案的代价"

def core_summary(scores: dict[str, int]) -> str:
    parts: list[str] = []
    if scores["structure"] >= 65:
        parts.append("偏好先看清结构再行动")
    elif scores["exploration"] >= 65:
        parts.append("偏好先通过试错获得真实反馈")
    else:
        parts.append("能在分析与行动之间保持平衡")

    if scores["evidence_orientation"] >= 65:
        parts.append("习惯用逻辑与证据校准判断")
    elif scores["relationship_orientation"] >= 65:
        parts.append("会把关系与现实协作放进同等权重")
    else:
        parts.append("会综合事实、感受与成本做权衡")

    if scores["meaning_drive"] >= 70:
        parts.append("长期动力更多来自意义一致性")
    elif scores["discipline_drive"] >= 70:
        parts.append("长期推进依赖纪律与稳定节奏")
    else:
        parts.append("更依赖阶段反馈维持状态")

    if scores["emotional_reactivity"] <= 42:
        parts.append("面对变化时情绪切换较为稳定")
    elif scores["recovery_speed"] <= 42:
        parts.append("面对扰动时需要更多恢复空间")
    else:
        parts.append("面对变化会有波动，但总体可回稳")

    return "；".join(parts) + "。"

def trait_tags(scores: dict[str, int]) -> list[str]:
    tags: list[str] = []
    if scores["structure"] >= 70:
        tags.append("结构驱动")
    elif scores["exploration"] >= 70:
        tags.append("探索驱动")
    else:
        tags.append("平衡判断")

    if scores["evidence_orientation"] >= 70:
        tags.append("证据导向")
    elif scores["relationship_orientation"] >= 70:
        tags.append("关系敏感")
    else:
        tags.append("综合权衡")

    if scores["risk_tolerance"] <= 38:
        tags.append("保守控险")
    elif scores["risk_tolerance"] >= 66:
        tags.append("机会进取")
    else:
        tags.append("稳健试错")

    if scores["meaning_drive"] >= 70:
        tags.append("意义驱动")
    elif scores["discipline_drive"] >= 70:
        tags.append("纪律驱动")
    else:
        tags.append("反馈驱动")

    if scores["emotional_reactivity"] <= 42:
        tags.append("情绪稳定")
    elif scores["reassurance_need"] >= 62:
        tags.append("确认感需求高")
    else:
        tags.append("可恢复波动")
    return tags

def trait_interpretations(scores: dict[str, int]) -> list[str]:
    items = []
    items.append("结构驱动：面对模糊问题时，会优先搭出框架与判断标准。" if scores["structure"] >= 65 else "探索驱动：更愿意通过试错和反馈快速逼近真实答案。")
    items.append("证据导向：被说服时更依赖逻辑、自洽和事实证据。" if scores["evidence_orientation"] >= 65 else "关系导向：在判断方案时会自然考虑协作氛围和人际成本。")
    items.append("稳健控险：面对高代价决策时，会天然提高下行保护权重。" if scores["risk_tolerance"] <= 40 else ("机会进取：当上限足够高时，愿意接受明显波动。" if scores["risk_tolerance"] >= 66 else "稳健试错：倾向主策略保守、局部探索。"))
    items.append("意义驱动：长期投入依赖目标与自我价值的一致性。" if scores["meaning_drive"] >= scores["discipline_drive"] else "纪律驱动：长期推进更依赖节奏、拆解和固定机制。")
    items.append("情绪稳定：变化发生时能较快从情绪切回任务。" if scores["emotional_reactivity"] <= 42 else ("确认需求：遇到扰动时更需要外部确认或稳定器。" if scores["reassurance_need"] >= 62 else "情绪有波动但可恢复：需要一点缓冲，之后仍能回到执行。"))
    return items

def decision_priorities(scores: dict[str, int]) -> list[str]:
    items = []
    if scores["risk_tolerance"] <= 40:
        items.append("第一优先级：风险边界清晰、可回退、避免高代价失误")
    elif scores["risk_tolerance"] >= 66:
        items.append("第一优先级：上限足够高，且失败代价在可控范围内")
    else:
        items.append("第一优先级：主策略稳健，同时保留局部探索空间")

    if scores["meaning_drive"] >= 70:
        items.append("第二优先级：与长期价值、身份认同和意义一致")
    elif scores["discipline_drive"] >= 70:
        items.append("第二优先级：能形成持续执行节奏，不依赖临时状态")
    else:
        items.append("第二优先级：可快速推进，并能持续获得反馈")

    if scores["relationship_orientation"] >= 66:
        items.append("第三优先级：兼顾关系质量、协作成本与责任边界")
    elif scores["evidence_orientation"] >= 66:
        items.append("第三优先级：逻辑充分、前提清晰、方案可解释")
    else:
        items.append("第三优先级：现实可行，不额外制造认知负担")
    return items

def decision_taboos(scores: dict[str, int]) -> list[str]:
    items = []
    if scores["risk_tolerance"] <= 40:
        items.append("禁止把高不可逆风险包装成“大胆尝试”")
    else:
        items.append("禁止只因短期安全感而放弃长期更优路径")

    if scores["social_energy"] <= 40:
        items.append("禁止默认推荐高强度、长时间、低收益的社交型方案")
    else:
        items.append("禁止把协作问题完全当作个人闭门问题处理")

    if scores["emotional_reactivity"] >= 64 or scores["reassurance_need"] >= 62:
        items.append("禁止在用户明显波动时一次性塞入过多复杂选项")
    else:
        items.append("禁止只给抽象判断，不给可执行下一步")
    return items

def communication_preferences(scores: dict[str, int]) -> list[str]:
    items = ["先讲结论，再讲依据"]
    items.append("多用结构化表达，少用情绪渲染" if scores["structure"] >= 60 else "允许保留一定开放讨论空间")
    items.append("明确每个选项的代价、前提和适用条件")
    items.append("优先提供 2 到 3 个可比较方案")
    if scores["emotional_reactivity"] >= 64:
        items.append("在高扰动场景下先降复杂度，再补充完整分析")
    return items

def agent_rules(scores: dict[str, int]) -> list[str]:
    rules = []
    rules.append("当问题模糊时，先帮助用户澄清结构和约束" if scores["structure"] >= 60 else "当问题模糊时，先给一个低成本试探方案")
    rules.append("当方案不可逆时，提高谨慎权重并展示回退路径")
    rules.append("至少提供一个稳健方案和一个探索方案")
    if scores["social_energy"] <= 40:
        rules.append("不要默认推荐高强度社交解法，除非收益显著")
    else:
        rules.append("协作议题中主动考虑人际协同与外部资源")
    if scores["meaning_drive"] >= 70:
        rules.append("建议中明确说明它如何服务于长期价值和身份一致性")
    else:
        rules.append("建议中明确下一步动作与短期反馈点")
    if scores["reassurance_need"] >= 62:
        rules.append("用户波动时，先补确认感与清晰边界，再推进选择")
    return rules

def blind_spots(scores: dict[str, int]) -> list[str]:
    items = []
    if scores["structure"] >= 68 and scores["action_bias"] <= 52:
        items.append("可能因为想清楚再动而错过最佳行动窗口")
    if scores["risk_tolerance"] <= 38:
        items.append("可能高估失败代价，低估可逆试错的收益")
    if scores["risk_tolerance"] >= 66:
        items.append("可能高估高上限机会，低估持续波动的消耗")
    if scores["relationship_orientation"] >= 68:
        items.append("可能为了关系稳定压低真实立场")
    if scores["evidence_orientation"] >= 68:
        items.append("可能高估逻辑一致性，低估人际现实和情境因素")
    if scores["meaning_drive"] >= 72:
        items.append("可能在意义感不足时显著降低执行力")
    if scores["reassurance_need"] >= 62:
        items.append("可能在不确定时过度等待外部确认，拖慢决断")
    if scores["recovery_speed"] <= 42:
        items.append("可能低估连续扰动对状态和判断质量的侵蚀")
    if not items:
        items.append("在平衡多种约束时，可能因为顾及过多而拖慢决断")
    return items

def counterbalance(scores: dict[str, int]) -> list[str]:
    items = []
    if scores["risk_tolerance"] <= 40:
        items.append("对高价值且可逆的机会，主动增加一个低成本试错选项")
    if scores["risk_tolerance"] >= 66:
        items.append("对激进方案，强制展示失败代价、止损点和撤退条件")
    if scores["relationship_orientation"] >= 66:
        items.append("涉及协作时，同时评估边界、责任与长期成本")
    if scores["evidence_orientation"] >= 66:
        items.append("在逻辑充分时，补充人际现实与执行阻力评估")
    if scores["meaning_drive"] >= 70:
        items.append("当用户状态下滑时，先重连目标意义，再安排执行节奏")
    if scores["reassurance_need"] >= 62:
        items.append("在不确定场景中，先给稳定锚点，再讨论开放选项")
    if scores["recovery_speed"] <= 42:
        items.append("连续高压场景下，显式安排缓冲与恢复窗口")
    if not items:
        items.append("当分析超过阈值时，强制进入小样本验证")
    return items

def scene_guidance(scores: dict[str, int]) -> list[str]:
    items = []
    if scores["structure"] >= 60:
        items.append("职业 / 学习决策：先列选项、约束与评估标准，再比较长期复利与风险边界")
    else:
        items.append("职业 / 学习决策：先做一个低成本试探，再根据反馈逐步收敛")

    if scores["social_energy"] <= 40:
        items.append("社交决策：优先小范围、高质量、可提前预期的社交，不勉强高噪音场景")
    else:
        items.append("社交决策：适合把社交作为资源获取与能量恢复的一部分，但要避免无目的消耗")

    if scores["emotional_reactivity"] >= 64 or scores["recovery_speed"] <= 42:
        items.append("突发情况决策：先稳定情绪和优先级，再处理细节，避免在扰动中做大决定")
    else:
        items.append("突发情况决策：可以先处理变化本身，再补责任划分与长期修正")

    if scores["exploration"] >= 60:
        items.append("新事物决策：允许主动试错，但要设置验证点与止损条件")
    else:
        items.append("新事物决策：先查资料和建立基本框架，再进入小步尝试")
    return items

def boundary_reminders(scores: dict[str, int]) -> list[str]:
    items = [
        "涉及重大财务支出、人生路径或高不可逆决策时，agent 只提供贴合偏好的建议，不直接代替最终拍板",
        "当短期情绪与长期人格画像冲突时，agent 需要并列呈现顺从当下与符合长期自我的两种方案",
        "当现实约束明显高于人格偏好时，agent 需要说明折中方案，而不是机械迎合偏好",
    ]
    if scores["reassurance_need"] >= 62:
        items.append("当用户明显需要确认感时，先提供稳定锚点与下一步，不以开放问题增加焦虑")
    else:
        items.append("当用户状态稳定时，可以适度扩大选择空间，帮助其看见更优解")
    return items

def dynamic_adjustment() -> list[str]:
    return [
        "后续若重新答题或补充行为证据，应更新基础答案、trait 向量与决策规则",
        "若用户反馈“建议不像我”，优先排查画像偏差，再调整规则，而不是直接推翻所有结论",
        "每累计 3 次关键决策，可复盘一次结果与偏差，持续收敛 soul.md",
    ]

def render_trait_scores(scores: dict[str, int]) -> str:
    return "\n".join(f"- {TRAIT_LABELS[trait]}：{scores[trait]}" for trait in TRAITS)

def render_basic_info(answers: dict[str, dict[str, str]]) -> str:
    lines = []
    for question in QUESTIONS:
        answer = answers[question.key]
        option = select_option(question, answer["choice"])
        lines.append(f"- {question.dimension}：{answer['choice']} / {option.summary}")
    return "\n".join(lines)

def render_answers(answers: dict[str, dict[str, str]]) -> str:
    lines = []
    for question in QUESTIONS:
        answer = answers[question.key]
        option = select_option(question, answer["choice"])
        lines.append(f"## {question.key.upper()} {question.title}")
        lines.append(f"- 维度：{question.dimension}")
        lines.append(f"- 选择：{answer['choice']} / {option.text}")
        lines.append(f"- 推理摘要：{option.summary}")
        lines.append(f"- 原因：{answer['reason'] or '未提供'}")
        lines.append("")
    return "\n".join(lines).rstrip()

def render_metadata(name: str, answers: dict[str, dict[str, str]], scores: dict[str, int]) -> str:
    timestamp = datetime.now().isoformat(timespec="seconds")
    lines = [
        "version: 2",
        'source: "six_question_inference"',
        "question_count: 6",
        'confidence: "medium"',
        f'updated_at: "{timestamp}"',
        f'name: "{escape_yaml(name)}"' if name else 'name: ""',
        "raw_answers:",
    ]
    for question in QUESTIONS:
        answer = answers[question.key]
        lines.append(f"  {question.key}:")
        lines.append(f'    dimension: "{question.dimension}"')
        lines.append(f'    choice: "{answer["choice"]}"')
        lines.append(f'    reason: "{escape_yaml(answer["reason"])}"')
    lines.append("traits:")
    for trait in TRAITS:
        lines.append(f"  {trait}: {scores[trait]}")
    lines.append("core_traits:")
    for item in trait_tags(scores):
        lines.append(f'  - "{escape_yaml(item)}"')
    lines.extend(
        [
            "decision_profile:",
            f'  uncertainty_mode: "{escape_yaml(uncertainty_mode(scores))}"',
            f'  emotional_mode: "{escape_yaml(emotion_mode(scores))}"',
            f'  conflict_mode: "{escape_yaml(conflict_mode(scores))}"',
            f'  risk_mode: "{escape_yaml(risk_mode(scores))}"',
            f'  motivation_mode: "{escape_yaml(motivation_mode(scores))}"',
            f'  energy_mode: "{escape_yaml(energy_style(scores))}"',
            "agent_directives:",
            f'  recommendation_style: "{escape_yaml(recommendation_style(scores))}"',
            f'  persuasion_style: "{escape_yaml(persuasion_style(scores))}"',
            f'  warning_style: "{escape_yaml(warning_style(scores))}"',
        ]
    )
    return "\n".join(lines)

def render_markdown(name: str, answers: dict[str, dict[str, str]], scores: dict[str, int]) -> str:
    subject = name or "该用户"
    sections = [
        "# Soul",
        "",
        "## 基础信息",
        render_basic_info(answers),
        "",
        "## 核心人格摘要",
        f"{subject}{core_summary(scores)}",
        "",
        "## 核心特质",
        "\n".join(f"- {item}" for item in trait_tags(scores)),
        "",
        "## 特质解读",
        "\n".join(f"- {item}" for item in trait_interpretations(scores)),
        "",
        "## Trait Vector",
        render_trait_scores(scores),
        "",
        "## 决策画像",
        f"- 面对不确定性：{uncertainty_mode(scores)}",
        f"- 面对扰动时：{emotion_mode(scores)}",
        f"- 处理冲突：{conflict_mode(scores)}",
        f"- 风险取向：{risk_mode(scores)}",
        f"- 动力系统：{motivation_mode(scores)}",
        f"- 恢复方式：{energy_style(scores)}",
        "",
        "## Agent 决策核心准则",
        "\n".join(f"- {item}" for item in decision_priorities(scores)),
        "",
        "## 决策禁忌",
        "\n".join(f"- {item}" for item in decision_taboos(scores)),
        "",
        "## 沟通偏好",
        "\n".join(f"- {item}" for item in communication_preferences(scores)),
        "",
        "## Agent 行为准则",
        "\n".join(f"- {item}" for item in agent_rules(scores)),
        "",
        "## 典型场景适配",
        "\n".join(f"- {item}" for item in scene_guidance(scores)),
        "",
        "## 高概率盲点",
        "\n".join(f"- {item}" for item in blind_spots(scores)),
        "",
        "## 反向补偿策略",
        "\n".join(f"- {item}" for item in counterbalance(scores)),
        "",
        "## 决策边界提醒",
        "\n".join(f"- {item}" for item in boundary_reminders(scores)),
        "",
        "## 动态调整机制",
        "\n".join(f"- {item}" for item in dynamic_adjustment()),
        "",
        "## 证据附录",
        render_answers(answers),
        "",
    ]
    return "\n".join(sections)

def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def metadata_output_path(markdown_path: Path) -> Path:
    if markdown_path.suffix:
        return markdown_path.with_name(f"{markdown_path.stem}.meta.yaml")
    return markdown_path.with_name(f"{markdown_path.name}.meta.yaml")

def main() -> None:
    args = parse_args()
    answers = collect_answers()
    scores = score_answers(answers)
    name = args.name.strip()
    output_path = Path(args.output).expanduser().resolve()
    meta_path = metadata_output_path(output_path)
    markdown_content = render_markdown(name, answers, scores)
    metadata_content = render_metadata(name, answers, scores)
    write_output(output_path, markdown_content)
    write_output(meta_path, metadata_content)
    print()
    print(f"已生成: {output_path}")
    print(f"已生成: {meta_path}")

if __name__ == "__main__":
    main()

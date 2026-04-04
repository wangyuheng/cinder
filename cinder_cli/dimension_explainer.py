"""
Dimension explainer module for providing plain-language explanations.
"""

from __future__ import annotations

from typing import Any


class DimensionExplainer:
    """Provides plain-language explanations for soul dimensions."""

    EXPLANATIONS = {
        "未知应对": {
            "description": "面对陌生任务或不确定情况时的第一反应",
            "impact": "影响 agent 在面对模糊问题时的建议方式",
            "options": {
                "A": "偏好先建立清晰框架，降低不确定性后再行动。Agent 会优先帮你梳理结构和约束。",
                "B": "偏好通过小实验快速试错，用反馈逼近答案。Agent 会建议低成本试探方案。",
                "C": "偏好先了解人际关系和现实约束。Agent 会建议先与关键人物沟通。",
                "D": "偏好先识别风险和底线。Agent 会优先帮你划定安全边界。",
            },
        },
        "情绪调节": {
            "description": "计划被打断或遇到突发情况时的情绪反应模式",
            "impact": "影响 agent 在你情绪波动时的沟通策略",
            "options": {
                "A": "会有明显波动但能较快恢复。Agent 可以直接讨论问题本身。",
                "B": "情绪稳定，快速切换状态。Agent 可以专注于问题解决。",
                "C": "容易焦虑，需要确认感。Agent 会先提供稳定锚点再推进。",
                "D": "外表稳定但内部消耗。Agent 会注意你的能量状态，适时建议休息。",
            },
        },
        "冲突处理": {
            "description": "与重要的人意见不一致时的处理方式",
            "impact": "影响 agent 在协作场景中的建议风格",
            "options": {
                "A": "优先保护关系，避免场面僵硬。Agent 会建议温和的沟通方式。",
                "B": "优先讲清事实和逻辑。Agent 会帮你准备客观的论据。",
                "C": "优先找机制避免重复冲突。Agent 会建议建立规则和流程。",
                "D": "优先快速定方向。Agent 会建议果断决策，事后再修正。",
            },
        },
        "风险偏好": {
            "description": "在确定性和高回报之间的权衡方式",
            "impact": "影响 agent 对风险选项的推荐权重",
            "options": {
                "A": "优先确定性，先把稳妥收益拿到手。Agent 会推荐保守方案。",
                "B": "主体稳妥，留小部分试错空间。Agent 会推荐稳健+探索的组合。",
                "C": "倾向高回报，只要上限足够值得。Agent 会推荐进取型方案。",
                "D": "继续寻找兼顾两者的新方案。Agent 会帮你优化选项空间。",
            },
        },
        "能量恢复": {
            "description": "经历高压后恢复能量的方式",
            "impact": "影响 agent 在你疲惫时的支持建议",
            "options": {
                "A": "独处沉浸恢复。Agent 会建议安静的个人活动。",
                "B": "和熟悉的人待在一起。Agent 会建议小范围社交。",
                "C": "通过新刺激恢复。Agent 会建议尝试新事物。",
                "D": "自由流动，看感觉。Agent 会提供多种选项让你选择。",
            },
        },
        "长期动力": {
            "description": "长期目标推进受阻时的重启方式",
            "impact": "影响 agent 在你卡住时的支持策略",
            "options": {
                "A": "靠纪律和系统持续推进。Agent 会帮你细化目标和节奏。",
                "B": "重新定义目标但保持节奏。Agent 会建议调整路径。",
                "C": "找外部监督或伙伴推动。Agent 会建议寻找外部约束。",
                "D": "重新确认意义再恢复投入。Agent 会帮你重连目标价值。",
            },
        },
    }

    TRAIT_EXPLANATIONS = {
        "exploration": {
            "name": "探索倾向",
            "description": "对新事物和试错的开放程度",
            "high": "更愿意尝试新方法，通过实践获得反馈",
            "low": "更倾向于充分准备和规划后再行动",
        },
        "structure": {
            "name": "结构需求",
            "description": "对清晰框架和组织的依赖程度",
            "high": "需要明确的计划和结构才能高效工作",
            "low": "能在模糊和开放的环境中保持效率",
        },
        "risk_tolerance": {
            "name": "风险偏好",
            "description": "对不确定性和潜在损失的接受程度",
            "high": "愿意为高回报承担较大波动",
            "low": "优先考虑确定性和下行保护",
        },
        "evidence_orientation": {
            "name": "证据导向",
            "description": "决策时对逻辑和证据的依赖程度",
            "high": "更相信数据和逻辑分析",
            "low": "会综合考虑感受、关系和情境",
        },
        "relationship_orientation": {
            "name": "关系导向",
            "description": "决策时对人际关系的重视程度",
            "high": "会优先考虑对他人的影响",
            "low": "更关注任务本身而非人际因素",
        },
        "action_bias": {
            "name": "行动偏好",
            "description": "倾向于快速行动还是深思熟虑",
            "high": "偏好快速尝试和迭代",
            "low": "偏好充分分析后再行动",
        },
        "social_energy": {
            "name": "社交能量",
            "description": "从社交互动中获取或消耗能量的程度",
            "high": "通过与人互动恢复能量",
            "low": "通过独处恢复能量",
        },
        "meaning_drive": {
            "name": "意义驱动",
            "description": "对目标和价值一致性的重视程度",
            "high": "需要感受到意义才能持续投入",
            "low": "能通过纪律和习惯维持推进",
        },
        "discipline_drive": {
            "name": "纪律驱动",
            "description": "依靠系统和节奏维持推进的程度",
            "high": "通过固定机制和习惯保持动力",
            "low": "需要外部刺激或意义感维持动力",
        },
        "adaptability": {
            "name": "适应弹性",
            "description": "面对变化和不确定时的适应能力",
            "high": "能快速调整策略和方向",
            "low": "偏好稳定和可预期的环境",
        },
        "emotional_reactivity": {
            "name": "情绪反应强度",
            "description": "对扰动和压力的情绪反应程度",
            "high": "情绪反应明显，需要时间恢复",
            "low": "情绪波动较小，能快速稳定",
        },
        "recovery_speed": {
            "name": "情绪恢复速度",
            "description": "从情绪扰动中恢复的速度",
            "high": "能较快从波动中恢复",
            "low": "需要较长时间平复情绪",
        },
        "reassurance_need": {
            "name": "外部确认需求",
            "description": "对他人认可和确认的依赖程度",
            "high": "需要外部确认来建立信心",
            "low": "能自我确认，独立决策",
        },
    }

    @classmethod
    def explain_dimension(cls, dimension: str, choice: str | None = None) -> str:
        """Explain a dimension in plain language."""
        if dimension not in cls.EXPLANATIONS:
            return f"未知维度: {dimension}"

        info = cls.EXPLANATIONS[dimension]
        lines = [
            f"## {dimension}",
            "",
            f"**含义**: {info['description']}",
            "",
            f"**影响**: {info['impact']}",
        ]

        if choice and choice in info["options"]:
            lines.extend([
                "",
                f"**你的选择 ({choice})**: {info['options'][choice]}",
            ])

        return "\n".join(lines)

    @classmethod
    def explain_trait(cls, trait: str, score: int | None = None) -> str:
        """Explain a trait in plain language."""
        if trait not in cls.TRAIT_EXPLANATIONS:
            return f"未知特质: {trait}"

        info = cls.TRAIT_EXPLANATIONS[trait]
        lines = [
            f"## {info['name']}",
            "",
            f"**含义**: {info['description']}",
        ]

        if score is not None:
            if score >= 66:
                level = "高"
                description = info["high"]
            elif score <= 34:
                level = "低"
                description = info["low"]
            else:
                level = "中等"
                description = "在两个极端之间保持平衡"

            lines.extend([
                "",
                f"**你的水平**: {level} ({score}/100)",
                "",
                f"**表现**: {description}",
            ])

        return "\n".join(lines)

    @classmethod
    def explain_all_dimensions(cls) -> str:
        """Explain all dimensions."""
        lines = ["# Soul 维度说明", ""]
        for dimension in cls.EXPLANATIONS:
            lines.append(cls.explain_dimension(dimension))
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def explain_all_traits(cls, scores: dict[str, int] | None = None) -> str:
        """Explain all traits with optional scores."""
        lines = ["# Soul 特质说明", ""]
        for trait in cls.TRAIT_EXPLANATIONS:
            score = scores.get(trait) if scores else None
            lines.append(cls.explain_trait(trait, score))
            lines.append("")
        return "\n".join(lines)

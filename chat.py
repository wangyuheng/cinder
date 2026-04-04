#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated and will be removed in a future version.
Please use the new cinder command instead:

    cinder chat [OPTIONS]

For more information, run: cinder --help
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
import warnings
from pathlib import Path

warnings.warn(
    "chat.py is deprecated. Please use 'cinder chat' instead. "
    "Run 'cinder --help' for more information.",
    DeprecationWarning,
    stacklevel=2,
)

DEFAULT_EXIT_COMMANDS = {"exit", "quit", "q", ":q"}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="使用 soul.md 作为系统提示词进行问答，支持 Ollama 与 Claude 反思循环")
    parser.add_argument("--backend", choices=("ollama", "claude"), default="ollama", help="后端类型，默认 ollama")
    parser.add_argument("--model", default="qwen3.5:0.8b", help="Ollama 模型名，默认 qwen3.5:0.8b")
    parser.add_argument("--claude-command", default="claude", help="Claude CLI 命令名，默认 claude")
    parser.add_argument("--soul", default="soul.md", help="soul.md 路径，默认当前目录下的 soul.md")
    parser.add_argument("--meta", default="", help="可选，附加加载的 soul.meta.yaml 路径")
    parser.add_argument("--message", default="", help="单轮提问内容；不传则进入交互模式")
    parser.add_argument("--temperature", type=float, default=0.2, help="模型温度，默认 0.2")
    parser.add_argument("--reflection-loop", action="store_true", help="在 Claude 模式下启用反思与追问循环")
    parser.add_argument("--max-iterations", type=int, default=3, help="反思循环最大轮数，默认 3")
    parser.add_argument("--sleep-seconds", type=float, default=1.0, help="反思循环轮次之间的等待秒数，默认 1")
    return parser.parse_args()

def read_text(path_str: str, label: str) -> str:
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"{label} 不存在: {path}")
    return path.read_text(encoding="utf-8").strip()

def build_system_prompt(soul_content: str, meta_content: str = "") -> str:
    prompt_parts = [
        "你是一个基于用户 soul 画像工作的个人代理。",
        "你需要把 soul 内容当作高优先级系统提示词，保持建议、表达、权衡方式与其中描述一致。",
        "你的目标不是迎合用户一时情绪，而是在尊重画像偏好的前提下，给出更稳健、更长期一致的建议。",
        "如果用户的短期冲动与 soul 中的长期偏好冲突，请同时给出顺从当下和符合长期画像的两种方案，并明确代价，默认推荐更符合长期稳定自我的方案。",
        "以下是 soul.md 内容：",
        soul_content,
    ]
    if meta_content:
        prompt_parts.extend(["", "以下是 soul.meta.yaml 内容：", meta_content])
    return "\n".join(prompt_parts)

def get_chat_model(model_name: str, temperature: float):
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:
        raise RuntimeError("缺少依赖，请先执行 `pip install -r requirements.txt`。") from exc
    return ChatOllama(model=model_name, temperature=temperature)

def invoke_claude(prompt: str, system_prompt: str, command: str) -> str:
    cmd = [command, "--system-prompt", system_prompt]
    try:
        result = subprocess.run(
            cmd,
            input=prompt,
            capture_output=True,
            text=True,
            check=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"未找到 Claude CLI 命令: {command}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else str(exc)
        raise RuntimeError(f"Claude 调用失败: {stderr}") from exc
    return result.stdout.strip()

def invoke_once(model, system_prompt: str, user_message: str, history: list):
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    messages = [SystemMessage(content=system_prompt), *history, HumanMessage(content=user_message)]
    response = model.invoke(messages)
    history.append(HumanMessage(content=user_message))
    history.append(AIMessage(content=response.content))
    return response.content

def run_single_turn(model, system_prompt: str, user_message: str) -> int:
    try:
        answer = invoke_once(model, system_prompt, user_message, history=[])
    except Exception as exc:
        print(f"调用失败: {exc}", file=sys.stderr)
        print("请确认 Ollama 服务已启动，并且模型已经 pull 完成。", file=sys.stderr)
        return 1
    print(answer)
    return 0

def generate_reflection_prompt(user_message: str, answer: str) -> str:
    return f"""请对以下回答进行反思，并判断是否需要继续追问用户补充信息。

用户问题：
{user_message}

当前回答：
{answer}

请重点检查：
1. 是否真正回答了用户的问题。
2. 是否存在逻辑漏洞、遗漏条件或隐含假设。
3. 是否缺少关键上下文，导致无法给出高质量答案。
4. 在现有信息下，回答还能怎样更完整、更稳健。

请严格按以下格式输出：
## 反思
- 结论一
- 结论二

## 最终结论
- 是否需要追问：是/否
- 原因：一句话说明

## 改进后的回答
给出你此刻能提供的更好版本回答。

## 追问问题
如果不需要追问，只写：无
如果需要追问，按编号列出，例如：
1. 第一个问题
2. 第二个问题
"""

def reflection_needs_follow_up(reflection: str) -> bool:
    lowered = reflection.lower()
    if "是否需要追问：否" in reflection or "是否需要追问: 否" in reflection:
        return False
    if "是否需要追问：是" in reflection or "是否需要追问: 是" in reflection:
        return True
    if "无需追问" in reflection or "不需要追问" in reflection:
        return False
    return "需要追问" in lowered

def extract_improved_answer(reflection: str, fallback_answer: str) -> str:
    marker = "## 改进后的回答"
    if marker not in reflection:
        return fallback_answer
    section = reflection.split(marker, 1)[1]
    for stop_marker in ("## 追问问题",):
        if stop_marker in section:
            section = section.split(stop_marker, 1)[0]
    improved = section.strip()
    return improved or fallback_answer

def extract_follow_up_questions(reflection: str) -> list[str]:
    if not reflection_needs_follow_up(reflection):
        return []

    section = reflection
    marker = "## 追问问题"
    if marker in reflection:
        section = reflection.split(marker, 1)[1]
    section = section.strip()
    if not section or section == "无":
        return []

    questions: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "无":
            continue
        match = re.match(r"^(?:[-*]\s+|\d+[.)]\s+)(.+)$", stripped)
        candidate = match.group(1).strip() if match else stripped
        if candidate and ("?" in candidate or "？" in candidate or match):
            questions.append(candidate)

    if questions:
        return questions

    fallback = [line.strip() for line in section.splitlines() if line.strip()]
    return fallback[:3]

def build_claude_iteration_prompt(context: str) -> str:
    return f"""请基于以下完整上下文回答用户，直接给出当前阶段你能提供的最佳答案。

{context}
"""

def run_claude_once(system_prompt: str, user_message: str, command: str) -> int:
    try:
        answer = invoke_claude(user_message, system_prompt, command)
    except Exception as exc:
        print(f"调用失败: {exc}", file=sys.stderr)
        return 1
    print(answer)
    return 0

def run_claude_reflection_loop(
    system_prompt: str,
    initial_message: str,
    command: str,
    max_iterations: int,
    sleep_seconds: float,
) -> int:
    context = f"用户原始问题：\n{initial_message}"
    best_answer = ""

    for iteration in range(1, max_iterations + 1):
        print(f"\n=== 循环 {iteration}/{max_iterations} ===")
        print("生成回答中...")
        try:
            answer = invoke_claude(build_claude_iteration_prompt(context), system_prompt, command)
        except Exception as exc:
            print(f"调用失败: {exc}", file=sys.stderr)
            return 1
        print(f"\nClaude 回答:\n{answer}")

        print("\n生成反思中...")
        try:
            reflection = invoke_claude(generate_reflection_prompt(context, answer), system_prompt, command)
        except Exception as exc:
            print(f"反思失败: {exc}", file=sys.stderr)
            return 1
        print(f"\nClaude 反思:\n{reflection}")

        best_answer = extract_improved_answer(reflection, answer)
        questions = extract_follow_up_questions(reflection)
        if not questions:
            print("\n反思认为不需要继续追问，循环结束。")
            print("\n最终回答:\n" + best_answer)
            return 0

        print("\n需要追问用户补充信息：")
        for index, question in enumerate(questions, start=1):
            print(f"{index}. {question}")

        user_answers: list[str] = []
        for question in questions:
            try:
                reply = input(f"{question}\n你 > ").strip()
            except EOFError:
                reply = ""
            if reply:
                user_answers.append(f"- {question}\n  用户补充：{reply}")

        if not user_answers:
            print("\n未收到补充信息，输出当前最佳回答。")
            print("\n最终回答:\n" + best_answer)
            return 0

        context = "\n\n".join([context, "用户补充信息：", "\n".join(user_answers)])
        if iteration < max_iterations and sleep_seconds > 0:
            time.sleep(sleep_seconds)

    print("\n达到最大循环次数，输出当前最佳回答。")
    if best_answer:
        print("\n最终回答:\n" + best_answer)
    return 0

def run_interactive(model, system_prompt: str) -> int:
    history: list = []
    print("已进入对话模式。输入 exit / quit / q 结束。")
    while True:
        try:
            user_input = input("\n你 > ").strip()
        except EOFError:
            print()
            return 0
        if not user_input:
            continue
        if user_input.lower() in DEFAULT_EXIT_COMMANDS:
            return 0
        try:
            answer = invoke_once(model, system_prompt, user_input, history)
        except Exception as exc:
            print(f"调用失败: {exc}", file=sys.stderr)
            print("请确认 Ollama 服务已启动，并且模型已经 pull 完成。", file=sys.stderr)
            return 1
        print(f"\nAgent > {answer}")

def run_claude_interactive(
    system_prompt: str,
    command: str,
    reflection_loop: bool,
    max_iterations: int,
    sleep_seconds: float,
) -> int:
    print("已进入 Claude 对话模式。输入 exit / quit / q 结束。")
    while True:
        try:
            user_input = input("\n你 > ").strip()
        except EOFError:
            print()
            return 0
        if not user_input:
            continue
        if user_input.lower() in DEFAULT_EXIT_COMMANDS:
            return 0
        if reflection_loop:
            exit_code = run_claude_reflection_loop(
                system_prompt=system_prompt,
                initial_message=user_input,
                command=command,
                max_iterations=max_iterations,
                sleep_seconds=sleep_seconds,
            )
        else:
            exit_code = run_claude_once(system_prompt, user_input, command)
        if exit_code != 0:
            return exit_code

def main() -> int:
    args = parse_args()
    try:
        soul_content = read_text(args.soul, "soul.md")
        meta_content = read_text(args.meta, "soul.meta.yaml") if args.meta else ""
        system_prompt = build_system_prompt(soul_content, meta_content)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.backend == "claude":
        if args.message:
            if args.reflection_loop:
                return run_claude_reflection_loop(
                    system_prompt=system_prompt,
                    initial_message=args.message,
                    command=args.claude_command,
                    max_iterations=args.max_iterations,
                    sleep_seconds=args.sleep_seconds,
                )
            return run_claude_once(system_prompt, args.message, args.claude_command)
        return run_claude_interactive(
            system_prompt=system_prompt,
            command=args.claude_command,
            reflection_loop=args.reflection_loop,
            max_iterations=args.max_iterations,
            sleep_seconds=args.sleep_seconds,
        )

    try:
        model = get_chat_model(args.model, args.temperature)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.message:
        return run_single_turn(model, system_prompt, args.message)
    return run_interactive(model, system_prompt)

if __name__ == "__main__":
    raise SystemExit(main())

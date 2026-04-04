"""
Chat handler module for managing chat sessions with proxy decision support.
"""

from __future__ import annotations

from typing import Any

from cinder_cli.config import Config
from cinder_cli.decision_logger import DecisionLogger
from cinder_cli.proxy_decision import ProxyDecisionMaker


class ChatHandler:
    """Handles chat interactions with soul-guided agent."""

    def __init__(self, config: Config):
        self.config = config
        self.soul_content = self._load_soul()
        self.soul_meta = self._load_soul_meta()
        self.proxy_enabled = config.get("proxy_mode", False)
        self.logging_enabled = config.get("decision_logging", True)

        if self.logging_enabled:
            self.logger = DecisionLogger(config.database_path)

        if self.proxy_enabled and self.soul_meta:
            self.proxy_maker = ProxyDecisionMaker(self.soul_meta)

    def run_single(self, message: str) -> None:
        """Run single-turn chat."""
        response = self._invoke_backend(message)
        print(response)

    def run_interactive(self) -> None:
        """Run interactive chat session."""
        print("已进入对话模式。输入 exit / quit / q 结束。")
        print("命令: /proxy on|off - 切换代理模式")
        print("      /mode - 查看当前模式")
        print("      /help - 查看帮助")

        while True:
            try:
                user_input = input("\n你 > ").strip()
            except EOFError:
                print()
                break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit", "q"}:
                break

            if user_input.startswith("/"):
                self._handle_command(user_input)
                continue

            response = self._invoke_backend(user_input)
            print(f"\nAgent > {response}")

    def _handle_command(self, command: str) -> None:
        """Handle slash commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd == "/proxy":
            self._toggle_proxy_mode(args)
        elif cmd == "/mode":
            self._show_mode()
        elif cmd == "/help":
            self._show_help()
        else:
            print(f"未知命令: {cmd}")

    def _toggle_proxy_mode(self, args: str) -> None:
        """Toggle proxy mode."""
        if args in ["on", "enable", "true"]:
            self.proxy_enabled = True
            if self.soul_meta and not hasattr(self, "proxy_maker"):
                self.proxy_maker = ProxyDecisionMaker(self.soul_meta)
            print("✓ 代理模式已启用")
        elif args in ["off", "disable", "false"]:
            self.proxy_enabled = False
            print("✓ 代理模式已禁用")
        else:
            self.proxy_enabled = not self.proxy_enabled
            status = "启用" if self.proxy_enabled else "禁用"
            print(f"✓ 代理模式已{status}")

    def _show_mode(self) -> None:
        """Show current mode settings."""
        print("\n当前模式:")
        print(f"  代理模式: {'启用' if self.proxy_enabled else '禁用'}")
        print(f"  日志记录: {'启用' if self.logging_enabled else '禁用'}")
        print(f"  后端: {self.config.get('backend', 'ollama')}")
        print(f"  模型: {self.config.get('model', 'qwen3.5:9b')}")

    def _show_help(self) -> None:
        """Show help message."""
        print("\n可用命令:")
        print("  /proxy on|off - 启用/禁用代理模式")
        print("  /mode - 查看当前模式设置")
        print("  /help - 显示此帮助信息")
        print("  exit/quit/q - 退出对话")

    def _load_soul(self) -> str:
        """Load soul.md content."""
        soul_path = self.config.get("soul_path", "soul.md")
        try:
            with open(soul_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _load_soul_meta(self) -> dict[str, Any]:
        """Load soul.meta.yaml content."""
        meta_path = self.config.get("meta_path", "")
        if not meta_path:
            soul_path = self.config.get("soul_path", "soul.md")
            meta_path = soul_path.replace(".md", ".meta.yaml")

        try:
            import yaml
            with open(meta_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def _invoke_backend(self, message: str) -> str:
        """Invoke the appropriate backend."""
        backend = self.config.get("backend", "ollama")

        if backend == "claude":
            return self._invoke_claude(message)
        else:
            return self._invoke_ollama(message)

    def _invoke_ollama(self, message: str) -> str:
        """Invoke Ollama backend."""
        try:
            from langchain_ollama import ChatOllama
            from langchain_core.messages import HumanMessage, SystemMessage

            model_name = self.config.get("model", "qwen3.5:9b")
            temperature = self.config.get("temperature", 0.2)

            model = ChatOllama(model=model_name, temperature=temperature)

            system_prompt = self._build_system_prompt()
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message),
            ]

            response = model.invoke(messages)
            return response.content

        except Exception as e:
            return f"调用失败: {e}"

    def _invoke_claude(self, message: str) -> str:
        """Invoke Claude backend."""
        import subprocess

        claude_command = self.config.get("claude_command", "claude")
        system_prompt = self._build_system_prompt()

        try:
            result = subprocess.run(
                [claude_command, "--system-prompt", system_prompt],
                input=message,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except FileNotFoundError:
            return f"未找到 Claude CLI 命令: {claude_command}"
        except subprocess.CalledProcessError as e:
            return f"Claude 调用失败: {e.stderr}"

    def _build_system_prompt(self) -> str:
        """Build system prompt from soul content."""
        prompt_parts = [
            "你是一个基于用户 soul 画像工作的个人代理。",
            "你需要把 soul 内容当作高优先级系统提示词，保持建议、表达、权衡方式与其中描述一致。",
            "你的目标不是迎合用户一时情绪，而是在尊重画像偏好的前提下，给出更稳健、更长期一致的建议。",
            "如果用户的短期冲动与 soul 中的长期偏好冲突，请同时给出顺从当下和符合长期画像的两种方案，并明确代价，默认推荐更符合长期稳定自我的方案。",
            "以下是 soul.md 内容：",
            self.soul_content,
        ]
        return "\n".join(prompt_parts)

    def _handle_proxy_command(self, command: str) -> None:
        """Handle proxy decision command."""
        if not self.proxy_enabled:
            print("代理模式未启用。使用 --proxy 标志启用。")
            return

        print(f"处理代理决策: {command}")

        options = [
            {"text": "选项一", "risk": "low"},
            {"text": "选项二", "risk": "medium"},
            {"text": "选项三", "risk": "high"},
        ]

        result = self.proxy_maker.make_decision(command, options)

        print(f"\n决策结果: {result['decision']}")
        print(f"置信度: {result['confidence']:.2f}")
        print(f"需要人工确认: {result['requires_human']}")
        print(f"推理: {result['reasoning']}")

        if self.logging_enabled:
            self.logger.log_decision(
                context={"command": command},
                soul_rules={"applied": result["soul_rules_applied"]},
                decision=result,
                confidence=result["confidence"],
                requires_human=result["requires_human"],
            )

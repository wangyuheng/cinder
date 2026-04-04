"""
Code Generator - Generates code using Ollama.
"""

from __future__ import annotations

from typing import Any
import ollama

from cinder_cli.config import Config


class CodeGenerator:
    """Generates code using Ollama model."""

    def __init__(self, config: Config):
        self.config = config
        self.model_name = config.get("model", "qwen3.5:0.8b")
        self.temperature = config.get("temperature", 0.2)
        self.base_url = config.get("ollama_base_url", "http://localhost:11434")
        self.keep_alive = config.get("ollama_keep_alive", "10m")
        self.client = ollama.Client(host=self.base_url)

    def generate_code(
        self,
        description: str,
        language: str = "python",
        constraints: dict[str, Any] | None = None,
    ) -> str:
        """
        Generate code from description.

        Args:
            description: Task description
            language: Programming language
            constraints: Optional constraints

        Returns:
            Generated code
        """
        system_prompt = self._build_system_prompt(language, constraints)
        user_prompt = self._build_user_prompt(description, language)

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": self.temperature,
                    "num_ctx": 4096,
                    "think": False,
                },
                keep_alive=self.keep_alive,
            )

            code = response.get("message", {}).get("content", "")

            # Extract code from markdown if present
            code = self._extract_code(code)

            return code

        except Exception as e:
            return f"# Error generating code: {e}\n# Description: {description}"

    def _build_system_prompt(
        self,
        language: str,
        constraints: dict[str, Any] | None,
    ) -> str:
        """Build system prompt for code generation."""
        prompt_parts = [
            f"You are an expert {language} developer.",
            "Generate clean, efficient, and well-documented code.",
            "Follow best practices and include appropriate error handling.",
            "Include docstrings and comments where helpful.",
        ]

        if constraints:
            if "framework" in constraints:
                prompt_parts.append(f"Use the {constraints['framework']} framework.")
            if "style" in constraints:
                prompt_parts.append(f"Follow {constraints['style']} coding style.")

        return "\n".join(prompt_parts)

    def _build_user_prompt(self, description: str, language: str) -> str:
        """Build user prompt for code generation."""
        return f"Create {language} code for the following task:\n\n{description}\n\nProvide only the code, no explanations."

    def _extract_code(self, text: str) -> str:
        """Extract code from markdown code blocks."""
        if "```" in text:
            lines = text.split("\n")
            code_lines = []
            in_code_block = False

            for line in lines:
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    code_lines.append(line)

            return "\n".join(code_lines)

        return text

    def format_code(
        self,
        code: str,
        language: str = "python",
    ) -> dict[str, Any]:
        """
        Format code using appropriate formatter.

        Args:
            code: Code to format
            language: Programming language

        Returns:
            Formatted code and status
        """
        if language == "python":
            return self._format_python(code)
        elif language in ("javascript", "typescript"):
            return self._format_javascript(code)
        else:
            return {
                "status": "skipped",
                "code": code,
                "message": f"No formatter for {language}",
            }

    def _format_python(self, code: str) -> dict[str, Any]:
        """Format Python code using black-like formatting."""
        try:
            import subprocess
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(code)
                temp_path = f.name

            try:
                result = subprocess.run(
                    ["python", "-m", "black", temp_path],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    with open(temp_path, "r") as f:
                        formatted = f.read()
                    return {
                        "status": "success",
                        "code": formatted,
                        "message": "Formatted with black",
                    }
                else:
                    return {
                        "status": "error",
                        "code": code,
                        "message": result.stderr,
                    }
            finally:
                import os
                os.unlink(temp_path)

        except Exception as e:
            return {
                "status": "error",
                "code": code,
                "message": str(e),
            }

    def _format_javascript(self, code: str) -> dict[str, Any]:
        """Format JavaScript/TypeScript code."""
        return {
            "status": "skipped",
            "code": code,
            "message": "JavaScript formatting requires prettier",
        }

    def validate_syntax(
        self,
        code: str,
        language: str = "python",
    ) -> dict[str, Any]:
        """
        Validate code syntax.

        Args:
            code: Code to validate
            language: Programming language

        Returns:
            Validation result
        """
        if language == "python":
            return self._validate_python_syntax(code)
        else:
            return {
                "valid": True,
                "message": f"Syntax validation not implemented for {language}",
            }

    def _validate_python_syntax(self, code: str) -> dict[str, Any]:
        """Validate Python syntax."""
        try:
            compile(code, "<string>", "exec")
            return {
                "valid": True,
                "message": "Syntax OK",
            }
        except SyntaxError as e:
            return {
                "valid": False,
                "message": str(e),
                "line": e.lineno,
                "offset": e.offset,
            }

    def validate_imports(
        self,
        code: str,
        language: str = "python",
    ) -> dict[str, Any]:
        """
        Validate imports in code.

        Args:
            code: Code to validate
            language: Programming language

        Returns:
            Import validation result
        """
        if language != "python":
            return {
                "valid": True,
                "message": f"Import validation not implemented for {language}",
            }

        import ast
        import importlib.util

        try:
            tree = ast.parse(code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)

            missing = []
            for imp in imports:
                spec = importlib.util.find_spec(imp.split(".")[0])
                if spec is None:
                    missing.append(imp)

            return {
                "valid": len(missing) == 0,
                "imports": imports,
                "missing": missing,
                "message": "All imports available" if not missing else f"Missing: {missing}",
            }

        except Exception as e:
            return {
                "valid": False,
                "message": str(e),
            }

    def apply_template(
        self,
        template_name: str,
        variables: dict[str, Any],
    ) -> str:
        """
        Apply a code template.

        Args:
            template_name: Name of the template
            variables: Variables to substitute

        Returns:
            Generated code from template
        """
        templates = {
            "python_main": '''#!/usr/bin/env python3
"""
{description}
"""

def main():
    pass

if __name__ == "__main__":
    main()
''',
            "python_class": '''"""
{description}
"""

class {class_name}:
    """A class for {purpose}."""

    def __init__(self{init_args}):
        """Initialize {class_name}."""
        {init_body}

    def {method_name}(self{method_args}):
        """{method_description}."""
        pass
''',
            "fastapi_app": '''"""
{description}
"""

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {{"message": "Hello World"}}
''',
            "flask_app": '''"""
{description}
"""

from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run()
''',
        }

        template = templates.get(template_name, "# Template not found: {template_name}")

        try:
            return template.format(**variables)
        except KeyError as e:
            return f"# Template error: missing variable {e}"

    def generate_docstring(
        self,
        code: str,
        language: str = "python",
        style: str = "google",
    ) -> str:
        """
        Generate docstring for code.

        Args:
            code: Code to document
            language: Programming language
            style: Docstring style

        Returns:
            Generated docstring
        """
        if language != "python":
            return f"/* Generated docstring for {language} code */"

        lines = code.strip().split("\n")
        first_line = lines[0] if lines else ""

        if "def " in first_line:
            func_match = first_line.split("def ")[1].split("(")[0] if "def " in first_line else "function"
            args = []
            if "(" in first_line and ")" in first_line:
                args_str = first_line.split("(")[1].split(")")[0]
                args = [a.strip().split("=")[0].strip() for a in args_str.split(",") if a.strip() and a.strip() != "self"]

            if style == "google":
                docstring = f'"""{func_match} 函数。'
                if args:
                    docstring += "\n\nArgs:\n"
                    for arg in args:
                        docstring += f"    {arg}: 参数说明\n"
                docstring += '\nReturns:\n    返回值说明\n"""'
                return docstring

        return '"""函数说明。"""'

    def generate_readme(
        self,
        project_name: str,
        description: str,
        files: list[str],
    ) -> str:
        """
        Generate README content.

        Args:
            project_name: Name of the project
            description: Project description
            files: List of project files

        Returns:
            README content
        """
        readme = f"""# {project_name}

{description}

## 项目结构

```
{project_name}/
"""
        for f in files:
            readme += f"├── {f}\n"

        readme += """```

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

## 许可证

MIT
"""
        return readme

    def run_mypy(
        self,
        code: str,
        strict: bool = False,
    ) -> dict[str, Any]:
        """
        Run mypy type checking.

        Args:
            code: Code to check
            strict: Use strict mode

        Returns:
            Type checking result
        """
        try:
            import subprocess
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as f:
                f.write(code)
                temp_path = f.name

            try:
                cmd = ["python", "-m", "mypy", temp_path]
                if strict:
                    cmd.append("--strict")

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "errors": result.stderr,
                }
            finally:
                os.unlink(temp_path)

        except Exception as e:
            return {
                "success": False,
                "output": "",
                "errors": str(e),
            }

"""
Code Generator - Generates code using Ollama.
"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING
import ollama

from cinder_cli.config import Config
from cinder_cli.executor.token_tracker import TokenTracker

if TYPE_CHECKING:
    from cinder_cli.tracing import LLMTracer


class CodeGenerator:
    """Generates code using Ollama model."""

    def __init__(
        self,
        config: Config,
        token_tracker: TokenTracker | None = None,
        llm_tracer: LLMTracer | None = None,
    ):
        self.config = config
        self.model_name = config.get("model", "qwen3.5:0.8b")
        self.temperature = config.get("temperature", 0.2)
        self.base_url = config.get("ollama_base_url", "http://localhost:11434")
        self.keep_alive = config.get("ollama_keep_alive", "10m")
        self.stream = config.get("ollama_stream", True)
        self.debug = config.get("ollama_debug", False)
        self.client = ollama.Client(host=self.base_url)
        self.token_tracker = token_tracker
        self.llm_tracer = llm_tracer

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

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        options = {
            "temperature": self.temperature,
            "num_ctx": 4096,
            "think": False,
        }

        if self.debug:
            print(f"\n[DEBUG] Ollama Request:")
            print(f"  Model: {self.model_name}")
            print(f"  Messages: {messages}")
            print(f"  Options: {options}")
            print(f"  Keep Alive: {self.keep_alive}")
            print(f"  Stream: {self.stream}\n")

        if self.llm_tracer:
            with self.llm_tracer.trace_llm_call(
                model=self.model_name,
                prompt=user_prompt,
                system_prompt=system_prompt,
                model_params={"temperature": self.temperature},
                phase="code_generation",
                language=language,
            ) as record:
                code = self._execute_llm_call(messages, options, record)
        else:
            code = self._execute_llm_call(messages, options, None)

        if self.debug:
            print(f"\n[DEBUG] Ollama Response:")
            print(f"  Code length: {len(code)} characters")
            print(f"  First 200 chars: {code[:200]}...\n")

        code = self._extract_code(code)

        return code

    def _execute_llm_call(
        self,
        messages: list[dict[str, str]],
        options: dict[str, Any],
        record: Any | None,
    ) -> str:
        """
        Execute LLM call and handle streaming/non-streaming modes.
        
        Args:
            messages: Chat messages
            options: Model options
            record: LLM call record (optional)
            
        Returns:
            Generated code
        """
        try:
            if self.stream:
                code_chunks = []
                print("[STREAM] ", end="", flush=True)
                
                input_tokens = 0
                output_tokens = 0
                
                for chunk in self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    options=options,
                    keep_alive=self.keep_alive,
                    stream=True,
                ):
                    content = chunk.message.content if hasattr(chunk, 'message') else chunk.get("message", {}).get("content", "")
                    if content:
                        print(content, end="", flush=True)
                        code_chunks.append(content)
                    
                    if hasattr(chunk, 'prompt_eval_count'):
                        val = chunk.prompt_eval_count
                        if val is not None:
                            input_tokens = val
                    elif "prompt_eval_count" in chunk:
                        val = chunk.get("prompt_eval_count")
                        if val is not None:
                            input_tokens = val
                    
                    if hasattr(chunk, 'eval_count'):
                        val = chunk.eval_count
                        if val is not None:
                            output_tokens = val
                    elif "eval_count" in chunk:
                        val = chunk.get("eval_count")
                        if val is not None:
                            output_tokens = val
                
                print()
                code = "".join(code_chunks)
                
                if self.debug:
                    print(f"\n[DEBUG] Stream Token Summary:")
                    print(f"  input_tokens: {input_tokens}")
                    print(f"  output_tokens: {output_tokens}")
                
                if self.token_tracker and (input_tokens > 0 or output_tokens > 0):
                    self.token_tracker.record_call(
                        phase="generation",
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        model=self.model_name,
                    )
                
                if record and self.llm_tracer:
                    self.llm_tracer.record_response(record, code, input_tokens, output_tokens)
            else:
                response = self.client.chat(
                    model=self.model_name,
                    messages=messages,
                    options=options,
                    keep_alive=self.keep_alive,
                )
                
                if self.debug:
                    print(f"\n[DEBUG] CodeGenerator Response Type:")
                    print(f"  {type(response)}")
                
                code = response.message.content if hasattr(response, 'message') else response.get("message", {}).get("content", "")
                
                input_tokens_raw = getattr(response, 'prompt_eval_count', None) or response.get("prompt_eval_count")
                output_tokens_raw = getattr(response, 'eval_count', None) or response.get("eval_count")
                
                input_tokens = input_tokens_raw if input_tokens_raw is not None else 0
                output_tokens = output_tokens_raw if output_tokens_raw is not None else 0
                
                if self.debug:
                    print(f"\n[DEBUG] Token Extraction:")
                    print(f"  Has prompt_eval_count attr: {hasattr(response, 'prompt_eval_count')}")
                    print(f"  Has eval_count attr: {hasattr(response, 'eval_count')}")
                    print(f"  input_tokens_raw: {input_tokens_raw}")
                    print(f"  output_tokens_raw: {output_tokens_raw}")
                    print(f"  input_tokens: {input_tokens}")
                    print(f"  output_tokens: {output_tokens}")
                
                if self.token_tracker:
                    self.token_tracker.record_call(
                        phase="generation",
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        model=self.model_name,
                    )
                
                if record and self.llm_tracer:
                    self.llm_tracer.record_response(record, code, input_tokens, output_tokens)
            
            return code
            
        except Exception as e:
            error_msg = f"# Error generating code: {e}"
            if self.debug:
                print(f"\n[DEBUG] Error: {e}\n")
            if record:
                record.error = str(e)
            return error_msg

    def generate_with_iterations(
        self,
        description: str,
        language: str = "python",
        constraints: dict[str, Any] | None = None,
        max_iterations: int = 3,
        quality_threshold: float = 0.8,
    ) -> dict[str, Any]:
        """
        Generate code iteratively with self-evaluation and improvement.

        Args:
            description: Task description
            language: Programming language
            constraints: Optional constraints
            max_iterations: Maximum number of iterations
            quality_threshold: Minimum quality score required

        Returns:
            Generation result with code and metadata
        """
        best_code = None
        best_score = 0.0
        iteration_history = []

        if self.llm_tracer:
            with self.llm_tracer.trace_llm_call(
                model=self.model_name,
                prompt=description,
                model_params={"max_iterations": max_iterations, "quality_threshold": quality_threshold},
                phase="iterative_generation",
                language=language,
            ) as record:
                result = self._execute_iterations(
                    description, language, constraints, max_iterations, quality_threshold,
                    iteration_history
                )
                if record:
                    self.llm_tracer.record_response(
                        record,
                        result.get("code", ""),
                        0,
                        0
                    )
                    record.metadata["iterations"] = result.get("iterations", 0)
                    record.metadata["final_score"] = result.get("final_score", 0)
                return result
        else:
            return self._execute_iterations(
                description, language, constraints, max_iterations, quality_threshold,
                iteration_history
            )

    def _execute_iterations(
        self,
        description: str,
        language: str,
        constraints: dict[str, Any] | None,
        max_iterations: int,
        quality_threshold: float,
        iteration_history: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Execute iterative code generation.
        
        Args:
            description: Task description
            language: Programming language
            constraints: Optional constraints
            max_iterations: Maximum number of iterations
            quality_threshold: Minimum quality score required
            iteration_history: List to store iteration history
            
        Returns:
            Generation result with code and metadata
        """
        best_code = None
        best_score = 0.0
        previous_code = None
        evaluation = None

        for iteration in range(max_iterations):
            if iteration == 0:
                code = self.generate_code(description, language, constraints)
            else:
                code = self._regenerate_with_feedback(
                    description,
                    language,
                    constraints,
                    previous_code,
                    evaluation
                )

            evaluation = self._self_evaluate(code, description, language)

            iteration_history.append({
                "iteration": iteration + 1,
                "quality_score": evaluation.get("quality_score", 0),
                "issues": evaluation.get("issues", []),
            })

            if evaluation.get("quality_score", 0) > best_score:
                best_score = evaluation.get("quality_score", 0)
                best_code = code

            if evaluation.get("quality_score", 0) >= quality_threshold:
                return {
                    "code": code,
                    "iterations": iteration + 1,
                    "final_score": evaluation.get("quality_score", 0),
                    "quality_threshold_met": True,
                    "iteration_history": iteration_history,
                }

            previous_code = code

        return {
            "code": best_code,
            "iterations": max_iterations,
            "final_score": best_score,
            "quality_threshold_met": best_score >= quality_threshold,
            "iteration_history": iteration_history,
        }

    def _self_evaluate(
        self,
        code: str,
        description: str,
        language: str,
    ) -> dict[str, Any]:
        """
        Self-evaluate generated code.

        Args:
            code: Generated code
            description: Task description
            language: Programming language

        Returns:
            Evaluation result with quality score
        """
        scores = {}
        issues = []

        syntax_result = self.validate_syntax(code, language)
        scores["syntax"] = 1.0 if syntax_result.get("valid", False) else 0.0
        if not syntax_result.get("valid", False):
            issues.append(f"Syntax error: {syntax_result.get('message', 'Unknown')}")

        logic_score = self._evaluate_logic(code, description, language)
        scores["logic"] = logic_score
        if logic_score < 0.7:
            issues.append("Logic may not fully address the task")

        style_score = self._evaluate_style(code, language)
        scores["style"] = style_score
        if style_score < 0.7:
            issues.append("Code style could be improved")

        doc_score = self._evaluate_documentation(code, language)
        scores["documentation"] = doc_score
        if doc_score < 0.5:
            issues.append("Insufficient documentation")

        weights = {
            "syntax": 0.3,
            "logic": 0.4,
            "style": 0.15,
            "documentation": 0.15,
        }

        quality_score = sum(
            scores[key] * weights[key] for key in scores
        )

        return {
            "quality_score": round(quality_score, 2),
            "scores": scores,
            "issues": issues,
        }

    def _evaluate_logic(
        self,
        code: str,
        description: str,
        language: str,
    ) -> float:
        """Evaluate if code logic addresses the task."""
        score = 0.5

        description_lower = description.lower()
        code_lower = code.lower()

        keywords = {
            "web": ["app", "route", "get", "post", "fastapi", "flask"],
            "api": ["api", "endpoint", "request", "response"],
            "database": ["database", "db", "query", "model"],
            "auth": ["auth", "login", "password", "token"],
            "test": ["test", "assert", "unittest"],
        }

        for category, kws in keywords.items():
            if category in description_lower:
                if any(kw in code_lower for kw in kws):
                    score += 0.1

        if "def " in code or "function " in code:
            score += 0.1
        if "class " in code:
            score += 0.1

        return min(score, 1.0)

    def _evaluate_style(self, code: str, language: str) -> float:
        """Evaluate code style."""
        score = 0.5

        lines = code.split("\n")
        if not lines:
            return 0.0

        avg_line_length = sum(len(line) for line in lines) / len(lines)
        if avg_line_length < 100:
            score += 0.2

        if "    " in code or "\t" in code:
            score += 0.1

        if any(line.strip().startswith("#") or '"""' in line or "'''" in line for line in lines):
            score += 0.1

        if language == "python":
            try:
                import ast
                ast.parse(code)
                score += 0.1
            except:
                pass

        return min(score, 1.0)

    def _evaluate_documentation(self, code: str, language: str) -> float:
        """Evaluate code documentation."""
        score = 0.0

        if '"""' in code or "'''" in code:
            score += 0.4
        if "#" in code:
            score += 0.2

        if language == "python":
            import ast
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                        if ast.get_docstring(node):
                            score += 0.1
            except:
                pass

        return min(score, 1.0)

    def _regenerate_with_feedback(
        self,
        description: str,
        language: str,
        constraints: dict[str, Any] | None,
        previous_code: str,
        evaluation: dict[str, Any],
    ) -> str:
        """
        Regenerate code with feedback from evaluation.

        Args:
            description: Task description
            language: Programming language
            constraints: Optional constraints
            previous_code: Previously generated code
            evaluation: Evaluation result

        Returns:
            Improved code
        """
        issues = evaluation.get("issues", [])
        scores = evaluation.get("scores", {})

        feedback_parts = []
        if scores.get("syntax", 1.0) < 1.0:
            feedback_parts.append("Fix syntax errors")
        if scores.get("logic", 0) < 0.7:
            feedback_parts.append("Improve logic to better address the task")
        if scores.get("style", 0) < 0.7:
            feedback_parts.append("Improve code style and formatting")
        if scores.get("documentation", 0) < 0.5:
            feedback_parts.append("Add more documentation and comments")

        feedback = "Previous issues: " + ", ".join(feedback_parts) if feedback_parts else ""

        enhanced_constraints = constraints or {}
        enhanced_constraints["feedback"] = feedback
        enhanced_constraints["previous_code"] = previous_code

        return self.generate_code(description, language, enhanced_constraints)

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

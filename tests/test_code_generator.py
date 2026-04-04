"""
Tests for CodeGenerator.
"""

import pytest

from cinder_cli.config import Config
from cinder_cli.executor import CodeGenerator


@pytest.fixture
def generator():
    """Create a code generator instance."""
    config = Config()
    config.set("model", "qwen3.5:9b")
    config.set("temperature", 0.2)
    return CodeGenerator(config)


class TestCodeGenerator:
    """Test cases for CodeGenerator."""

    def test_extract_code_from_markdown(self, generator):
        """Test code extraction from markdown."""
        markdown = """
Here's the code:

```python
def hello():
    print("Hello, World!")
```

That's it!
"""
        code = generator._extract_code(markdown)
        assert 'def hello():' in code
        assert 'print("Hello, World!")' in code
        assert "```" not in code

    def test_extract_code_plain(self, generator):
        """Test code extraction from plain text."""
        plain = """def hello():
    print("Hello, World!")
"""
        code = generator._extract_code(plain)
        assert code == plain

    def test_build_system_prompt(self, generator):
        """Test system prompt building."""
        prompt = generator._build_system_prompt("python", {"framework": "fastapi"})
        
        assert "python" in prompt.lower()
        assert "fastapi" in prompt.lower()

    def test_build_user_prompt(self, generator):
        """Test user prompt building."""
        prompt = generator._build_user_prompt("创建一个函数", "python")
        
        assert "创建一个函数" in prompt
        assert "python" in prompt.lower()

"""
Invitation code loader.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from cinder_cli.config import Config
from cinder_cli.database.models import InvitationCode


class InvitationLoader:
    """Loads invitation codes from configuration file."""
    
    def __init__(self, config_path: Path | None = None):
        if config_path is None:
            config = Config()
            config_path = Path(config.get("invitations_path", "~/.cinder/invitations.yaml")).expanduser()
        
        self.config_path = config_path
    
    def load_codes(self) -> list[InvitationCode]:
        """Load invitation codes from configuration file."""
        if not self.config_path.exists():
            return []
        
        with open(self.config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        codes = []
        for item in data.get("codes", []):
            code = InvitationCode(
                code=item["code"],
                is_single_use=item.get("is_single_use", True),
                used_count=0,
                max_uses=item.get("max_uses"),
                created_at="",
                is_active=item.get("is_active", True),
            )
            codes.append(code)
        
        return codes
    
    def get_code_by_value(self, code_value: str) -> InvitationCode | None:
        """Get invitation code by value."""
        codes = self.load_codes()
        for code in codes:
            if code.code == code_value:
                return code
        return None

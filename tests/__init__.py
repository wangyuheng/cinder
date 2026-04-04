"""
Tests for cinder_cli package.
"""

import pytest


def test_import():
    """Test that the package can be imported."""
    import cinder_cli
    assert cinder_cli.__version__ == "2.0.0"


def test_import_modules():
    """Test that all modules can be imported."""
    from cinder_cli import cli
    from cinder_cli import config
    from cinder_cli import database
    from cinder_cli import question_guide
    from cinder_cli import soul_presenter
    from cinder_cli import chat_handler
    from cinder_cli import proxy_decision
    from cinder_cli import decision_logger
    from cinder_cli import dimension_explainer
    from cinder_cli import soul_adjuster
    from cinder_cli import decision_reviewer

    assert cli is not None
    assert config is not None
    assert database is not None

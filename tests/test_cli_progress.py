"""
Tests for responsive and color-aware progress displays.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from cinder_cli.cli_responsive_progress import ResponsiveProgressDisplay
from cinder_cli.cli_color_aware_progress import ColorAwareProgressDisplay


def test_responsive_progress_compact_mode():
    """Test responsive progress in compact mode."""
    display = ResponsiveProgressDisplay()
    
    with patch.object(display, '_get_terminal_width', return_value=70):
        with patch.object(display, '_is_compact_mode', return_value=True):
            progress = display.create_progress()
            assert progress is not None


def test_responsive_progress_full_mode():
    """Test responsive progress in full mode."""
    display = ResponsiveProgressDisplay()
    
    with patch.object(display, '_get_terminal_width', return_value=100):
        with patch.object(display, '_is_compact_mode', return_value=False):
            progress = display.create_progress()
            assert progress is not None


def test_responsive_progress_minimal_mode():
    """Test responsive progress in minimal mode."""
    display = ResponsiveProgressDisplay()
    
    with patch.object(display, '_get_terminal_width', return_value=50):
        progress = display.create_progress()
        assert progress is not None


def test_color_aware_progress_with_color():
    """Test color-aware progress with color support."""
    console = Mock()
    console.color_system = "truecolor"
    
    display = ColorAwareProgressDisplay(console=console)
    
    assert display._supports_color() is True
    
    progress = display.create_progress()
    assert progress is not None


def test_color_aware_progress_without_color():
    """Test color-aware progress without color support."""
    console = Mock()
    console.color_system = None
    
    display = ColorAwareProgressDisplay(console=console)
    
    assert display._supports_color() is False
    
    progress = display.create_progress()
    assert progress is not None


def test_color_aware_progress_force_color():
    """Test color-aware progress with forced color."""
    console = Mock()
    console.color_system = None
    
    display = ColorAwareProgressDisplay(console=console, force_color=True)
    
    assert display._supports_color() is True


def test_color_aware_status_symbols():
    """Test status symbols in color-aware mode."""
    console = Mock()
    console.color_system = "truecolor"
    
    display = ColorAwareProgressDisplay(console=console)
    
    success_symbol = display._get_status_symbol("success")
    assert "[green]" in success_symbol
    
    error_symbol = display._get_status_symbol("error")
    assert "[red]" in error_symbol


def test_color_aware_status_symbols_no_color():
    """Test status symbols without color."""
    console = Mock()
    console.color_system = None
    
    display = ColorAwareProgressDisplay(console=console)
    
    success_symbol = display._get_status_symbol("success")
    assert "[OK]" in success_symbol
    
    error_symbol = display._get_status_symbol("error")
    assert "[ERR]" in error_symbol


def test_responsive_phase_summary_compact():
    """Test phase summary in compact mode."""
    console = Mock()
    display = ResponsiveProgressDisplay(console=console)
    
    with patch.object(display, '_is_compact_mode', return_value=True):
        display.display_phase_summary("PLAN", duration=15.5, tasks_completed=3)
        
        console.print.assert_called_once()
        call_arg = console.print.call_args[0][0]
        assert "PLAN" in call_arg
        assert "15.1s" in call_arg


def test_color_aware_phase_summary():
    """Test phase summary in color-aware mode."""
    console = Mock()
    console.color_system = "truecolor"
    
    display = ColorAwareProgressDisplay(console=console)
    
    display.display_phase_summary("PLAN", duration=15.5, tasks_completed=3)
    
    console.print.assert_called_once()
    call_arg = console.print.call_args[0][0]
    assert "PLAN" in call_arg

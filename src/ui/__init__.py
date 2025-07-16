"""
UI System for Daydreamer Project

This package contains the user interface components for the Daydreamer simulation system,
including web dashboard and CLI interfaces.
"""

from .web_dashboard import WebDashboard
from .cli_interface import CLIInterface

__all__ = ['WebDashboard', 'CLIInterface']
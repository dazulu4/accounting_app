"""
Configuration package for enterprise settings

This package contains all configuration-related modules including
environment variables, database settings, and application configuration.
"""

from .environment import AppSettings, settings

__all__ = ["settings", "AppSettings"]

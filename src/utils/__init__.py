# -*- coding: utf-8 -*-
"""
Package utilitaires pour JARVIS
"""

from .system_utils import (
    SystemDetector, 
    SystemType, 
    system_detector,
    get_system_type,
    is_windows,
    is_macos,
    is_linux,
    adapt_command,
    check_program_available
)

__all__ = [
    'SystemDetector',
    'SystemType', 
    'system_detector',
    'get_system_type',
    'is_windows',
    'is_macos',
    'is_linux',
    'adapt_command',
    'check_program_available'
]
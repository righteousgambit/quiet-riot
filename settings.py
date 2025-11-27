#!/usr/bin/env python3
"""
Backward compatibility module for settings.
This module provides compatibility with existing code that imports settings.
New code should use config.get_config() instead.
"""

from quiet_riot import config

# Get config singleton
_cfg = config.get_config()

# Initialize module-level variables
scan_objects = []
account_no = None


def init(session):
    """
    Initialize settings (backward compatibility).

    Args:
        session: Boto3 session object
    """
    _cfg.init(session)
    # Update module-level variables for backward compatibility
    global scan_objects, account_no
    scan_objects = _cfg.scan_objects
    account_no = _cfg.account_no


# Make them accessible via __getattr__ for dynamic access
def __getattr__(name):
    """Dynamic attribute access for backward compatibility."""
    if name == "scan_objects":
        return _cfg.scan_objects
    elif name == "account_no":
        return _cfg.account_no
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

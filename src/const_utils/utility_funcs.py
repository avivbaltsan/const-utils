"""Constant-related utility functions"""

import inspect
from typing import Any, Dict


def is_const(name: str) -> bool:
    """Assures the canonical naming rules for constants within
    this package:
        * The constant name must be completely in uppercase;
        * The constant name must *not* begin with an underscore character;
        * And trivially, the constant name must be a valid Python variable name.
    """
    return name.isidentifier() and name.isupper() and not name.startswith('_')


def access_namespace_consts(local=False) -> Dict[str, Any]:
    """Access all constants within the caller namespace.
    A constant is any attribute name for which `is_const()`
    is True.

    If `local` is True, constants are scanned over `locals()`
    instead of `globals()`.
    """
    current_frame = inspect.currentframe()
    if current_frame is None:
        raise RuntimeError('Cannot retrieve current frame')

    caller_frame = current_frame.f_back
    namespace = caller_frame.f_locals if local else caller_frame.f_globals

    return {name: value for name, value in namespace.items() if is_const(name)}

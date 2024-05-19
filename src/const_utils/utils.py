"""Project utilities"""


def is_const(name: str) -> bool:
    """Assures the canonical naming rules for constants within
    this package:
        * The constant name must be completely in uppercase;
        * The constant name must *not* begin with an underscore character;
        * And trivially, the constant name must be a valid Python variable name.
    """
    return name.isidentifier() and name.isupper() and not name.startswith('_')

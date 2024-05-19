"""Definition of 'Const Classes'"""
import importlib
import inspect
from typing import Dict

from src.const_utils.utils import is_const


class ConstClassMeta(type):
    """Metaclass that allows for the creation of a
    `ConstClass`: a class with added utilities
    for handling class-attribute constants.

    Example:
        >>> class MathConsts(metaclass=ConstClassMeta):
        ...     PI = 3.14159
        ...     E = 2.71828
        ...     NA = 6.0221408e+23
        >>>
        >>>
        >>> MathConsts['PI']  # returns 3.14159
        >>> MathConsts.as_dict()  # returns {'PI': 3.14159, 'E': 2.71828, 'NA': 6.022...}
        >>> MathConsts.apply()  # Apply the constants to the global namespace_callable

    For standard creation of Const Classes,
    using `BaseConstClass` is preferred.
    """

    _class_constant_cache: Dict[object, set] = {}

    def __new__(cls, *args, **kwargs):
        """Register an instance of the metaclass and its
        constant attributes to the class constant cache.
        """
        const_class = super().__new__(cls, *args, **kwargs)
        constants = {name for name in dir(const_class) if is_const(name)}
        cls._class_constant_cache[const_class] = constants
        return const_class

    def __getitem__(cls, item):
        """Utility for accessing constant value by its name."""
        class_constants = ConstClassMeta._class_constant_cache[cls]
        if item in class_constants:
            return getattr(cls, item)
        else:
            available = ', '.join(class_constants)
            raise ValueError(f'Class {cls.__name__} does not '
                             f'contain a constant named {item}. '
                             f'Existing constants are {available}')

    def __setattr__(cls, name, value):
        """Hook the creation of a new class attribute by
        checking if the newly created attribute is a constant,
        and if so adding it to the class constant cache.

        If a class attribute is changed to a non-constant
        value, remove the attribute name from the class
        cache.
        """
        super().__setattr__(name, value)
        class_constants = ConstClassMeta._class_constant_cache[cls]

        if is_const(name) and name not in class_constants:
            class_constants.add(name)

    def __delattr__(cls, name):
        """Hook the deletion of a class attribute by
        checking if the deleted attribute is a constant,
        and if so remove it from the class constant cache.
        """
        super().__delattr__(name)
        class_constants = ConstClassMeta._class_constant_cache[cls]
        if name in class_constants:
            class_constants.remove(name)

    def as_dict(cls):
        """Return a dictionary representation of the
        constants within the class.
        """
        class_constants = ConstClassMeta._class_constant_cache[cls]
        return {const_name: getattr(cls, const_name) for const_name in class_constants}

    @property
    def const_names(cls):
        """Return a list of all constant names"""
        return list(cls.as_dict())

    @property
    def const_values(cls):
        """Return a list of all constant values"""
        return list(cls.as_dict().values())

    def __apply(cls, namespace, override, f_assign):
        for name in ConstClassMeta._class_constant_cache[cls]:
            value = getattr(cls, name)
            if not override and hasattr(namespace, name):
                continue
            f_assign(name, value)

    def apply_to_module(cls, module_name, override=False):
        """Save the constants defined under the class
        to the given module (notated by its name),
        represented as string. To alter the current module,
        use `__name__`. If `override` is set to `True`,
        override already existing attributes within the
        given module name.
        """
        module = importlib.import_module(module_name)
        cls.__apply(module, override, module.__setattr__)

    def apply(cls, local=False, override=False):
        """Save the constants defined under the class
        to the global namespace of the scope from
        which this method is called.

        If `local` is set to `True`, the values are
        saved to the local namespace_callable instead of the
        global. If `override` is set to `True`,
        constants defined under this class that have
        names that already exist as attributes of
        the calling namespace_callable will override the
        existing attributes.
        """
        current_frame = inspect.currentframe()
        if current_frame is None:
            raise RuntimeError('Cannot retrieve current frame')

        caller_frame = current_frame.f_back
        if local:
            namespace = caller_frame.f_locals
        else:
            namespace = caller_frame.f_globals

        cls.__apply(namespace, override, namespace.__setitem__)


class BaseConstClass(metaclass=ConstClassMeta):
    """Helper class that provides a standard way
    to create a Constant Class using inheritance.
    """
    pass


__all__ = ['ConstClassMeta', 'BaseConstClass']

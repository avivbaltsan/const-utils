import sys
import types

import pytest

from src.const_utils.const_class import ConstClassMeta


@pytest.fixture
def sample_const_class():
    class MathConsts(metaclass=ConstClassMeta):
        PI = 3.14159
        E = 2.71828
        NA = 6.0221408e+23
    return MathConsts


@pytest.fixture
def custom_identifier_const_class():
    def custom_identifier(s: str) -> bool:
        return s.isidentifier() and s.islower() and not s.startswith('_')

    class MathConstsLowercase(metaclass=ConstClassMeta, constant_identifier=custom_identifier):
        pi = 3.14159
        e = 2.71828
        na = 6.0221408e+23

    return MathConstsLowercase


@pytest.fixture
def sample_const_class2():
    class PythonKeywords(metaclass=ConstClassMeta):
        FUNC_DEFINITION = 'def'
        CLASS_DEFINITION = 'class'
        IF_STATEMENT = 'if'
    return PythonKeywords


@pytest.fixture
def fake_module():
    name = 'fake_module'
    module = types.ModuleType(name)
    sys.modules[name] = module

    yield module

    del sys.modules[name]


def test_const_class_cache(sample_const_class, sample_const_class2):
    expected_cache = {
        sample_const_class: {'PI', 'E', 'NA'},
        sample_const_class2: {'FUNC_DEFINITION', 'CLASS_DEFINITION', 'IF_STATEMENT'}
    }
    assert ConstClassMeta._class_constant_cache[sample_const_class] == expected_cache[sample_const_class]
    assert ConstClassMeta._class_constant_cache[sample_const_class2] == expected_cache[sample_const_class2]


def test_cache_with_custom_constant_identifier(custom_identifier_const_class):
    expected_dict = {
        'pi': 3.14159,
        'e': 2.71828,
        'na': 6.0221408e+23,
    }
    assert custom_identifier_const_class.as_dict() == expected_dict


def test_as_dict(sample_const_class):
    expected_dict = {
        'PI': 3.14159,
        'E': 2.71828,
        'NA': 6.0221408e+23
    }
    assert sample_const_class.as_dict() == expected_dict


def test_deleting_constant(sample_const_class):
    del sample_const_class.PI
    assert 'PI' not in ConstClassMeta._class_constant_cache[sample_const_class]


def test_setting_constant(sample_const_class):
    sample_const_class.ZERO = 0
    assert 'ZERO' in ConstClassMeta._class_constant_cache[sample_const_class]


def test_applying_to_module(sample_const_class, fake_module):
    # Override a single value to test `override`
    setattr(fake_module, 'PI', 0)

    sample_const_class.apply_to_module('fake_module', override=True)

    const_class_namespace = sample_const_class.as_dict().items()
    module_namespace = vars(fake_module).items()

    assert all(item in module_namespace for item in const_class_namespace)


@pytest.mark.parametrize('is_local', [
    True,
    False
])
def test_applying_to_current_namespace(is_local, sample_const_class):
    f_namespace = locals if is_local else globals

    def inner_scope():
        # Override a single value to test `override` argument
        f_namespace().update({'PI': None})
        # Update global/local namespace
        sample_const_class.apply(is_local, override=True)
        return f_namespace()

    updated_namespace = inner_scope()
    all(item in updated_namespace for item in sample_const_class.as_dict())

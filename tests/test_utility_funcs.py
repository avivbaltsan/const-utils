import pytest

from src.const_utils.utility_funcs import access_namespace_consts, is_const


@pytest.fixture
def new_globals():
    added_globals = {'G1': 1, 'G2': 2}
    globals().update(added_globals)

    yield added_globals

    globals().pop('G1')
    globals().pop('G2')


@pytest.mark.parametrize('const_name,expected', [
    ('23po ij', False),
    ('3hello', False),
    ('3HELLO', False),
    ('HELLO3', True),
    ('HELLO_THERE', True),
    ('Hello_There', False)
])
def test_is_const(const_name, expected):
    assert is_const(const_name) == expected


def test_access_namespace_consts_global(new_globals):
    assert access_namespace_consts() == new_globals


def test_access_namespace_consts_local():
    new_locals = {'L1': 1, 'L2': 2}
    locals().update(new_locals)
    assert access_namespace_consts(local=True) == new_locals

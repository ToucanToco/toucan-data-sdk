import sys
import textwrap
import types

import pandas as pd
import pytest

from toucan_data_sdk.utils.helpers import (
    clean_cachedir_old_entries,
    get_func_sourcecode,
    get_param_value_from_func_call,
    get_temp_column_name,
)


def test_get_temp_column_name():
    df = pd.DataFrame({"__tmp__": ["a, b"]})
    assert get_temp_column_name(df) == "__tmp___"


def test_get_param_value_from_func_call():
    def foo(a, b, c=3, d=4, *args, **kwargs):
        pass

    args = [1]
    kwargs = {"b": 2, "d": 44, "e": 55}
    expected = {"a": 1, "b": 2, "c": 3, "d": 44, "kwargs": {"e": 55}}
    for k, v in expected.items():
        assert get_param_value_from_func_call(k, foo, args, kwargs) == v

    with pytest.raises(TypeError):
        get_param_value_from_func_call("e", foo, args, kwargs)

    def bar(*, a, b=None):
        pass

    args = []
    kwargs = {"a": 1}
    expected = {"a": 1, "b": None}
    for k, v in expected.items():
        assert get_param_value_from_func_call(k, bar, args, kwargs) == v


def test_get_func_sourcecode(mocker):
    module_name = "plop"
    module_dir = "plopdir"
    new_module = types.ModuleType(module_name)
    new_module.__file__ = "plopdir/plop.py"
    new_module.__path__ = [module_dir]
    sys.path.append(module_dir)
    sys.modules[module_name] = new_module
    code = textwrap.dedent(
        """
    def foo():
        return 1

    def get_answer():
        return 42
    """
    ).lstrip()
    exec(code, new_module.__dict__)

    mocker.patch("inspect.getsource").side_effect = ZeroDivisionError
    mocker.patch("linecache.getlines").return_value = code.splitlines(keepends=True)

    func_code = get_func_sourcecode(new_module.get_answer)
    assert func_code.strip().endswith("return 42")


def test_clean_cachedir_old_entries():
    with pytest.raises(ValueError):
        clean_cachedir_old_entries(cachedir=None, func_name="", limit=0)

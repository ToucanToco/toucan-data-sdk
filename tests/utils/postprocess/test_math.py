import pandas as pd
import pytest

from toucan_data_sdk.utils.postprocess import (
    add, subtract, multiply, divide, formula
)
from toucan_data_sdk.utils.postprocess.math import FormulaError


def test_math_operations_with_column():
    """ It should return result for basic math operations with a column name"""
    data = pd.DataFrame([{'value1': 10, 'value2': 20},
                         {'value1': 17, 'value2': 5}])
    kwargs = {'new_column': 'result', 'column_1': 'value1', 'column_2': 'value2'}

    res = add(data, **kwargs)
    expected_col = [30, 22]
    assert res['result'].tolist() == expected_col

    res = subtract(data, **kwargs)
    expected_col = [-10, 12]
    assert res['result'].tolist() == expected_col

    res = multiply(data, **kwargs)
    expected_col = [200, 85]
    assert res['result'].tolist() == expected_col

    res = divide(data, **kwargs)
    expected_col = [.5, 3.4]
    assert res['result'].tolist() == expected_col


def test_math_operations_with_number():
    """ It should return result for basic math operations with a constant number"""
    data = pd.DataFrame([{'value1': 10}, {'value1': 17}])
    kwargs = {'new_column': 'value1', 'column_1': 'value1', 'column_2': .25}

    res = add(data.copy(), **kwargs)
    expected_col = [10.25, 17.25]
    assert res['value1'].tolist() == expected_col

    res = subtract(data.copy(), **kwargs)
    expected_col = [9.75, 16.75]
    assert res['value1'].tolist() == expected_col

    res = multiply(data.copy(), **kwargs)
    expected_col = [2.5, 4.25]
    assert res['value1'].tolist() == expected_col

    res = divide(data.copy(), **kwargs)
    expected_col = [40.0, 68.0]
    assert res['value1'].tolist() == expected_col

    data = pd.DataFrame([{'value1': 10}, {'value1': 25}])
    kwargs = {'new_column': 'result', 'column_1': 2, 'column_2': 'value1'}

    res = add(data.copy(), **kwargs)
    expected_col = [12, 27]
    assert res['result'].tolist() == expected_col

    res = divide(data.copy(), **kwargs)
    expected_col = [.2, .08]
    assert res['result'].tolist() == expected_col


def test_bad_arg():
    """ It should raise an error when calling a math operation with a bad parameter """
    data = pd.DataFrame([{'value1': 10}, {'value1': 17}])
    kwargs = {'new_column': 'value1', 'column_1': 'value1', 'column_2': [1, 2]}

    with pytest.raises(TypeError) as exc_info:
        add(data.copy(), **kwargs)
    assert str(exc_info.value) == 'column_2 must be a string, an integer or a float'

    data = pd.DataFrame([{'value1': 10}, {'value1': 17}])
    kwargs = {'new_column': 'value1', 'column_1': {'bad': 'type'}, 'column_2': 'value1'}

    with pytest.raises(TypeError) as exc_info:
        divide(data.copy(), **kwargs)
    assert str(exc_info.value) == 'column_1 must be a string, an integer or a float'


def test_formula():
    df = pd.DataFrame({'a': [1, 3], 'b': [2, 4], 'other col': [3, 5],
                       'yet another1': [2, 2]})

    with pytest.raises(FormulaError) as exc_info:
        formula(df, new_column='c', formula='a, + b')
    assert str(exc_info.value) == '"a," is not valid. Allowed entries are numbers, ' \
                                  'column names and math symbols ' \
                                  '(among "(", ")", "+", "-", "/", "*", "%", ".")'

    with pytest.raises(FormulaError) as exc_info:
        formula(df, new_column='c', formula='import ipdb')
    assert str(exc_info.value) == '"import ipdb" is not a valid column name'

    res = formula(df, new_column='c', formula='a + b')
    assert res['c'].tolist() == [3, 7]

    res = formula(df, new_column='c', formula='.5*a - b')
    assert res['c'].tolist() == [-1.5, -2.5]

    res = formula(df, new_column='c', formula='a + other col')
    assert res['c'].tolist() == [4, 8]

    res = formula(df, new_column='c', formula='a + other col / 2')
    assert res['c'].tolist() == [2.5, 5.5]

    res = formula(df, new_column='c', formula='a + other col // 2')
    assert res['c'].tolist() == [2, 5]

    res = formula(df, new_column='c', formula='(a + other col)/  2.')
    assert res['c'].tolist() == [2, 4]

    res = formula(df, new_column='c', formula='(a + b ) % 3')
    assert res['c'].tolist() == [0, 1]

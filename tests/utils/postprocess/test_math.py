from functools import partial

import pandas as pd
import pytest

from toucan_data_sdk.utils.postprocess import (
    absolute_values,
    add,
    divide,
    formula,
    multiply,
    round_values,
    subtract,
)
from toucan_data_sdk.utils.postprocess.math import (
    DEPRECATED_COLUMN_QUOTE_CHARS,
    LOGGER,
    FormulaError,
    Token,
    _parse_formula,
    get_new_syntax_formula,
)


def test_math_operations_with_column():
    """ It should return result for basic math operations with a column name"""
    data = pd.DataFrame([{'value1': 10, 'value2': 20}, {'value1': 17, 'value2': 5}])
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
    expected_col = [0.5, 3.4]
    assert res['result'].tolist() == expected_col


def test_math_operations_with_number():
    """ It should return result for basic math operations with a constant number"""
    data = pd.DataFrame([{'value1': 10}, {'value1': 17}])
    kwargs = {'new_column': 'value1', 'column_1': 'value1', 'column_2': 0.25}

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
    expected_col = [0.2, 0.08]
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


def test_token():
    t = Token('    ')
    assert len(t) == 0
    assert repr(t) == "''"
    assert t == ''
    assert t.get_text() == ''
    t1 = Token(' a ', quoted=True)
    assert t1.get_text() == '`a`'
    t2 = Token('a')
    assert t1 == t2


# DEPRECATED: OLD SYNTAX
def test_old_parse_formula():
    old_parse_formula = partial(_parse_formula, quote_chars=DEPRECATED_COLUMN_QUOTE_CHARS)
    assert old_parse_formula('a') == ['a']
    assert old_parse_formula('a+b') == ['a', '+', 'b']
    assert old_parse_formula('pika + chuuu') == ['pika', '+', 'chuuu']
    assert old_parse_formula('pika + (chuuu/10)') == ['pika', '+', '(', 'chuuu', '/', '10', ')']
    assert old_parse_formula('pika + (chu uu/10)') == ['pika', '+', '(', 'chu uu', '/', '10', ')']
    assert old_parse_formula('pika + (chu_uu/10)') == ['pika', '+', '(', 'chu_uu', '/', '10', ')']
    assert old_parse_formula('pika + ("chu-uu"/10)') == ['pika', '+', '(', 'chu-uu', '/', '10', ')']
    assert old_parse_formula('a + b*3.1') == ['a', '+', 'b', '*', '3', '.', '1']
    assert old_parse_formula('a + "b*3.1"') == ['a', '+', 'b*3.1']
    assert old_parse_formula('("and-another" - yet_another) / (and - another)') == [
        '(',
        'and-another',
        '-',
        'yet_another',
        ')',
        '/',
        '(',
        'and',
        '-',
        'another',
        ')',
    ]
    assert old_parse_formula("pika + ('chu-uu'/10)") == ['pika', '+', '(', 'chu-uu', '/', '10', ')']
    assert old_parse_formula('pika + (\'chu-uu\'/10)') == [  # noqa: Q0
        'pika',
        '+',
        '(',
        'chu-uu',
        '/',
        '10',
        ')',
    ]
    assert old_parse_formula("pika + (\"chu-uu\"/10)") == [  # noqa: Q0
        'pika',
        '+',
        '(',
        'chu-uu',
        '/',
        '10',
        ')',
    ]
    with pytest.raises(FormulaError) as e:
        old_parse_formula('pika + ("chu-uu/10)')
    assert str(e.value) == 'Missing closing quote in formula'


def test_get_new_syntax_formula():
    assert get_new_syntax_formula('a') == '`a`'
    assert get_new_syntax_formula('a+b') == '`a`+`b`'
    assert get_new_syntax_formula('pika + chuuu') == '`pika`+`chuuu`'
    assert get_new_syntax_formula('pika + (chuuu/10)') == '`pika`+(`chuuu`/10)'
    assert get_new_syntax_formula('pika + (chu_uu/10)') == '`pika`+(`chu_uu`/10)'
    assert get_new_syntax_formula('pika + ("chu-uu"/10)') == '`pika`+(`chu-uu`/10)'
    assert get_new_syntax_formula('a + b*3.1') == '`a`+`b`*3.1'
    assert get_new_syntax_formula('a + "b*3.1"') == '`a`+`b*3.1`'
    old = '("and-another" - yet_another) / (and - another)'
    assert get_new_syntax_formula(old) == '(`and-another`-`yet_another`)/(`and`-`another`)'
    assert get_new_syntax_formula("pika + ('chu-uu'/10)") == '`pika`+(`chu-uu`/10)'
    assert get_new_syntax_formula('pika + (\'chu-uu\'/10)') == '`pika`+(`chu-uu`/10)'  # noqa: Q0
    assert get_new_syntax_formula("pika + (\"chu-uu\"/10)") == '`pika`+(`chu-uu`/10)'  # noqa: Q0


# DEPRECATED: OLD SYNTAX
def test_formula_old_syntax(mocker):
    df = pd.DataFrame(
        {
            'a': [1, 3],
            'b': [2, 4],
            'other col': [3, 5],
            'yet_another': [2, 2],
            'and-another': [2, 2],
        }
    )

    with pytest.raises(FormulaError) as exc_info:
        formula(df, new_column='c', formula='a, + b')
    assert str(exc_info.value) == '"a," is not a valid column name'

    with pytest.raises(FormulaError) as exc_info:
        formula(df, new_column='c', formula='import ipdb')
    assert str(exc_info.value) == '"import ipdb" is not a valid column name'

    log_warning = mocker.patch.object(LOGGER, 'warning')
    res = formula(df, new_column='c', formula='a + b')
    assert res['c'].tolist() == [3, 7]
    log_warning.assert_called_once_with(
        "DEPRECATED: You should always use ` for your columns. Old syntax: 'a + b', new syntax: '`a`+`b`'"
    )

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

    res = formula(df, new_column='c', formula='yet_another + b')
    assert res['c'].tolist() == [4, 6]

    res = formula(df, new_column='c', formula='(yet_another + b ) % 3')
    assert res['c'].tolist() == [1, 0]

    with pytest.raises(FormulaError):
        formula(df, new_column='c', formula='and-another - yet_another')

    res = formula(df, new_column='c', formula='"and-another" - yet_another')
    assert res['c'].tolist() == [0, 0]


def test_formula():
    df = pd.DataFrame(
        {
            'a': [1, 3],
            'b': [2, 4],
            'other col': [3, 5],
            'yet_another': [2, 2],
            'and-another': [2, 2],
        }
    )

    with pytest.raises(FormulaError) as exc_info:
        formula(df, new_column='c', formula='`a,` + `b`')
    assert str(exc_info.value) == '"a," is not a valid column name'

    with pytest.raises(FormulaError) as exc_info:
        formula(df, new_column='c', formula='`import ipdb`')
    assert str(exc_info.value) == '"import ipdb" is not a valid column name'

    res = formula(df, new_column='c', formula='`a` + `b`')
    assert res['c'].tolist() == [3, 7]

    res = formula(df, new_column='c', formula='.5*`a` - `b`')
    assert res['c'].tolist() == [-1.5, -2.5]

    res = formula(df, new_column='c', formula='`a` + `other col`')
    assert res['c'].tolist() == [4, 8]

    res = formula(df, new_column='c', formula='`a` + `other col` / 2')
    assert res['c'].tolist() == [2.5, 5.5]

    res = formula(df, new_column='c', formula='`a` + `other col` // 2')
    assert res['c'].tolist() == [2, 5]

    res = formula(df, new_column='c', formula='(`a` + `other col`)/  2.')
    assert res['c'].tolist() == [2, 4]

    res = formula(df, new_column='c', formula='(`a` + `b` ) % 3')
    assert res['c'].tolist() == [0, 1]

    res = formula(df, new_column='c', formula='`yet_another` + `b`')
    assert res['c'].tolist() == [4, 6]

    res = formula(df, new_column='c', formula='(`yet_another` + `b` ) % 3')
    assert res['c'].tolist() == [1, 0]

    with pytest.raises(FormulaError):
        formula(df, new_column='c', formula='`and`-`another` - `yet_another`')

    res = formula(df, new_column='c', formula='`and-another` - `yet_another`')
    assert res['c'].tolist() == [0, 0]


def test_formula_number_columns():
    df = pd.DataFrame({'2017': [3, 2], '2018': [8, -1]})

    res = formula(df, new_column='evo', formula='2018 - 2017')
    assert res['evo'].tolist() == [1, 1]

    # DEPRECATED: OLD SYNTAX
    res = formula(df, new_column='evo', formula='"2018" - "2017"')
    assert res['evo'].tolist() == [5, -3]

    res = formula(df, new_column='evo', formula='`2018` - `2017`')
    assert res['evo'].tolist() == [5, -3]


# ~~ round_values & absolute_values ~~~
data = pd.DataFrame(
    [
        {'ENTITY': 'A', 'VALUE_1': -1.563, 'VALUE_2': -1.563},
        {'ENTITY': 'A', 'VALUE_1': 0.423, 'VALUE_2': 0.423},
        {'ENTITY': 'A', 'VALUE_1': 0, 'VALUE_2': 0},
        {'ENTITY': 'A', 'VALUE_1': -1.612, 'VALUE_2': 1.612},
    ]
)


def test_round_values():
    df = round_values(data.copy(), column='VALUE_1', decimals=1)
    assert df['VALUE_1'].tolist() == [-1.6, 0.4, 0, -1.6]


def test_absolute_values():
    df = absolute_values(data.copy(), column='VALUE_1')
    assert df['VALUE_1'].tolist() == [1.563, 0.423, 0, 1.612]

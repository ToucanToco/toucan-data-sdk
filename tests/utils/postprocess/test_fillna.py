import pandas as pd
from numpy import nan, isnan
import pytest

from toucan_data_sdk.utils.postprocess import fillna


def test_fillna():
    """ It should return result for fillna """
    data = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014,
         'value': 300},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015,
         'value': nan},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016,
         'value': 450}
    ])

    # with column already in data.columns
    kwargs = {
        'column': 'value',
        'value': 0
    }
    res = fillna(data.copy(), **kwargs)
    assert res['value'][1] == 0

    # with column not already in data.columns
    kwargs = {
        'column': 'other_column',
        'value': 5
    }

    res = fillna(data.copy(), **kwargs)
    assert isnan(res['value'][1])
    assert 'other_column' in res.columns
    assert all(x == 5 for x in res['other_column'])

    # with column_value argument correct
    kwargs = {
        'column': 'value',
        'column_value': 'year'
    }
    res = fillna(data.copy(), **kwargs)

    assert (res[data.value.isnull()].value == data[data.value.isnull()].year).all()

    # with column_value argument unccorrect
    kwargs = {
        'column': 'value',
        'column_value': 'uncorrect'
    }

    with pytest.raises(ValueError) as exc_info:
        fillna(data.copy(), **kwargs)
    assert str(exc_info.value) == '"uncorrect" is not a valid column name'

    # with column_value argument unccorrect
    kwargs = {
        'column': 'value',
        'column_value': 'value',
        'value': 1
    }

    with pytest.raises(ValueError) as exc_info:
        fillna(data.copy(), **kwargs)
    error_message = 'You cannot set both the parameters value and column_value'
    assert str(exc_info.value) == error_message

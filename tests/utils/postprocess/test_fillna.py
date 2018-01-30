import pandas as pd
from numpy import nan, isnan

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
    data2 = data.copy()

    kwargs = {
        'column': 'value',
        'value': 0
    }
    res = fillna(data, **kwargs)
    assert res['value'][1] == 0

    kwargs2 = {
        'column': 'other_column',
        'value': 5
    }

    res = fillna(data2, **kwargs2)
    assert isnan(res['value'][1])
    assert 'other_column' in res.columns
    assert all(x == 5 for x in res['other_column'])

from copy import copy

import pandas as pd

from toucan_data_sdk.utils.postprocess import cumsum


def test_cumsum():
    """ It should return result for cumsum """
    data = pd.DataFrame(
        [
            {'index_col': 'A', 'date_col': '20170109', 'value': 10},
            {'index_col': 'A', 'date_col': '20170209', 'value': 5},
            {'index_col': 'A', 'date_col': '20170909', 'value': 3},
            {'index_col': 'A', 'date_col': '20170509', 'value': 11},
        ]
    )
    expected_col = [10, 15, 26, 29]

    kwargs = {
        'new_column': 'result',
        'column': 'value',
        'index': 'index_col',
        'date_column': 'date_col',
        'date_format': '%Y%d%m',
    }

    res = cumsum(data, **kwargs)
    assert [*res.columns] == ['index_col', 'date_col', 'value', 'result']
    assert res['result'].tolist() == expected_col

    # same column
    kwargs = {
        'new_column': 'value',
        'column': 'value',
        'index': ['index_col'],
        'date_column': 'date_col',
        'date_format': '%Y%m%d',
    }
    res = cumsum(copy(data), **kwargs)
    assert [*res.columns] == ['index_col', 'date_col', 'value']
    assert res['value'].tolist() == expected_col

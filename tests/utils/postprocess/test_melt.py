import pandas as pd
import pytest

from toucan_data_sdk.utils.postprocess import melt


def test_melt():
    """ It should return result for melt """
    data = pd.DataFrame([{
        'column_1': 'S45',
        'column_2': 'lalaland',
        'info_1': 10,
        'info_2': 20,
        'info_3': None
    }])

    kwargs = {
        "id": ['column_1', 'column_2'],
        "value": ['info_1', 'info_2', 'info_3']
    }

    res = melt(data, **kwargs)
    res2 = melt(data, **kwargs, dropna=True)
    assert len(res) == 3
    assert len(res2) == 2
    assert res['variable'][0] == 'info_1'
    assert res['variable'][1] == 'info_2'
    assert res['variable'][2] == 'info_3'
    assert res['value'][0] == 10
    assert res['value'][1] == 20
    assert res['value'][2] is None
    assert 'info_1' in res2['variable'].values
    assert 'info_2' in res2['variable'].values
    assert 'info_3' not in res2['variable'].values

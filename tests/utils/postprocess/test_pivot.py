import pandas as pd
from copy import copy

from toucan_data_sdk.utils.postprocess import pivot, pivot_by_group


def test_pivot():
    """ It should return result for pivot """

    # ~~~~ pivot on int column ~~~
    data = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450}
    ])
    kwargs = {
        'index': ['variable', 'wave'],
        'column': 'year',
        'value': 'value'
    }
    res = pivot(data, **kwargs)
    assert res[2014][0] == 300
    assert res[2015][0] == 250
    assert res[2016][0] == 450

    # ~~~ pivot on str column ~~~
    data_obj = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 'value1'},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 'value2'},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 'value3'},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 'value4'},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 'value5'}
    ])
    res = pivot(data_obj, **kwargs)
    assert res[2014][0] == 'value1 value5'
    assert res[2015][0] == 'value2'
    assert res[2016][0] == 'value3 value4'


def test_pivot_by_group():
    """ It should return result for pivot """
    data = pd.DataFrame({
        'type': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B'],
        'kpi': ['var1', 'var1_evol', 'var2', 'var2_evol',
                'var1', 'var1_evol', 'var2', 'var2_evol'],
        'montant': [5, 0.3, 6, 0.2, 7, 0.5, 8, 0.4]
    })

    # ~~~ no id_cols ~~~
    kwargs = {
        'variable': 'kpi',
        'value': 'montant',
        'new_columns': ['value', 'variation'],
        'groups': {
            'var1': ['var1', 'var1_evol'],
            'var2': ['var2', 'var2_evol']
        }
    }
    res = pivot_by_group(copy(data), **kwargs)
    assert len(res.columns) == 3
    assert 'kpi' in res.columns
    assert len(res) == 2

    assert res.loc[res['kpi'] == 'var1', 'value'].iloc[0] == 6
    assert res.loc[res['kpi'] == 'var2', 'value'].iloc[0] == 7

    # ~~~ with id_cols ~~~
    kwargs = {
        'variable': 'kpi',
        'value': 'montant',
        'new_columns': ['value', 'variation'],
        'groups': {
            'var1': ['var1', 'var1_evol'],
            'var2': ['var2', 'var2_evol']
        },
        'id_cols': ['type']
    }
    res = pivot_by_group(data, **kwargs)
    assert len(res.columns) == 4
    assert len(res) == 4

    mask = (res['kpi'] == 'var1') & (res['type'] == 'A')
    assert res.loc[mask, 'value'].iloc[0] == 5
    mask2 = (res['kpi'] == 'var2') & (res['type'] == 'B')
    assert res.loc[mask2, 'variation'].iloc[0] == 0.4

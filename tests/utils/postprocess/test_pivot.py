import pandas as pd

from toucan_data_sdk.utils.postprocess import pivot, pivot_by_group


def test_pivot():
    """ It should return result for pivot """

    # ~~~~ pivot on int column ~~~
    data = pd.DataFrame(
        [
            {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450},
        ]
    )
    kwargs = {'index': ['variable', 'wave'], 'column': 'year', 'value': 'value'}
    res = pivot(data, **kwargs)
    assert res[2014][0] == 300
    assert res[2015][0] == 250
    assert res[2016][0] == 450

    # ~~~ pivot on str column ~~~
    data_obj = pd.DataFrame(
        [
            {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 'value1'},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 'value2'},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 'value3'},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 'value4'},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 'value5'},
        ]
    )
    res = pivot(data_obj, **kwargs)
    assert res[2014][0] == 'value1 value5'
    assert res[2015][0] == 'value2'
    assert res[2016][0] == 'value3 value4'


def test_pivot_agg_sum():
    """ It should return result for pivot """

    # ~~~~ pivot on int column ~~~
    data = pd.DataFrame(
        [
            {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 100},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 150},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 200},
        ]
    )
    kwargs = {
        'index': ['variable', 'wave'],
        'column': 'year',
        'value': 'value',
        'agg_function': 'sum',
    }
    res = pivot(data, **kwargs)
    assert res[2014][0] == 400
    assert res[2015][0] == 400
    assert res[2016][0] == 650


def test_pivot_agg_mean():
    """ It should return result for pivot """

    # ~~~~ pivot on int column ~~~
    data = pd.DataFrame(
        [
            {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 100},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 150},
            {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 200},
        ]
    )
    kwargs = {'index': ['variable', 'wave'], 'column': 'year', 'value': 'value'}
    res = pivot(data, **kwargs)
    assert res[2014][0] == 200
    assert res[2015][0] == 200
    assert res[2016][0] == 325


def test_pivot_with_value_to_pivot():
    data = pd.DataFrame(
        [
            {"date": 2018, "Type": 'A', "value_column": 2},
            {"date": 2018, "Type": 'B', "value_column": 2},
            {"date": 2018, "Type": 'REF', "value_column": 4},
            {"date": 2019, "Type": 'A', "value_column": 2},
            {"date": 2019, "Type": 'B', "value_column": 5},
            {"date": 2019, "Type": 'REF', "value_column": 3},
        ]
    )
    kwargs = {
        'index': ['date'],
        'column': 'Type',
        'value': 'value_column',
        'values_to_pivot': ['REF'],
    }
    res = pivot(data, **kwargs)
    assert res.columns.contains('REF')
    assert res.shape[0] == 4
    assert set(res.Type) == {'A', 'B'}

    data = pd.DataFrame(
        [
            {"date": 2018, "Type": 'A', "value_column": 2},
            {"date": 2018, "Type": 'B', "value_column": 2},
            {"date": 2018, "Type": 'REF', "value_column": 4},
            {"date": 2018, "Type": 'REF2', "value_column": 3},
            {"date": 2019, "Type": 'A', "value_column": 2},
            {"date": 2019, "Type": 'B', "value_column": 5},
            {"date": 2019, "Type": 'REF', "value_column": 3},
            {"date": 2019, "Type": 'REF2', "value_column": 3},
        ]
    )
    kwargs = {
        'index': ['date'],
        'column': 'Type',
        'value': 'value_column',
        'values_to_pivot': ['REF', 'REF2'],
    }
    res = pivot(data, **kwargs)
    assert res.columns.contains('REF')
    assert res.columns.contains('REF2')
    assert res.shape[0] == 4
    assert set(res.Type) == {'A', 'B'}


def test_pivot_by_group():
    """ It should return result for pivot """
    data = pd.DataFrame(
        {
            'type': ['A', 'A', 'A', 'A', 'B', 'B', 'B', 'B'],
            'kpi': [
                'var1',
                'var1_evol',
                'var2',
                'var2_evol',
                'var1',
                'var1_evol',
                'var2',
                'var2_evol',
            ],
            'montant': [5, 0.3, 6, 0.2, 7, 0.5, 8, 0.4],
        }
    )

    # ~~~ no id_cols ~~~
    kwargs = {
        'variable': 'kpi',
        'value': 'montant',
        'new_columns': ['value', 'variation'],
        'groups': {'var1': ['var1', 'var1_evol'], 'var2': ['var2', 'var2_evol']},
    }
    res = pivot_by_group(data, **kwargs)
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
        'groups': {'var1': ['var1', 'var1_evol'], 'var2': ['var2', 'var2_evol']},
        'id_cols': ['type'],
    }
    res = pivot_by_group(data, **kwargs)
    assert len(res.columns) == 4
    assert len(res) == 4

    mask = (res['kpi'] == 'var1') & (res['type'] == 'A')
    assert res.loc[mask, 'value'].iloc[0] == 5
    mask2 = (res['kpi'] == 'var2') & (res['type'] == 'B')
    assert res.loc[mask2, 'variation'].iloc[0] == 0.4

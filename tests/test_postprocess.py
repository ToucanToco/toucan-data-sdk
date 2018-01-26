from copy import copy

import pandas as pd
import pytest
from numpy import inf, nan, testing, isnan

from toucan_data_sdk.utils.postprocess import (
    replace, rename, melt, top, pivot,
    pivot_by_group, argmax, fillna,
    query_df, add, subtract, multiply,
    divide, cumsum, percentage, waterfall
)


@pytest.fixture
def sample_data():
    return [
        {'ord': 1, 'category_name': 'Clap', 'category_id': 'clap', 'product_id': 'super clap',
         'date': 't1', 'played': 12},
        {'ord': 10, 'category_name': 'Clap', 'category_id': 'clap', 'product_id': 'clap clap',
         'date': 't1', 'played': 1},
        {'ord': 1, 'category_name': 'Snare', 'category_id': 'snare', 'product_id': 'tac',
         'date': 't1', 'played': 1},
        {'ord': 1, 'category_name': 'Clap', 'category_id': 'clap', 'product_id': 'super clap',
         'date': 't2', 'played': 10},
        {'ord': 1, 'category_name': 'Snare', 'category_id': 'snare', 'product_id': 'tac',
         'date': 't2', 'played': 100},
        {'ord': 1, 'category_name': 'Tom', 'category_id': 'tom', 'product_id': 'bom',
         'date': 't2', 'played': 1}
    ]


def test_replace():
    """ It should replace data in the dataframe """
    df = pd.DataFrame([
        {'year': 2016, 'month': "jan."},
        {'year': 2016, 'month': "feb."},
        {'year': 2017, 'month': "jan."},
    ])
    config = {
        'column': 'month',
        'dst_column': 'month_int',
        'to_replace': {
            "jan.": 1,
            "feb.": 2,
            "mar.": 3,
        }
    }
    expected_result = [1, 2, 1]
    df = replace(df, **config)
    assert list(df.month_int) == expected_result


def test_rename():
    """ It should return a translated data dict """
    data = pd.DataFrame([{'hello': 'world'}])
    config = {
        'values': {'world': {'fr': 'monde'}},
        'columns': {'hello': {'fr': 'bonjour'}},
        'locale': 'fr'
    }
    data_translated = [{'bonjour': 'monde'}]
    df = rename(data, **config)
    res = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert res == data_translated


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

    bad_kwargs = {
        "id": ['column_1', 'apple'],
        "value": ['info_1', 'info_2', 'info_3']
    }
    with pytest.raises(Exception) as exc_info:
        melt(data, **bad_kwargs)
    assert str(exc_info.value) == 'Invalid configuration for melt, missing ' \
                                  'key: "[\'apple\'] not in index"'

    bad_kwargs2 = {
        "id": ['column_1', 'column_2'],
        "value": ['peach', 'banana', 'info_3']
    }
    with pytest.raises(Exception) as exc_info:
        melt(data, **bad_kwargs2)
    assert str(exc_info.value) == 'Invalid configuration for melt, missing ' \
                                  'key: "[\'peach\' \'banana\'] not in index"'


def test_top():
    """ It should return result for top """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 1, 'value': 100},
        {'variable': 'toto', 'Category': 1, 'value': 200},
        {'variable': 'toto', 'Category': 1, 'value': 300},
        {'variable': 'lala', 'Category': 1, 'value': 100},
        {'variable': 'lala', 'Category': 1, 'value': 150},
        {'variable': 'lala', 'Category': 1, 'value': 250},
        {'variable': 'lala', 'Category': 2, 'value': 350},
        {'variable': 'lala', 'Category': 2, 'value': 450}
    ])

    # ~~~ without group ~~~
    expected = [
        {'variable': 'lala', 'Category': 2, 'value': 450},
        {'variable': 'lala', 'Category': 2, 'value': 350},
        {'variable': 'toto', 'Category': 1, 'value': 300}
    ]

    kwargs = {
        "value": 'value',
        "limit": 3,
        "order": "desc"
    }
    df = top(data, **kwargs).reset_index(drop=True)
    assert pd.DataFrame(expected).equals(df)

    # ~~~ with group ~~~
    expected = [
        {'variable': 'lala', 'Category': 1, 'value': 150},
        {'variable': 'lala', 'Category': 1, 'value': 100},
        {'variable': 'lala', 'Category': 2, 'value': 450},
        {'variable': 'lala', 'Category': 2, 'value': 350},
        {'variable': 'toto', 'Category': 1, 'value': 200},
        {'variable': 'toto', 'Category': 1, 'value': 100}
    ]
    kwargs = {
        "group": ['variable', "Category"],
        "value": 'value',
        "limit": -2,
        "order": "desc"
    }
    df = top(data, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        assert wa[i] == expected[i]

    kwargs = {
        "group": ['variable', "Category"],
        "value": 'value',
        "limit": '-2',
        "order": "desc"
    }
    df = top(data, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        assert wa[i] == expected[i]

    # ~~~ bad group ~~~
    kwargs = {
        "group": ['apple'],
        "value": 'value',
        "limit": -2,
        "order": "desc"
    }
    with pytest.raises(Exception) as exc_info:
        top(data, **kwargs)
    assert str(exc_info.value) == "Invalid configuration for top, missing key: 'apple'"


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

    # ~~~ missing index ~~~
    bad_kwargs = {
        'index': ['apple'],
        'column': 'year',
        'value': 'value'
    }
    with pytest.raises(Exception) as exc_info:
        pivot(data, **bad_kwargs)
    assert str(exc_info.value) == "Invalid configuration for pivot, missing key: 'apple'"


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


def test_argmax():
    """ It should return result for argmax """
    data = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450}])

    kwargs = {'column': 'year'}
    res = argmax(data, **kwargs)
    res = res.reset_index(drop=True)
    assert len(res) == 1
    assert res['year'][0] == 2016
    assert res['value'][0] == 450


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


def test_query_df():
    """ It should return a filtered data dict """
    data = pd.DataFrame([{'value': 30}, {'value': 10}, {'value': 20}])
    config = {'query': 'value > 15'}
    filtered_data = pd.DataFrame([{'value': 30}, {'value': 20}], index=[0, 2])

    df = query_df(data, **config)
    assert df.equals(filtered_data)

    # ~~~ bad config ~~~
    with pytest.raises(Exception) as exc_info:
        query_df(data, **{'query': 'pomme > 10'})
    assert str(exc_info.value) == "Invalid query: name 'pomme' is not defined"


def test_math_operations():
    """ It should return result for basic math operations """
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

    # ~~~ bad column ~~~
    bad_kwargs = {'new_column': 'result', 'column_1': 'value1', 'column_2': 'apple'}

    with pytest.raises(Exception) as exc_info:
        add(data, **bad_kwargs)
    assert str(exc_info.value) == "Invalid config for sum: 'apple'"

    with pytest.raises(Exception) as exc_info:
        subtract(data, **bad_kwargs)
    assert str(exc_info.value) == "Invalid config for subtract: 'apple'"

    with pytest.raises(Exception) as exc_info:
        multiply(data, **bad_kwargs)
    assert str(exc_info.value) == "Invalid config for multiply: 'apple'"

    with pytest.raises(Exception) as exc_info:
        divide(data, **bad_kwargs)
    assert str(exc_info.value) == "Invalid config for divide: 'apple'"


def test_cumsum():
    """ It should return result for cumsum """
    data = pd.DataFrame([
        {'index_col': 'A', 'date_col': '20170901', 'value': 10},
        {'index_col': 'A', 'date_col': '20170902', 'value': 5},
        {'index_col': 'A', 'date_col': '20170909', 'value': 3},
        {'index_col': 'A', 'date_col': '20170905', 'value': 11}
    ])
    expected_col = [10, 15, 29, 26]

    kwargs = {'new_column': 'result',
              'column': 'value',
              'index': 'index_col',
              'date_column': 'date_col',
              'date_format': '%Y%m%d'}

    res = cumsum(data, **kwargs)
    assert [*res.columns] == ['date_col', 'index_col', 'value', 'result']
    assert res['result'].tolist() == expected_col

    # same column
    kwargs = {
        'new_column': 'value',
        'column': 'value',
        'index': ['index_col'],
        'date_column': 'date_col',
        'date_format': '%Y%m%d'
    }
    res = cumsum(copy(data), **kwargs)
    assert [*res.columns] == ['date_col', 'index_col', 'value']
    assert res['value'].tolist() == expected_col

    # ~~~ bad config ~~~
    bad_kwargs = {
        'new_column': 'value',
        'column': 'value',
        'index': ['index_col'],
        'date_column': 'apple',
        'date_format': '%Y%m%d'
    }
    with pytest.raises(Exception) as exc_info:
        cumsum(data, **bad_kwargs)
    assert str(exc_info.value) == "Invalid config for cumsum: 'apple'"


def test_percentage():
    """ It should add a column `number_percentage` to the dataframe """
    data = pd.DataFrame([
        {'gender': 'male', 'sport': 'bicycle', 'number': 17},
        {'gender': 'female', 'sport': 'basketball', 'number': 17},
        {'gender': 'male', 'sport': 'basketball', 'number': 3},
        {'gender': 'female', 'sport': 'football', 'number': 7},
        {'gender': 'female', 'sport': 'running', 'number': 30},
        {'gender': 'male', 'sport': 'running', 'number': 20},
        {'gender': 'male', 'sport': 'football', 'number': 21},
        {'gender': 'female', 'sport': 'bicycle', 'number': 17}
    ])

    # ~~~ without group_cols ~~~
    kwargs = {
        'new_column': 'number_percentage',
        'column': 'number'
    }
    res = percentage(data, **kwargs)
    assert res['number_percentage'].tolist()[0] == 1700/132
    assert res['number_percentage'].tolist()[2] == 300 / 132
    assert res['number_percentage'].tolist()[4] == 3000 / 132

    # ~~~ with group_cols ~~~
    kwargs = {
        'new_column': 'number_percentage',
        'column': 'number',
        'group_cols': ['sport']
    }
    res = percentage(data, **kwargs)
    expected_col = [50, 85, 15, 25, 60, 40, 75, 50]
    assert res['number_percentage'].tolist() == expected_col


def test_waterfall(sample_data):
    """ It should return value for waterfall """
    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'insideGroup': {'id': 'product_id', 'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    expected = [
        {'variation': nan, 'label': 'Trimestre 1', 'value': 14.0,
         'groups': nan, 'type': nan, 'order': nan},
        {'variation': -0.23076923076923078, 'label': 'Clap', 'value': -3.0,
         'groups': 'clap', 'type': 'parent', 'order': nan},
        {'variation': -0.16666666666666666, 'label': 'super clap', 'value': -2.0,
         'groups': 'clap', 'type': 'child', 'order': 1.0},
        {'variation': -1.000000, 'label': 'clap clap', 'value': -1.0,
         'groups': 'clap', 'type': 'child', 'order': 10.0},
        {'variation': 99.0, 'label': 'Snare', 'value': 99.0,
         'groups': 'snare', 'type': 'parent', 'order': nan},
        {'variation': 99.0, 'label': 'tac', 'value': 99.0,
         'groups': 'snare', 'type': 'child', 'order': 1.0},
        {'variation': inf, 'label': 'Tom', 'value': 1.0,
         'groups': 'tom', 'type': 'parent', 'order': nan},
        {'variation': inf, 'label': 'bom', 'value': 1.0,
         'groups': 'tom', 'type': 'child', 'order': 1.0},
        {'variation': nan, 'label': 'Trimester 2', 'value': 111.0,
         'groups': nan, 'type': nan, 'order': nan}
    ]
    df = pd.DataFrame(sample_data)
    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        testing.assert_equal(wa[i], expected[i])


def test_waterfall_upperGroup_groupsOrder(sample_data):
    for line in sample_data:
        line['category_order'] = len(line['category_name'])
        del line['ord']

    kwargs = {
        'upperGroup': {
            'id': 'category_id',
            'label': 'category_name',
            'groupsOrder': 'category_order'
        },
        'insideGroup': {
            'id': 'product_id'
        },
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    expected = [
        {'variation': nan, 'label': 'Trimestre 1', 'value': 14.0, 'groups': nan, 'type': nan,
         'order': nan},
        {'variation': inf, 'label': 'Tom', 'value': 1.0, 'groups': 'tom', 'type': 'parent',
         'order': 3.0},
        {'variation': inf, 'label': 'bom', 'value': 1.0, 'groups': 'tom', 'type': 'child',
         'order': nan},
        {'variation': -0.23076923076923078, 'label': 'Clap', 'value': -3.0, 'groups': 'clap',
         'type': 'parent', 'order': 4.0},
        {'variation': -1.0, 'label': 'clap clap', 'value': -1.0, 'groups': 'clap',
         'type': 'child', 'order': nan},
        {'variation': -0.16666666666666666, 'label': 'super clap', 'value': -2.0,
         'groups': 'clap', 'type': 'child', 'order': nan},
        {'variation': 99.0, 'label': 'Snare', 'value': 99.0, 'groups': 'snare',
         'type': 'parent', 'order': 5.0},
        {'variation': 99.0, 'label': 'tac', 'value': 99.0, 'groups': 'snare', 'type': 'child',
         'order': nan},
        {'variation': nan, 'label': 'Trimester 2', 'value': 111.0, 'groups': nan, 'type': nan,
         'order': nan}
    ]

    df = pd.DataFrame(sample_data)
    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        testing.assert_equal(wa[i], expected[i])


def test_waterfall_no_value_start():
    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'insideGroup': {'id': 'product_id', 'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    data = [
        {'ord': 1, 'category_name': 'Clap', 'category_id': 'clap',
         'product_id': 'super clap', 'date': 't2', 'played': 10},
        {'ord': 1, 'category_name': 'Snare', 'category_id': 'snare',
         'product_id': 'tac', 'date': 't2', 'played': 100},
        {'ord': 1, 'category_name': 'Tom', 'category_id': 'tom',
         'product_id': 'bom', 'date': 't2', 'played': 1}
    ]

    expected = [
        {'variation': nan, 'label': 'Trimestre 1', 'value': 0, 'groups': nan, 'type': nan,
         'order': nan},
        {'variation': inf, 'label': 'Clap', 'value': 10, 'groups': 'clap', 'type': 'parent',
         'order': nan},
        {'variation': inf, 'label': 'super clap', 'value': 10, 'groups': 'clap',
         'type': 'child', 'order': 1.0},
        {'variation': inf, 'label': 'Snare', 'value': 100.0, 'groups': 'snare',
         'type': 'parent', 'order': nan},
        {'variation': inf, 'label': 'tac', 'value': 100.0, 'groups': 'snare', 'type': 'child',
         'order': 1.0},
        {'variation': inf, 'label': 'Tom', 'value': 1.0, 'groups': 'tom', 'type': 'parent',
         'order': nan},
        {'variation': inf, 'label': 'bom', 'value': 1.0, 'groups': 'tom', 'type': 'child',
         'order': 1.0},
        {'variation': nan, 'label': 'Trimester 2', 'value': 111.0, 'groups': nan, 'type': nan,
         'order': nan}
    ]
    df = pd.DataFrame(data)
    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        testing.assert_equal(wa[i], expected[i])


def test_waterfall_null():
    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'insideGroup': {'id': 'product_id', 'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    data = None
    df = pd.DataFrame(data)
    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa == []


def test_waterfall_not_implemented(sample_data):
    """ It should raise Error for not implemented features """
    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'insideGroup': {'id': 'product_id', 'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
        'breakdown': ['id']
    }
    df = pd.DataFrame(sample_data)
    with pytest.raises(NotImplementedError) as exc_info:
        waterfall(df, **kwargs)
    assert str(exc_info.value) == 'We will add breakdown support ' \
                                  'on your request, please contact the devs'

    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }
    df = pd.DataFrame(sample_data)
    with pytest.raises(NotImplementedError) as exc_info:
        waterfall(df, **kwargs)
    assert str(exc_info.value) == 'We will add support for upperGroup only ' \
                                  'on you request, please contact the devs'

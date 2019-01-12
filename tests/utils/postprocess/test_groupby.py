import pandas as pd

from toucan_data_sdk.utils.postprocess import groupby

data = pd.DataFrame(
    [{'ENTITY': 'A', 'YEAR': '2017', 'VALUE_1': 10, 'VALUE_2': 3},
     {'ENTITY': 'A', 'YEAR': '2017', 'VALUE_1': 20, 'VALUE_2': 1},
     {'ENTITY': 'A', 'YEAR': '2018', 'VALUE_1': 10, 'VALUE_2': 5},
     {'ENTITY': 'A', 'YEAR': '2018', 'VALUE_1': 30, 'VALUE_2': 4},
     {'ENTITY': 'B', 'YEAR': '2017', 'VALUE_1': 60, 'VALUE_2': 4},
     {'ENTITY': 'B', 'YEAR': '2017', 'VALUE_1': 40, 'VALUE_2': 3},
     {'ENTITY': 'B', 'YEAR': '2018', 'VALUE_1': 50, 'VALUE_2': 7},
     {'ENTITY': 'B', 'YEAR': '2018', 'VALUE_1': 60, 'VALUE_2': 6}
     ])


def test_one_group_col_one_value_col():
    df = groupby(
        df=data,
        group_cols='ENTITY',
        aggregations={
            'VALUE_1': 'sum'
        }
    )
    df_expected = pd.DataFrame(
        [{'ENTITY': 'A', 'VALUE_1': 70},
         {'ENTITY': 'B', 'VALUE_1': 210}
         ])
    assert df.sort_index(axis=1).equals(df_expected.sort_index(axis=1))


def test_two_group_cols_two_value_cols():
    df = groupby(
        df=data,
        group_cols=['ENTITY', 'YEAR'],
        aggregations={
            'VALUE_1': 'sum',
            'VALUE_2': 'mean'
        }
    )
    df_expected = pd.DataFrame(
        [{'ENTITY': 'A', 'YEAR': '2017', 'VALUE_1': 30, 'VALUE_2': 2.0},
         {'ENTITY': 'A', 'YEAR': '2018', 'VALUE_1': 40, 'VALUE_2': 4.5},
         {'ENTITY': 'B', 'YEAR': '2017', 'VALUE_1': 100, 'VALUE_2': 3.5},
         {'ENTITY': 'B', 'YEAR': '2018', 'VALUE_1': 110, 'VALUE_2': 6.5}
         ])
    assert df.sort_index(axis=1).equals(df_expected.sort_index(axis=1))


def test_groupby_append():
    data_cols = ['ENTITY', 'YEAR', 'VALUE_1', 'VALUE_2']
    aggs = {
        'sum_value1': {'VALUE_1': 'sum'},
        'max_value1': {'VALUE_1': 'max'},
        'mean_value2': {'VALUE_2': 'mean'}
    }
    df = groupby(data.copy(), group_cols=['YEAR', 'ENTITY'], aggregations=aggs)
    assert df.shape == (8, 7)
    assert df[data_cols].equals(data[data_cols])
    expected_appended = pd.DataFrame({
        'sum_value1': [30, 30, 40, 40, 100, 100, 110, 110],
        'max_value1': [20, 20, 30, 30, 60, 60, 60, 60],
        'mean_value2': [2, 2, 4.5, 4.5, 3.5, 3.5, 6.5, 6.5]
    })
    assert df[['sum_value1', 'max_value1', 'mean_value2']].equals(expected_appended)

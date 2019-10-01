import pandas as pd

from toucan_data_sdk.utils.postprocess import groupby

data = pd.DataFrame(
    [
        {'ENTITY': 'A', 'YEAR': '2017', 'VALUE_1': 10, 'VALUE_2': 3},
        {'ENTITY': 'A', 'YEAR': '2017', 'VALUE_1': 20, 'VALUE_2': 1},
        {'ENTITY': 'A', 'YEAR': '2018', 'VALUE_1': 10, 'VALUE_2': 5},
        {'ENTITY': 'A', 'YEAR': '2018', 'VALUE_1': 30, 'VALUE_2': 4},
        {'ENTITY': 'B', 'YEAR': '2017', 'VALUE_1': 60, 'VALUE_2': 4},
        {'ENTITY': 'B', 'YEAR': '2017', 'VALUE_1': 40, 'VALUE_2': 3},
        {'ENTITY': 'B', 'YEAR': '2018', 'VALUE_1': 50, 'VALUE_2': 7},
        {'ENTITY': 'B', 'YEAR': '2018', 'VALUE_1': 60, 'VALUE_2': 6},
    ]
)


def test_one_group_col_one_value_col():
    df = groupby(df=data, group_cols='ENTITY', aggregations={'VALUE_1': 'sum'})
    df_expected = pd.DataFrame([{'ENTITY': 'A', 'VALUE_1': 70}, {'ENTITY': 'B', 'VALUE_1': 210}])
    assert df.sort_index(axis=1).equals(df_expected.sort_index(axis=1))


def test_two_group_cols_two_value_cols():
    df = groupby(
        df=data, group_cols=['ENTITY', 'YEAR'], aggregations={'VALUE_1': 'sum', 'VALUE_2': 'mean'}
    )
    df_expected = pd.DataFrame(
        [
            {'ENTITY': 'A', 'YEAR': '2017', 'VALUE_1': 30, 'VALUE_2': 2.0},
            {'ENTITY': 'A', 'YEAR': '2018', 'VALUE_1': 40, 'VALUE_2': 4.5},
            {'ENTITY': 'B', 'YEAR': '2017', 'VALUE_1': 100, 'VALUE_2': 3.5},
            {'ENTITY': 'B', 'YEAR': '2018', 'VALUE_1': 110, 'VALUE_2': 6.5},
        ]
    )
    assert df.sort_index(axis=1).equals(df_expected.sort_index(axis=1))


def test_multiple_aggregation_on_one_column():
    df = groupby(df=data, group_cols='ENTITY', aggregations={'VALUE_1': ['sum', 'count']})
    df_expected = pd.DataFrame(
        [
            {'ENTITY': 'A', 'sum_VALUE_1': 70, 'count_VALUE_1': 4},
            {'ENTITY': 'B', 'sum_VALUE_1': 210, 'count_VALUE_1': 4},
        ]
    )
    assert df.sort_index(axis=1).equals(df_expected.sort_index(axis=1))

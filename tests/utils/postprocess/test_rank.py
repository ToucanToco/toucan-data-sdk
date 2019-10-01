import pandas as pd
import pytest

from toucan_data_sdk.utils.postprocess import rank

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


def test_invalid_value_col_type():
    with pytest.raises(TypeError):
        rank(data, value_cols='ENTITY')


def test_empty_rank_cols_names():
    df = rank(data, value_cols='VALUE_1')
    assert df.columns[-1] == 'VALUE_1_rank'


def test_empty_group_cols():
    df = rank(data, value_cols=['VALUE_1', 'VALUE_2'])
    expected = pd.DataFrame(
        [
            {'VALUE_1_rank': 1, 'VALUE_2_rank': 2},
            {'VALUE_1_rank': 3, 'VALUE_2_rank': 1},
            {'VALUE_1_rank': 1, 'VALUE_2_rank': 6},
            {'VALUE_1_rank': 4, 'VALUE_2_rank': 4},
            {'VALUE_1_rank': 7, 'VALUE_2_rank': 4},
            {'VALUE_1_rank': 5, 'VALUE_2_rank': 2},
            {'VALUE_1_rank': 6, 'VALUE_2_rank': 8},
            {'VALUE_1_rank': 7, 'VALUE_2_rank': 7},
        ]
    )
    assert df[['VALUE_1_rank', 'VALUE_2_rank']].equals(expected)


def test_group_cols():
    df = rank(data, value_cols=['VALUE_1', 'VALUE_2'], group_cols='YEAR', method='average')
    expected = pd.DataFrame(
        [
            {'VALUE_1_rank': 1.0, 'VALUE_2_rank': 2.5},
            {'VALUE_1_rank': 2.0, 'VALUE_2_rank': 1.0},
            {'VALUE_1_rank': 1.0, 'VALUE_2_rank': 2.0},
            {'VALUE_1_rank': 2.0, 'VALUE_2_rank': 1.0},
            {'VALUE_1_rank': 4.0, 'VALUE_2_rank': 4.0},
            {'VALUE_1_rank': 3.0, 'VALUE_2_rank': 2.5},
            {'VALUE_1_rank': 3.0, 'VALUE_2_rank': 4.0},
            {'VALUE_1_rank': 4.0, 'VALUE_2_rank': 3.0},
        ]
    )
    assert df[['VALUE_1_rank', 'VALUE_2_rank']].equals(expected)

import pandas as pd

from toucan_data_sdk.utils.postprocess import add_aggregation_columns


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


def test_add_aggregation_columns():
    data_cols = ['ENTITY', 'YEAR', 'VALUE_1', 'VALUE_2']
    aggs = {
        'sum_value1': {'VALUE_1': 'sum'},
        'max_value1': {'VALUE_1': 'max'},
        'mean_value2': {'VALUE_2': 'mean'}
    }
    df = add_aggregation_columns(data.copy(), group_cols=['YEAR', 'ENTITY'], aggregations=aggs)
    assert df.shape == (8, 7)
    assert df[data_cols].equals(data[data_cols])
    expected_appended = pd.DataFrame({
        'sum_value1': [30, 30, 40, 40, 100, 100, 110, 110],
        'max_value1': [20, 20, 30, 30, 60, 60, 60, 60],
        'mean_value2': [2, 2, 4.5, 4.5, 3.5, 3.5, 6.5, 6.5]
    })
    assert df[['sum_value1', 'max_value1', 'mean_value2']].equals(expected_appended)

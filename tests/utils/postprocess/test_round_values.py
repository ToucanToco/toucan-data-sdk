import pandas as pd

from toucan_data_sdk.utils.postprocess import round_values

data = pd.DataFrame([{'ENTITY': 'A', 'VALUE_1': -1.563, 'VALUE_2': -1.563},
                     {'ENTITY': 'A', 'VALUE_1': 0.423, 'VALUE_2': 0.423},
                     {'ENTITY': 'A', 'VALUE_1': 0, 'VALUE_2': 0},
                     {'ENTITY': 'A', 'VALUE_1': 1.612, 'VALUE_2': 1.612}])


def test_round_result():
    config = {'params': {'VALUE_1': 0, 'VALUE_2': 1}}
    df = round_values(data, **config)
    expected = pd.DataFrame([{'ENTITY': 'A', 'VALUE_1': -2.0, 'VALUE_2': -1.6},
                             {'ENTITY': 'A', 'VALUE_1': 0.0, 'VALUE_2': 0.4},
                             {'ENTITY': 'A', 'VALUE_1': 0.0, 'VALUE_2': 0.0},
                             {'ENTITY': 'A', 'VALUE_1': 2.0, 'VALUE_2': 1.6}])
    assert df.equals(expected)

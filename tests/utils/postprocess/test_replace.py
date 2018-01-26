import pandas as pd
from toucan_data_sdk.utils.postprocess import replace


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

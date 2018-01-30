import pandas as pd

from toucan_data_sdk.utils.postprocess import (
    convert_datetime_to_str,
    convert_str_to_datetime
)


def test_convert_str_to_datetime():
    """ It should replace data in the dataframe """
    df = pd.DataFrame([
        {'date': '2016-01', 'city': "Rennes"},
        {'date': '2016-01', 'city': "Nantes"},
        {'date': '2017-05', 'city': "Paris"},
    ])
    config = {
        'selector': 'date',
        'format': '%Y-%m'
    }
    expected_result = [
        pd.Timestamp('20160101'),
        pd.Timestamp('20160101'),
        pd.Timestamp('20170501')
    ]
    df = convert_str_to_datetime(df, **config)
    assert list(df.date) == expected_result


def test_convert_datetime_to_str():
    """ It should replace data in the dataframe """
    df = pd.DataFrame([
        {'date': pd.Timestamp('20160101'), 'city': "Rennes"},
        {'date': pd.Timestamp('20160106'), 'city': "Nantes"},
        {'date': pd.Timestamp('20170501'), 'city': "Paris"},
    ])
    config = {
        'selector': 'date',
        'format': '%Y-%m'
    }
    expected_result = ['2016-01', '2016-01', '2017-05']
    df = convert_datetime_to_str(df, **config)
    assert list(df.date) == expected_result

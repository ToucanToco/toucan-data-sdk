import pandas as pd
import pytest
from numpy import nan

from toucan_data_sdk.utils.postprocess import (
    convert_datetime_to_str,
    convert_str_to_datetime,
    change_date_format,
    cast
)


def test_convert_str_to_datetime():
    """ It should replace data in the dataframe """
    config = {'column': 'date', 'format': '%Y-%m'}
    df = pd.DataFrame([
        {'date': '2016-01', 'city': "Rennes"},
        {'date': '2016-01', 'city': "Nantes"},
        {'date': '2017-05', 'city': "Paris"},
    ])
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
    expected_result = ['2016-01', '2016-01', '2017-05']

    config = {'column': 'date', 'format': '%Y-%m'}
    new_df = convert_datetime_to_str(df.copy(), **config)
    assert new_df['date'].tolist() == expected_result

    # with new_column
    config['new_column'] = 'date_str'
    new_df = convert_datetime_to_str(df.copy(), **config)
    assert new_df['date'][0] == pd.Timestamp('20160101')
    assert new_df['date_str'].tolist() == expected_result


def test_change_date_format():
    """ It should replace data in the dataframe """

    expected_result = ['01/01/2016', '06/01/2016', '01/05/2017']

    # wihtout format
    df = pd.DataFrame([
        {'date': pd.Timestamp('20160101'), 'city': "Rennes"},
        {'date': pd.Timestamp('20160106'), 'city': "Nantes"},
        {'date': pd.Timestamp('20170501'), 'city': "Paris"},
    ])

    config = {
        'column': 'date',
        'output_format': '%d/%m/%Y'}
    df = change_date_format(df, **config)
    assert list(df.date) == expected_result

    # without new_column
    df = pd.DataFrame([
        {'date': pd.Timestamp('20160101'), 'city': "Rennes"},
        {'date': pd.Timestamp('20160106'), 'city': "Nantes"},
        {'date': pd.Timestamp('20170501'), 'city': "Paris"},
    ])

    config = {
        'column': 'date',
        'input_format': '%Y%m%d',
        'output_format': '%d/%m/%Y'}
    df = change_date_format(df, **config)
    assert list(df.date) == expected_result

    # with new_column
    df = pd.DataFrame([
        {'date': pd.Timestamp('20160101'), 'city': "Rennes"},
        {'date': pd.Timestamp('20160106'), 'city': "Nantes"},
        {'date': pd.Timestamp('20170501'), 'city': "Paris"},
    ])

    config = {
        'column': 'date',
        'input_format': '%Y%m%d',
        'output_format': '%d/%m/%Y',
        'new_column': 'new_date'}
    df = change_date_format(df, **config)
    assert list(df.new_date) == expected_result


def test_cast():
    """ It should convert columns from one type to another"""
    df = pd.DataFrame([
        {'name': 'Pika', 'year': '2017', 'value': '12.7'},
        {'name': 'Chu', 'year': '2018', 'value': 3.1},
        {'name': 'Nani', 'year': 2015, 'value': '13'},
        {'name': 'Zbruh', 'year': '2012', 'value': 14}
    ])

    # Basic tests
    config = {
        'column': 'year',
        'type': 'int'
    }
    new_df = cast(df, **config)
    assert new_df['year'].tolist() == [2017, 2018, 2015, 2012]
    assert new_df[['name', 'value']].equals(df[['name', 'value']])

    config = {
        'column': 'value',
        'type': 'float'
    }
    new_df = cast(df, **config)
    assert new_df['value'].tolist() == [12.7, 3.1, 13.0, 14.0]

    config = {
        'column': 'year',
        'type': 'str'
    }
    new_df = cast(df, **config)
    assert new_df['year'].tolist() == ['2017', '2018', '2015', '2012']

    # with new_column
    config = {
        'column': 'year',
        'type': 'int',
        'new_column': 'year_as_int'
    }
    new_df = cast(df, **config)
    assert new_df['year_as_int'].tolist() == [2017, 2018, 2015, 2012]
    assert new_df[['name', 'value']].equals(df[['name', 'value']])

    # Add bad values
    df = df.append({'name': 'BadBoy', 'year': nan, 'value': ''}, ignore_index=True)
    config = {
        'column': 'year',
        'type': 'int',
    }
    with pytest.raises(ValueError):
        cast(df, **config)

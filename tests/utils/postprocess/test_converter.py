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
    df = pd.DataFrame([
        {'date': pd.Timestamp('20160101'), 'city': "Rennes"},
        {'date': pd.Timestamp('20160106'), 'city': "Nantes"},
        {'date': pd.Timestamp('20170501'), 'city': "Paris"},
    ])

    expected_result = ['01/01/2016', '06/01/2016', '01/05/2017']

    # without input_format
    config = {
        'column': 'date',
        'output_format': '%d/%m/%Y'}
    new_df = change_date_format(df.copy(), **config)
    assert list(new_df.date) == expected_result

    # without new_column and input_format
    config = {
        'column': 'date',
        'input_format': '%Y%m%d',
        'output_format': '%d/%m/%Y'}
    new_df = change_date_format(df.copy(), **config)
    assert list(new_df.date) == expected_result

    # with input_format
    config = {
        'column': 'date',
        'input_format': '%Y%m%d',
        'output_format': '%d/%m/%Y',
        'new_column': 'new_date'}
    new_df = change_date_format(df.copy(), **config)
    assert list(new_df.new_date) == expected_result

    # convert time-zone from non explicit timezone
    df = pd.DataFrame([
        {'date': "2018-11-13 08:00:02.091000", 'city': "Rennes"},
        {'date': "2018-11-13 12:01:05.091000", 'city': "Nantes"},
        {'date': "2018-11-13 10:12:09.091000", 'city': "Paris"},
    ])
    expected_result = ["09:00", "13:01", "11:12"]
    config = {'column': 'date', 'output_format': '%H:%M', 'new_time_zone': "Europe/Paris"}
    df_new = change_date_format(df, **config)
    assert list(df_new.date) == expected_result

    # Non convert time-zone from explicit timezone (+1)
    df = pd.DataFrame([
        {'date': "2018-11-13 10:00:02.091000+01:00", 'city': "Rennes"},
        {'date': "2018-11-13 14:01:05.091000+01:00", 'city': "Nantes"},
        {'date': "2018-11-13 12:12:09.091000+01:00", 'city': "Paris"},
    ])
    expected_result = ["09:00", "13:01", "11:12"]
    config = {'column': 'date', 'output_format': '%H:%M'}
    df_new = change_date_format(df, **config)
    assert list(df_new.date) == expected_result

    # convert time-zone from explicit timezone (+0)
    df = pd.DataFrame([
        {'date': "2018-11-13 08:00:02.091000+00:00", 'city': "Rennes"},
        {'date': "2018-11-13 12:01:05.091000+00:00", 'city': "Nantes"},
        {'date': "2018-11-13 10:12:09.091000+00:00", 'city': "Paris"},
    ])
    expected_result = ["09:00", "13:01", "11:12"]
    config = {'column': 'date', 'output_format': '%H:%M', 'new_time_zone': "Europe/Paris"}
    df_new = change_date_format(df, **config)
    assert list(df_new.date) == expected_result

    # convert time-zone from explicit timezone (+2)
    df = pd.DataFrame([
        {'date': "2018-11-13 10:00:02.091000+02:00", 'city': "Rennes"},
        {'date': "2018-11-13 14:01:05.091000+02:00", 'city': "Nantes"},
        {'date': "2018-11-13 12:12:09.091000+02:00", 'city': "Paris"},
    ])
    expected_result = ["08:00", "12:01", "10:12"]
    config = {'column': 'date', 'output_format': '%H:%M', 'new_time_zone': "UTC"}
    df_new = change_date_format(df, **config)
    assert list(df_new.date) == expected_result


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

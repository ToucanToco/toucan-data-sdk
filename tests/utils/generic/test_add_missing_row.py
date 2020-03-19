import math
import os

import pandas as pd
import pytest

from toucan_data_sdk.utils.generic import add_missing_row
from toucan_data_sdk.utils.helpers import ParamsValueError

fixtures_base_dir = 'tests/fixtures'


def test_add_missing_row():
    """
    It should add missing row compare to a reference column
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    new_df = add_missing_row(input_df, id_cols=['City', 'Country', 'Region'], reference_col='Year')
    assert len(new_df) == 12

    input_df = input_df.drop(['Country', 'Region'], axis=1).drop_duplicates()
    new_df = add_missing_row(input_df, id_cols=['City'], reference_col='Year')
    assert len(new_df) == 12


def test_add_missing_row_use_index():
    """
    It should add missing row using the index provided
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    new_df = add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year',
        complete_index=('2009', '2010', '2011', '2012'),
    )
    assert new_df.shape[0] == 16


def test_add_missing_row_between():
    """
    It should add missing row compare to a reference column that are
    between min and max value of each group
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    expected = [2011]
    new_df = add_missing_row(
        input_df, id_cols=['City', 'Country', 'Region'], reference_col='Year', method='between'
    )
    assert len(new_df) == 10

    result = new_df.loc[new_df['City'] == 'Nantes', 'Year'].unique().tolist()
    result.sort()
    assert result == expected


def test_add_missing_row_between_and_after():
    """
    It should add missing row compare to a reference column that are
    bigger than min of each group
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    expected = [2011, 2012]
    new_df = add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year',
        method='between_and_after',
    )

    assert len(new_df) == 11

    result = new_df.loc[new_df['City'] == 'Nantes', 'Year'].unique().tolist()
    result.sort()
    assert result == expected


def test_add_missing_row_between_and_before():
    """
    It should add missing row compare to a reference column that are
    smaller than max of each group
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'add_missing_row.csv'))

    expected = [2010, 2011]
    new_df = add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year',
        method='between_and_before',
    )

    result = new_df.loc[new_df['City'] == 'Nantes', 'Year'].unique().tolist()
    result.sort()
    assert result == expected


def test_add_missing_row_cols_to_keep():
    """
    It should add missing row compare to a reference column and keep an other column
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'add_missing_row_2.csv'))

    new_df = add_missing_row(
        input_df, id_cols=['group'], reference_col='date', cols_to_keep=['month']
    )
    mask = (new_df['group'] == 'B') & (new_df['date'] == 20161001)
    assert len(new_df.loc[mask, 'month']) == 1
    assert new_df.loc[mask, 'month'].iloc[0] == 'octobre'
    assert math.isnan(new_df.loc[mask, 'value'].iloc[0])


def test_add_missing_row_index_date_range():
    """
    It should add missing row compare to a date_range
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    input_df['Year'] = input_df['Year'].astype(str)
    complete_index = {
        'type': 'date',
        'format': '%Y',
        'start': '2010',
        'end': '2013',
        'freq': {'years': 1},
    }
    new_df = add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year',
        complete_index=complete_index,
    )

    assert len(new_df) == 16


def test_add_missing_row_index_date_error():
    """
    It should add missing row compare to a date_range
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    with pytest.raises(ParamsValueError) as e_info:
        add_missing_row(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            reference_col='Year',
            complete_index={'type': 'my_date'},
        )

    assert str(e_info.value) == 'Unknown complete index type: my_date'

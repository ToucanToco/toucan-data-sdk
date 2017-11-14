import os

import pandas as pd
import pytest

import toucan_data_sdk.utils as util


def get_fixture(filename):
    return pd.read_csv(os.path.join('tests/fixtures', filename))


def test_roll():
    """
    It should return the same DataFrame as the one after a roll_up

    """
    input_df = get_fixture('roll_up_in.csv')
    res_df = util.roll_up(input_df,
                          levels=['Country', 'Region', 'City'],
                          groupby_vars=['value', 'population'],
                          value_name='Location',
                          var_name='Type')
    res_df = res_df[['Location', 'Type', 'population',
                     'value', 'Country', 'Region', 'City']]
    expected_output = get_fixture('roll_up.csv')
    assert res_df.equals(expected_output)


def test_two_values_melt():
    """
    It should return the same DataFrame as the expected
    one after a two_values_melt
    """
    input_df = get_fixture('two_values_melt_in.csv')
    res_df = util.two_values_melt(
        input_df,
        first_value_vars=['avg', 'total'],
        second_value_vars=['evol_avg', 'evol_total'],
        var_name='type',
        value_name='location'
    )

    expected_output = get_fixture('two_values_melt_out.csv')
    assert res_df.equals(expected_output)


def test_compute_evolution():
    """
    It should compute an evolution column against a period that is distant
    from a fixed offset
    """
    input_df = get_fixture('compute_evolution.csv')
    evolution_col = util.compute_evolution(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        date_col='Year',
        value_col='population',
        freq=1,
        method='abs',
    )
    assert input_df['evolution'].equals(evolution_col)

    evolution_pct_col = util.compute_evolution(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        date_col='Year',
        value_col='population',
        freq=1,
        method='pct',
    )
    assert input_df['evolution_pct'].equals(evolution_pct_col)

    input_df = get_fixture('compute_evolution.csv')
    evolution_df = util.compute_evolution(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        date_col='Year',
        value_col='population',
        freq=1,
        method='pct',
        format='df'
    )
    assert input_df['populationA-1'].equals(
        evolution_df['population_offseted'])
    assert input_df['evolution_pct'].equals(
        evolution_df['evolution_computed'])
    assert input_df.shape[1] + 2 == evolution_df.shape[1]

    evolution_df = util.compute_evolution(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        date_col='Year',
        value_col='population',
        freq=1,
        method='pct',
        format='df',
        offseted_suffix='_A',
        evolution_col_name='evol'
    )
    assert input_df['populationA-1'].equals(evolution_df['population_A'])
    assert input_df['evolution_pct'].equals(evolution_df['evol'])
    assert input_df.shape[1] + 2 == evolution_df.shape[1]

    evolution_df = util.compute_evolution(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        date_col='Date',
        value_col='population',
        freq={
            'years': 1
        },
        method='pct',
        format='df'
    )
    assert input_df['populationA-1'].equals(
        evolution_df['population_offseted'])
    assert input_df['evolution_pct'].equals(evolution_df['evolution_computed'])
    assert input_df.shape[1] + 2 == evolution_df.shape[1]

    evolution_df = util.compute_evolution(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        date_col='Year',
        value_col='population',
        freq=1,
        method='abs',
        format='df',
        how='outer',
        fillna=0
    )

    evolution_fillna = pd.Series(
        [2, 10, 20, 200, 20, -13, 100, -12, -220, -7, -100])
    assert evolution_df['evolution_computed'].astype(int).equals(
        evolution_fillna)
    assert evolution_df.shape[0] == 11
    assert input_df.shape[1] + 2 == evolution_df.shape[1]


def test_compute_evolution_with_duplicates(mocker):
    """
    It should print a warning when the dataframe has duplicates
    """
    input_df = get_fixture('compute_evolution_duplicates.csv')
    mock_warning = mocker.patch('logging.Logger.warning')
    _ = util.compute_evolution(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        date_col='Year',
        value_col='population',
        freq=1,
        method='abs',
    )
    assert mock_warning.call_count == 1


def test_compute_evolution_with_wrong_method():
    """
    It should raise a ValueError when the method is not 'abs' or 'pct'
    """
    input_df = get_fixture('compute_evolution.csv')
    with pytest.raises(ValueError):
        _ = util.compute_evolution(
            input_df,
            id_cols=['City', 'Country', 'Region'],
            date_col='Year',
            value_col='population',
            freq=1,
            method='wrong_method',
        )


def test_compute_cumsum():
    """
    It should compute cumsum
    """
    input_df = get_fixture('compute_cumsum.csv')
    cumsum_df = util.compute_cumsum(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_cols=['Date'],
        value_cols=['population']
    )
    assert input_df['population_cumsum'].equals(cumsum_df['population'])

    cumsum_df = util.compute_cumsum(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_cols=['Date'],
        value_cols=['population'],
        cols_to_keep=['blob']
    )
    assert input_df['blob'].equals(cumsum_df['blob'])


def test_add_missing_row():
    """
    It should add missing row compare to a reference column
    """
    input_df = get_fixture('add_missing_row.csv')
    new_df = util.add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year'
    )
    assert new_df.shape[0] == 12


def test_add_missing_row_use_index():
    """
    It should add missing row using the index provided
    """
    input_df = get_fixture('add_missing_row.csv')
    new_df = util.add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year',
        complete_index=('2009', '2010', '2011', '2012')
    )
    assert new_df.shape[0] == 16


def test_compute_ffill_by_group():
    """
    It should compute ffill with a groupby
    """
    input_df = get_fixture('compute_ffill_by_group.csv')
    df = util.compute_ffill_by_group(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_cols=['Year'],
        value_col='population',
    )

    conditions = [
        {'Year': 2011, 'City': 'Lille', 'ffilled': True},
        {'Year': 2010, 'City': 'Nantes', 'ffilled': False},
        {'Year': 2012, 'City': 'Nantes', 'ffilled': True},
        {'Year': 2010, 'City': 'Paris', 'ffilled': False},
    ]

    for cond in conditions:
        mask = (df['Year'] == cond['Year']) & (df['City'] == cond['City'])
        assert df.loc[mask, 'population'].notnull().all() == cond['ffilled']

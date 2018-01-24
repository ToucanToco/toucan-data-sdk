import math
import os

import pandas as pd
import pytest

from toucan_data_sdk.utils import (
    roll_up,
    two_values_melt,
    compute_evolution_by_frequency,
    compute_evolution_by_criteria,
    compute_cumsum,
    add_missing_row,
    compute_ffill_by_group,
    aggregate_for_requesters,
    clean_dataframe,
    build_label_replacement_dict,
    change_vowels,
    randomize_values)
from toucan_data_sdk.utils.compute_evolution import DuplicateRowsError
from toucan_data_sdk.utils.helpers import ParamsValueError

fixtures_base_dir = 'tests/fixtures'


def test_roll():
    """
    It should return the same DataFrame as the one after a roll_up

    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'roll_up_in.csv'))
    res_df = roll_up(input_df,
                     levels=['Country', 'Region', 'City'],
                     groupby_vars=['value', 'population'],
                     value_name='Location',
                     var_name='Type')
    res_df = res_df[['Location', 'Type', 'population', 'value', 'Country', 'Region', 'City']]
    expected_output = pd.read_csv(os.path.join(fixtures_base_dir, 'roll_up.csv'))
    assert res_df.equals(expected_output)


def test_two_values_melt():
    """
    It should return the same DataFrame as the expected one in csv after a two_values_melt

    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'two_values_melt_in.csv'))
    res_df = two_values_melt(
        input_df,
        first_value_vars=['avg', 'total'],
        second_value_vars=['evol_avg', 'evol_total'],
        var_name='type',
        value_name='location'
    )

    expected_output = pd.read_csv(os.path.join(fixtures_base_dir, 'two_values_melt_out.csv'))
    res_df.equals(expected_output)


def test_compute_evolution():
    """
    It should compute an evolution column against a period that is distant
    from a fixed offset
    """
    id_cols = ['City', 'Country', 'Region']
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_evolution.csv'))
    evolution_col = compute_evolution_by_frequency(
        input_df,
        id_cols,
        'Year',
        'population',
        freq=1,
        method='abs',
    )
    assert input_df['evolution'].equals(evolution_col)

    evolution_pct_col = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
        date_col='Year',
        value_col='population',
        freq=1,
        method='pct',
    )
    assert input_df['evolution_pct'].equals(evolution_pct_col)

    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_evolution.csv'))
    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
        date_col='Year',
        value_col='population',
        freq=1,
        method='pct',
        format='df'
    )
    assert input_df['populationA-1'].equals(evolution_df['population_offseted'])
    assert input_df['evolution_pct'].equals(evolution_df['evolution_computed'])
    assert (input_df.shape[1] + 2) == evolution_df.shape[1]

    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
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
    assert (input_df.shape[1] + 2) == evolution_df.shape[1]

    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
        date_col='Date',
        value_col='population',
        freq={
            'years': 1
        },
        method='pct',
        format='df'
    )
    assert input_df['populationA-1'].equals(evolution_df['population_offseted'])
    assert input_df['evolution_pct'].equals(evolution_df['evolution_computed'])
    assert (input_df.shape[1] + 1) == evolution_df.shape[1]
    assert evolution_df['Date'].dtype == pd.np.object

    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
        date_col='Year',
        value_col='population',
        freq=1,
        method='abs',
        format='df',
        missing_date_as_zero=True
    )

    evolution_fillna = pd.Series([2, 10, 20, 200, 20, -13, 100, -12, -220, -7, -100])
    assert evolution_df['evolution_computed'].astype(int).equals(evolution_fillna)
    assert 11 == evolution_df.shape[0]
    assert (input_df.shape[1] + 2) == evolution_df.shape[1]


def test_compute_evolution_error_params():
    """
    It should compute an evolution column against a period that is distant
    from a fixed offset
    """
    id_cols = ['City', 'Country', 'Region', 'Year']
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_evolution.csv'))

    with pytest.raises(ParamsValueError) as e_info:
        compute_evolution_by_frequency(
            input_df,
            id_cols,
            'Year',
            'population',
            freq=1,
            method='abs',
        )

    assert "Duplicate declaration of column(s) {'Year'} in the parameters" == \
           str(e_info.value)


def test_compute_evolution_error_method():
    """
    It should fail to compute an evolution with unexpected method parameter.
    """
    id_cols = ['City', 'Country', 'Region']
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_evolution.csv'))
    with pytest.raises(ValueError):
        compute_evolution_by_frequency(
            input_df,
            id_cols,
            'Year',
            'population',
            freq=1,
            method='unknown',
        )


def test_compute_evolution_error_duplicate():
    """
    It should compute an evolution column against a period that is distant
    from a fixed offset
    """
    id_cols = ['Country', 'Region']
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_evolution.csv'))

    with pytest.raises(DuplicateRowsError):
        compute_evolution_by_frequency(
            input_df,
            id_cols,
            'Year',
            'population'
        )

    evolution_computed = compute_evolution_by_frequency(
        input_df,
        id_cols,
        'Year',
        'population',
        raise_duplicate_error=False
    )
    assert len(evolution_computed), 7


def test_compute_evolution_sub_df():
    """
    It should compute an evolution column against an other column
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_evolution.csv'))
    evolution_df = compute_evolution_by_criteria(
        input_df,
        id_cols=['Country'],
        value_col='population',
        compare_to="City =='Nantes'",
        method='abs',
        format='df'
    )

    assert 100 == evolution_df['population_offseted'][0]
    assert input_df['evolution_nantes'].equals(evolution_df['evolution_computed'])
    assert (input_df.shape[1] + 2) == evolution_df.shape[1]


def test_compute_cumsum():
    """
    It should compute cumsum
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_cumsum.csv'))
    cumsum_df = compute_cumsum(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_cols=['Date'],
        value_cols=['population']
    )
    assert input_df['population_cumsum'].equals(cumsum_df['population'])

    cumsum_df = compute_cumsum(
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
    input_df = pd.read_csv(
        os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    new_df = add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year'
    )
    assert len(new_df) == 12

    input_df = input_df.drop(['Country', 'Region'], axis=1).drop_duplicates()
    new_df = add_missing_row(
        input_df,
        id_cols=['City'],
        reference_col='Year'
    )
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
        complete_index=('2009', '2010', '2011', '2012')
    )
    assert new_df.shape[0] == 16


def test_add_missing_row_between():
    """
    It should add missing row compare to a reference column that are
    between min and max value of each group
    """
    input_df = pd.read_csv(
        os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    expected = [2011]
    new_df = add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year',
        method='between'
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
    input_df = pd.read_csv(
        os.path.join(fixtures_base_dir, 'add_missing_row.csv'))
    expected = [2011, 2012]
    new_df = add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year',
        method='between_and_after'
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
    input_df = pd.read_csv(
        os.path.join(fixtures_base_dir, 'add_missing_row.csv'))

    expected = [2010, 2011]
    new_df = add_missing_row(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_col='Year',
        method='between_and_before'
    )

    result = new_df.loc[new_df['City'] == 'Nantes', 'Year'].unique().tolist()
    result.sort()
    assert result == expected


def test_add_missing_row_keep_cols():
    """
    It should add missing row compare to a reference column and keep an other column
    """
    input_df = pd.read_csv(
        os.path.join(fixtures_base_dir, 'add_missing_row_2.csv'))

    new_df = add_missing_row(
        input_df,
        id_cols=['group'],
        reference_col='date',
        keep_cols=['month']
    )
    mask = (new_df['group'] == 'B') & (new_df['date'] == 20161001)
    assert len(new_df.loc[mask, 'month']) == 1
    assert new_df.loc[mask, 'month'].iloc[0] == 'octobre'
    assert math.isnan(new_df.loc[mask, 'value'].iloc[0])


def test_compute_ffill_by_group():
    """
    It should compute ffill with a groupby
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_ffill_by_group.csv'))
    new_df = compute_ffill_by_group(
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
        new_df_notnull_all = new_df.loc[
            (new_df['Year'] == cond['Year']) &
            (new_df['City'] == cond['City']),
            'population'
        ].notnull().all()
        assert new_df_notnull_all == cond['ffilled']


def test_compute_ffill_by_group_2():
    """
    It should compute_ffill_by_group without messing between groups
    """
    ytd_kills = pd.DataFrame([
        {'knight': 'lancelot', 'year': 500, 'quarter': 1, 'kills': 3},
        {'knight': 'lancelot', 'year': 500, 'quarter': 2},
        {'knight': 'lancelot', 'year': 500, 'quarter': 3},
        {'knight': 'lancelot', 'year': 500, 'quarter': 4, 'kills': 4},

        {'knight': 'arthur', 'year': 500, 'quarter': 1, 'kills': 10},
        {'knight': 'arthur', 'year': 500, 'quarter': 2, 'kills': 20},
        {'knight': 'arthur', 'year': 500, 'quarter': 3},
        {'knight': 'arthur', 'year': 500, 'quarter': 4, 'kills': 30},

        {'knight': 'lancelot', 'year': 501, 'quarter': 4, 'kills': 1},
        {'knight': 'lancelot', 'year': 501, 'quarter': 1, 'kills': 0},
        {'knight': 'lancelot', 'year': 501, 'quarter': 2},
        {'knight': 'lancelot', 'year': 501, 'quarter': 3},

        {'knight': 'arthur', 'year': 501, 'quarter': 4, 'kills': 4},
        {'knight': 'arthur', 'year': 501, 'quarter': 3},
        {'knight': 'arthur', 'year': 501, 'quarter': 2, 'kills': 2},
        {'knight': 'arthur', 'year': 501, 'quarter': 1, 'kills': 0},
    ])

    filled = compute_ffill_by_group(
        ytd_kills,
        id_cols=['knight', 'year'],
        reference_cols=['quarter'],
        value_col='kills',
    )

    expected = {
        'knight == "arthur" and year == 500 and quarter == 3': 20,
        'knight == "arthur" and year == 501 and quarter == 3': 2,
        'knight == "lancelot" and year == 500 and quarter == 2': 3,
        'knight == "lancelot" and year == 500 and quarter == 3': 3,
        'knight == "lancelot" and year == 501 and quarter == 2': 0,
        'knight == "lancelot" and year == 501 and quarter == 3': 0,
    }

    for query, expected_value in expected.items():
        assert filled.query(query).iloc[0].kills == expected_value


def test_aggregate_requesters():
    """
    It should aggregate for requesters without losing NaN values
    """
    df = pd.DataFrame([
        {'year': 2017, 'filter1': 'A', 'filter2': 'C', 'value': 1},
        {'year': 2017, 'filter1': 'A', 'filter2': 'D', 'value': 5},
        {'year': 2017, 'filter1': 'B', 'filter2': pd.np.nan, 'value': 2},
        {'year': 2017, 'filter1': 'B', 'filter2': 'C', 'value': 8},
    ])
    res = aggregate_for_requesters(
        df,
        ['year'],
        {'filter1': 'All 1', 'filter2': 'All 2'},
    )
    mask = (res['filter1'] == 'All 1') & (res['filter2'] == 'All 2')
    assert res[mask]['value'][0] == 16
    mask = (res['filter1'] == 'All 1') & (res['filter2'] == 'C')
    assert res[mask]['value'][0] == 9

    res = aggregate_for_requesters(
        df,
        ['year'],
        {'filter1': 'All 1', 'filter2': 'All 2'},
        'max'
    )
    mask = (res['filter1'] == 'All 1') & (res['filter2'] == 'All 2')
    assert res[mask]['value'][0] == 8
    mask = (res['filter1'] == 'All 1') & (res['filter2'] == 'C')
    assert res[mask]['value'][0] == 8


def test_clean_dataframe():
    """It should clean a dataframe"""
    df = pd.DataFrame([
        {'DATE OF BIRTH     ': 1991.0, 'name': 'Eric', 'age': 26, 'sex': 'male'},
        {'DATE OF BIRTH     ': 1980.0, 'name': 'Samya', 'age': 37, 'sex': 'female'},
        {'DATE OF BIRTH     ': 1988.0, 'name': 'Romain', 'age': 29, 'sex': 'male'},
        {'DATE OF BIRTH     ': 1988.0, 'name': 'Fred', 'age': 29, 'sex': 'male'},
        {'DATE OF BIRTH     ': 1990.0, 'name': 'Virginie', 'age': 27, 'sex': 'female'},
        {'DATE OF BIRTH     ': 1991.0, 'name': 'Pierre', 'age': 26, 'sex': 'male'},
        {'DATE OF BIRTH     ': 1999.0, 'name': 'Erwam', 'age': 18, 'sex': 'male'},
        {'DATE OF BIRTH     ': 2000.0, 'name': 'Sophie', 'age': 17, 'sex': 'female'},
        {'DATE OF BIRTH     ': 1970.0, 'name': 'Aurelie', 'age': 47, 'sex': 'female'},
        {'DATE OF BIRTH     ': 1993.0, 'name': 'Jeremie', 'age': 24, 'sex': 'male'},
        {'DATE OF BIRTH     ': 1973.0, 'name': 'Emilie', 'age': 44, 'sex': 'female'},
    ])
    df = clean_dataframe(df, threshold=5, rename_cols={'name': 'surname'})

    assert set(df.columns) == {'date-of-birth', 'surname', 'age', 'sex'}
    assert df['date-of-birth'].dtype == 'int'
    assert df['sex'].dtype == 'category'


@pytest.fixture()
def name_generator():
    return lambda: 'toto'


def test_change_vowels(name_generator):
    """
    It should change vowels when possible, and create a new name when impossible
    """

    def changed_letters(x, y):
        return [i for i in range(len(x)) if x[i] != y[i]]

    word_with_vowels = "TurlUtutu"
    res = change_vowels(word_with_vowels, name_generator)
    assert changed_letters(word_with_vowels, res) == [1, 4]

    res = change_vowels(word_with_vowels, name_generator, 3)
    assert changed_letters(word_with_vowels, res) == [1, 4, 6]

    word_with_no_vowel = "qwqwqw"
    res = change_vowels(word_with_no_vowel, name_generator)
    assert res == name_generator()


def test_change_vowels_not_a_string(name_generator):
    """
    It should not break when the input is not a string
    """
    res = change_vowels(0.123, name_generator=name_generator)
    assert res == name_generator()


def test_build_label_replacement_dict(name_generator):
    """It should build a replacement dict"""
    labels = pd.Series(['TurlUtutu', 'special', 'xkcd'])

    res = build_label_replacement_dict(
        labels,
        name_generator=name_generator,
        max_changed_vowels=3,
        override_values={'special': 'snowflake'}
    )
    assert res['TurlUtutu'] != 'TurlUtutu'
    assert res['TurlUtutu'][6] != 'u'
    assert res['xkcd'] == name_generator()
    assert res['special'] == 'snowflake'


def test_build_label_replacement_dict_with_keys_matching_values(name_generator):
    """It should build a replacement dict"""
    labels = pd.Series(['toto', 'xkcd'])

    res = build_label_replacement_dict(
        labels,
        name_generator=name_generator,
    )
    assert res['toto'] != 'toto'
    assert res['xkcd'] != 'toto'


def test_build_label_replacement_dict_with_no_name_generator():
    """It should build a replacement dict"""
    labels = pd.Series(['toto', 'xkcd'])
    res = build_label_replacement_dict(
        labels,
    )
    assert res['toto'] != 'toto'
    assert res['xkcd'] != 'xkcd'


def test_randomize_values():
    """It should output a serie with values in the required bounds"""
    values = pd.Series([0, 1, 2, 3, 4, 5])
    inf_bound = 0.85
    sup_bound = 1.15
    min_values = values * inf_bound
    max_values = values * sup_bound

    randomized = randomize_values(values, inf_bound, sup_bound)

    in_bounds = (randomized <= max_values) & (randomized >= min_values)

    assert in_bounds.all()


def test_randomize_values_bounds_error():
    """It should raise a ParamsValueError when the bounds are incorrect"""

    with pytest.raises(ParamsValueError) as e_info:
        randomize_values(pd.Series([0, 1]), 1.1, 0.2)

    assert str(e_info.value) == "The inferior bound should be inferior to the superior bound."

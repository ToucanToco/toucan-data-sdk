import os
import pandas as pd
from toucan_data_sdk.utils.generic import compute_ffill_by_group


fixtures_base_dir = 'tests/fixtures'


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

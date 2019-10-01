import os

import pandas as pd
import pytest

from toucan_data_sdk.utils.generic import compute_cumsum
from toucan_data_sdk.utils.helpers import ParamsValueError

fixtures_base_dir = 'tests/fixtures'


def test_compute_cumsum():
    """
    It should compute cumsum
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_cumsum.csv'))
    cumsum_df = compute_cumsum(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_cols=['Date'],
        value_cols=['population'],
    )
    assert input_df['population_cumsum'].equals(cumsum_df['population'])


def test_compute_cumsum_keep_cols():
    """
    It should compute cumsum an keep col
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_cumsum.csv'))
    cumsum_df = compute_cumsum(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_cols=['Date'],
        value_cols=['population'],
        cols_to_keep=['blob'],
    )
    assert input_df['blob'].equals(cumsum_df['blob'])


def test_compute_cumsum_multiple_values():
    """
    It should compute cumsum with multiple value
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_cumsum.csv'))
    cumsum_df = compute_cumsum(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_cols=['Date'],
        value_cols=['population', 'size'],
    )
    assert input_df['population_cumsum'].equals(cumsum_df['population'])
    assert input_df['size_cumsum'].equals(cumsum_df['size'])


def test_compute_cumsum_new_value_cols():
    """
    It should compute cumsum with multiple value
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, 'compute_cumsum.csv'))
    cumsum_df = compute_cumsum(
        input_df,
        id_cols=['City', 'Country', 'Region'],
        reference_cols=['Date'],
        value_cols=['population'],
        new_value_cols=['new_population'],
    )
    assert input_df['population'].equals(cumsum_df['population'])
    assert input_df['population_cumsum'].equals(cumsum_df['new_population'])


def test_compute_cumsum_new_value_cols_error():
    """
    It should compute cumsum with multiple value
    """
    with pytest.raises(ParamsValueError) as exc_info:
        compute_cumsum(
            pd.DataFrame(),
            id_cols=['City', 'Country', 'Region'],
            reference_cols=['Date'],
            value_cols=['population'],
            new_value_cols=['a', 'b'],
        )

    expected = "`value_cols` and `new_value_cols` needs to have the same number of elements"
    assert str(exc_info.value) == expected

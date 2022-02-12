import os

import pandas as pd

from toucan_data_sdk.utils.generic import two_values_melt

fixtures_base_dir = "tests/fixtures"


def test_two_values_melt():
    """
    It should return the same DataFrame as the expected one in csv after a two_values_melt

    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "two_values_melt_in.csv"))
    res_df = two_values_melt(
        input_df,
        first_value_vars=["avg", "total"],
        second_value_vars=["evol_avg", "evol_total"],
        var_name="type",
        value_name="location",
    )

    expected_output = pd.read_csv(os.path.join(fixtures_base_dir, "two_values_melt_out.csv"))
    res_df.equals(expected_output)

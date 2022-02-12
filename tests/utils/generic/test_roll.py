import os

import pandas as pd

from toucan_data_sdk.utils.generic import roll_up

fixtures_base_dir = "tests/fixtures"


def test_roll():
    """
    It should return the same DataFrame as the one after a roll_up

    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "roll_up_in.csv"))
    res_df = roll_up(
        input_df,
        levels=["Country", "Region", "City"],
        groupby_vars=["value", "population"],
        value_name="Location",
        var_name="Type",
        parent_name="Parent",
    )
    res_df = res_df[
        ["Location", "Type", "population", "value", "Country", "Region", "City", "Parent"]
    ]

    expected_output = pd.read_csv(os.path.join(fixtures_base_dir, "roll_up.csv"))
    assert res_df.equals(expected_output)


def test_drop_levels():
    """
    It should return the same DataFrame as the one after a roll_up

    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "roll_up_in.csv"))
    res_df = roll_up(
        input_df,
        levels=["Country", "Region", "City"],
        groupby_vars=["value", "population"],
        value_name="Location",
        var_name="Type",
        drop_levels=["Region"],
    )
    assert "Region" not in res_df.Type.unique()

import os

import pandas as pd
import pytest

from toucan_data_sdk.utils.generic import (
    compute_evolution_by_criteria,
    compute_evolution_by_frequency,
)
from toucan_data_sdk.utils.generic.compute_evolution import DuplicateRowsError
from toucan_data_sdk.utils.helpers import ParamsValueError

fixtures_base_dir = "tests/fixtures"


def test_compute_evolution():
    """
    It should compute an evolution column against a period that is distant
    from a fixed offset
    """
    id_cols = ["City", "Country", "Region"]
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "compute_evolution.csv"))
    evolution_col = compute_evolution_by_frequency(
        input_df, id_cols, "Year", "population", freq=1, method="abs"
    )
    assert input_df["evolution"].equals(evolution_col)

    evolution_pct_col = compute_evolution_by_frequency(
        input_df, id_cols=id_cols, date_col="Year", value_col="population", freq=1, method="pct"
    )
    assert input_df["evolution_pct"].equals(evolution_pct_col)

    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "compute_evolution.csv"))
    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
        date_col="Year",
        value_col="population",
        freq=1,
        method="pct",
        format="df",
    )
    assert input_df["populationA-1"].equals(evolution_df["population_offseted"])
    assert input_df["evolution_pct"].equals(evolution_df["evolution_computed"])
    assert (input_df.shape[1] + 2) == evolution_df.shape[1]

    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
        date_col="Year",
        value_col="population",
        freq=1,
        method="pct",
        format="df",
        offseted_suffix="_A",
        evolution_col_name="evol",
    )
    assert input_df["populationA-1"].equals(evolution_df["population_A"])
    assert input_df["evolution_pct"].equals(evolution_df["evol"])
    assert (input_df.shape[1] + 2) == evolution_df.shape[1]

    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
        date_col="Date",
        value_col="population",
        freq={"years": 1},
        method="pct",
        format="df",
    )

    assert input_df["populationA-1"].equals(evolution_df["population_offseted"])
    assert input_df["evolution_pct"].equals(evolution_df["evolution_computed"])
    assert (input_df.shape[1] + 1) == evolution_df.shape[1]
    assert evolution_df["Date"].dtype == pd.np.object

    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=id_cols,
        date_col="Year",
        value_col="population",
        freq=1,
        method="abs",
        format="df",
        missing_date_as_zero=True,
    )

    evolution_fillna = pd.Series([2, 10, 20, 200, 20, -13, 100, -12, -220, -7, -100])
    assert evolution_df["evolution_computed"].astype(int).equals(evolution_fillna)
    assert 11 == evolution_df.shape[0]
    assert (input_df.shape[1] + 2) == evolution_df.shape[1]


def test_compute_evolution_error_params():
    """
    It should compute an evolution column against a period that is distant
    from a fixed offset
    """
    id_cols = ["City", "Country", "Region", "Year"]
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "compute_evolution.csv"))

    with pytest.raises(ParamsValueError) as e_info:
        compute_evolution_by_frequency(
            input_df, id_cols, "Year", "population", freq=1, method="abs"
        )

    assert "Duplicate declaration of column(s) {'Year'} in the parameters" == str(e_info.value)


def test_compute_evolution_error_method():
    """
    It should fail to compute an evolution with unexpected method parameter.
    """
    id_cols = ["City", "Country", "Region"]
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "compute_evolution.csv"))
    with pytest.raises(ValueError):
        compute_evolution_by_frequency(
            input_df, id_cols, "Year", "population", freq=1, method="unknown"
        )


def test_compute_evolution_error_duplicate():
    """
    It should compute an evolution column against a period that is distant
    from a fixed offset
    """
    id_cols = ["Country", "Region"]
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "compute_evolution.csv"))

    with pytest.raises(DuplicateRowsError):
        compute_evolution_by_frequency(input_df, id_cols, "Year", "population")

    evolution_computed = compute_evolution_by_frequency(
        input_df, id_cols, "Year", "population", raise_duplicate_error=False
    )
    assert len(evolution_computed), 7


def test_compute_evolution_sub_df():
    """
    It should compute an evolution column against an other column
    """
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "compute_evolution.csv"))
    evolution_df = compute_evolution_by_criteria(
        input_df,
        id_cols=["Country"],
        value_col="population",
        compare_to="City =='Nantes'",
        method="abs",
        format="df",
    )

    assert 100 == evolution_df["population_offseted"][0]
    assert input_df["evolution_nantes"].equals(evolution_df["evolution_computed"])
    assert (input_df.shape[1] + 2) == evolution_df.shape[1]


def test_compute_evolution_by_frequency_date_dict():
    input_df = pd.read_csv(os.path.join(fixtures_base_dir, "compute_evolution.csv"))
    evolution_df = compute_evolution_by_frequency(
        input_df,
        id_cols=["City", "Country", "Region"],
        date_col={"selector": "Partial_Date", "format": "%Y-%m"},
        value_col="population",
        freq={"years": 1},
        method="pct",
        format="df",
    )

    assert input_df["populationA-1"].equals(evolution_df["population_offseted"])
    assert input_df["evolution_pct"].equals(evolution_df["evolution_computed"])
    assert (input_df.shape[1] + 1) == evolution_df.shape[1]

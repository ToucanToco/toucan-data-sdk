import pandas as pd

from toucan_data_sdk.utils.postprocess import top, top_group


def test_top():
    """It should return result for top"""
    data = pd.DataFrame(
        [
            {"variable": "toto", "Category": 1, "value": 100},
            {"variable": "toto", "Category": 1, "value": 200},
            {"variable": "toto", "Category": 1, "value": 300},
            {"variable": "lala", "Category": 1, "value": 100},
            {"variable": "lala", "Category": 1, "value": 150},
            {"variable": "lala", "Category": 1, "value": 250},
            {"variable": "lala", "Category": 2, "value": 350},
            {"variable": "lala", "Category": 2, "value": 450},
        ]
    )

    # ~~~ without group ~~~
    expected = pd.DataFrame(
        [
            {"variable": "lala", "Category": 2, "value": 450},
            {"variable": "lala", "Category": 2, "value": 350},
            {"variable": "toto", "Category": 1, "value": 300},
        ]
    )
    kwargs = {"value": "value", "limit": 3, "order": "desc"}
    df = top(data, **kwargs).reset_index(drop=True)
    assert df.equals(expected)

    # ~~~ with group ~~~
    expected = pd.DataFrame(
        [
            {"variable": "lala", "Category": 1, "value": 150},
            {"variable": "lala", "Category": 1, "value": 100},
            {"variable": "lala", "Category": 2, "value": 450},
            {"variable": "lala", "Category": 2, "value": 350},
            {"variable": "toto", "Category": 1, "value": 200},
            {"variable": "toto", "Category": 1, "value": 100},
        ]
    )
    kwargs = {"group": ["variable", "Category"], "value": "value", "limit": -2, "order": "desc"}
    df = top(data, **kwargs)
    assert df.equals(expected)


def test_top_date_strings():
    """It should manage to use top if the column can be interpretated as date"""
    df = pd.DataFrame(
        {"date": ["2017-01-01", "2017-03-02", "2018-01-02", "2016-04-02", "2017-01-03"]}
    )
    top_df = top(df, value="date", limit=2)
    assert top_df["date"].tolist() == ["2016-04-02", "2017-01-01"]

    top_df = top(df, value="date", limit=3, order="desc")
    assert top_df["date"].tolist() == ["2018-01-02", "2017-03-02", "2017-01-03"]

    top_df = top(df, value="date", limit=3, order="desc", date_format="%Y-%d-%m")
    assert top_df["date"].tolist() == ["2018-01-02", "2017-01-03", "2017-03-02"]


def test_top_date_strings_temp_column():
    """It should not change existing columns"""
    df = pd.DataFrame(
        {"date": ["2017-01-01", "2017-03-02"], "date_": ["a", "b"], "date__": ["aa", "bb"]}
    )
    assert top(df, value="date", limit=2, order="desc").equals(df[::-1])


def test_top_group():
    """It should return result for top_group"""
    data = pd.DataFrame(
        {
            "Label": ["G1", "G2", "G3", "G4", "G5", "G3", "G3"],
            "Categories": ["C1", "C2", "C1", "C2", "C1", "C2", "C3"],
            "Valeurs": [6, 1, 9, 4, 8, 2, 5],
            "Periode": ["mois", "mois", "mois", "semaine", "semaine", "semaine", "semaine"],
        }
    )

    # ~~~ with filters ~~~
    expected = pd.DataFrame(
        {
            "Periode": ["mois", "mois", "semaine", "semaine", "semaine"],
            "Label": ["G3", "G1", "G5", "G3", "G3"],
            "Categories": ["C1", "C1", "C1", "C2", "C3"],
            "Valeurs": [9, 6, 8, 2, 5],
        }
    )
    kwargs = {
        "group": "Periode",
        "value": "Valeurs",
        "aggregate_by": ["Label"],
        "limit": 2,
        "order": "desc",
    }
    df = top_group(data, **kwargs)
    assert df.equals(expected)

    # ~~~ without groups ~~~
    expected = pd.DataFrame(
        {
            "Label": ["G3", "G3", "G3", "G5"],
            "Categories": ["C1", "C2", "C3", "C1"],
            "Valeurs": [9, 2, 5, 8],
            "Periode": ["mois", "semaine", "semaine", "semaine"],
        }
    )
    kwargs = {
        "group": None,
        "value": "Valeurs",
        "aggregate_by": ["Label"],
        "limit": 2,
        "order": "desc",
    }
    df = top_group(data, **kwargs)
    assert df.equals(expected)

    # ~~~ with group and function = mean ~~~
    expected = pd.DataFrame(
        {
            "Periode": ["mois", "mois", "semaine", "semaine"],
            "Label": ["G3", "G1", "G5", "G4"],
            "Categories": ["C1", "C1", "C1", "C2"],
            "Valeurs": [9, 6, 8, 4],
        }
    )
    kwargs = {
        "group": ["Periode"],
        "value": "Valeurs",
        "aggregate_by": ["Label"],
        "limit": 2,
        "function": "mean",
        "order": "desc",
    }
    df = top_group(data, **kwargs)
    assert df.equals(expected)

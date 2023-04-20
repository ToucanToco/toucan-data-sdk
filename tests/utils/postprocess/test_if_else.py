import pandas as pd
import pytest

from toucan_data_sdk.utils.postprocess import if_else

rows1 = [
    {"country": "France", "city": "Paris", "clean": -1, "the rating": 3},
    {"country": "Germany", "city": "Munich", "clean": 4, "the rating": 5},
]

rows2 = [
    {"country": "France", "city": "Nice", "clean": 3, "the rating": 4},
    {"country": "Hell", "city": "HellCity", "clean": 0, "the rating": 0},
]


@pytest.mark.parametrize(
    "df",
    [
        pd.DataFrame(rows1 + rows2),  # test for single dataframe
        pd.concat([pd.DataFrame(rows1), pd.DataFrame(rows2)]),  # test for concatenated dataframe
        pd.concat(
            [pd.DataFrame(rows1, index=[0, 0]), pd.DataFrame(rows2, index=[0, 0])]
        ),  # test with not unique df.index
    ],
)
def test_if_else(df):
    config = {
        "if": "`the rating` == 3",
        "then": {"postprocess": "formula", "formula": '("the rating" + clean) // 2'},
        "else": "Hihi",
        "new_column": "new",
    }
    res = if_else(df, **config)
    assert res.columns.tolist() == ["country", "city", "clean", "the rating", "new"]
    assert res[["country", "city", "clean", "the rating"]].equals(df)
    assert res["new"].tolist() == [1, "Hihi", "Hihi", "Hihi"]

    config = {
        "if": "`the rating` % 2 == 0",
        "then": 7,
        "else": [
            {
                "postprocess": "concat",
                "columns": ["country", "city"],
                "sep": " -> ",
                "new_column": "concated",
            },
            {"postprocess": "upper", "column": "concated"},
        ],
        "new_column": "new",
    }
    res = if_else(df, **config)
    assert res.columns.tolist() == ["country", "city", "clean", "the rating", "new", "concated"]
    assert res[["country", "city", "clean", "the rating"]].equals(df)
    assert res["new"].tolist() == ["FRANCE -> PARIS", "GERMANY -> MUNICH", 7, 7]

    config = {
        "if": 'country == "France"',
        "then": "F",
        "else": {
            "postprocess": "if_else",
            "if": 'country == "Germany"',
            "then": "G",
            "else": "Other",
        },
        "new_column": "new",
    }
    res = if_else(df, **config)
    assert res["new"].tolist() == ["F", "G", "F", "Other"]

    config = {"if": 'country == "France"', "then": "F", "new_column": "new"}
    res = if_else(df, **config)
    assert res["new"].tolist() == ["F", None, "F", None]

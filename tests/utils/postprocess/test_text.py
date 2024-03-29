import pandas as pd
import pytest

from toucan_data_sdk.utils.postprocess.text import (
    capitalize,
    center,
    concat,
    contains,
    endswith,
    find,
    isupper,
    length,
    lower,
    partition,
    repeat,
    replace_pattern,
    split,
    strip,
    title,
)


@pytest.fixture
def df():
    return pd.DataFrame(
        {
            "a": ["1", "3", "2", "1"],
            "b": ["lower", "CAPITALS", "this is a sentence", "SwApCaSe"],
            "c": [77, 88, 99, 11],
            "d": ["pika", "fway", "zbruh", "wesh"],
        }
    )


@pytest.fixture
def df1():
    return pd.DataFrame(
        {"a": ["1", "3", "2", "1"], "b": ["2017 03 01", "2018", "2014 03 12", "2018 01 01"]}
    )


def test_length(df):
    df = length(df, "b", "c")
    assert df["c"].tolist() == [5, 8, 18, 8]


def test_lower(df):
    df = lower(df, "b")
    assert df["b"].tolist() == ["lower", "capitals", "this is a sentence", "swapcase"]


def test_title(df):
    df = title(df, "b", new_column="c")
    assert df["c"].tolist() == ["Lower", "Capitals", "This Is A Sentence", "Swapcase"]


def test_capitalize(df):
    df = capitalize(df, "b", new_column="c")
    assert df["c"].tolist() == ["Lower", "Capitals", "This is a sentence", "Swapcase"]


def test_is_upper(df):
    df = isupper(df, "b", "c")
    assert df["c"].tolist() == [False, True, False, False]


def test_strip():
    df = pd.DataFrame({"a": ["#   b #", "  #c####", "asd#"]})
    df = strip(df, "a", new_column="b", to_strip="# ")
    assert df["b"].tolist() == ["b", "c", "asd"]


def test_center(df):
    df = center(df, "d", width=10, fillchar="*")
    assert df["d"].tolist() == ["***pika***", "***fway***", "**zbruh***", "***wesh***"]


def test_split(df1):
    # new_columns set but not a list
    with pytest.raises(ValueError) as e1:
        split(df1.copy(), column="b", new_columns="new_col")
    # new_columns is a list without enough items
    with pytest.raises(ValueError) as e2:
        split(df1.copy(), column="b", new_columns=["c", "d"])
    expected_error_message = "'new_columns' should be a list with at least 3 elements"
    assert str(e1.value) == str(e2.value) == expected_error_message

    df = split(df1.copy(), column="b", new_columns=["c", "d", "e"])
    assert df["c"].tolist() == ["2017", "2018", "2014", "2018"]
    assert df["d"].tolist() == ["03", None, "03", "01"]
    assert df["e"].tolist() == ["01", None, "12", "01"]

    df = split(df1.copy(), column="b", new_columns=["c", "d", "e"], limit=1)
    assert df["c"].tolist() == ["2017", "2018", "2014", "2018"]
    assert df["d"].tolist() == ["03 01", None, "03 12", "01 01"]
    assert "e" not in df.columns

    # new_columns not set -> create it
    df = split(df1.copy(), column="b")
    assert df.columns.tolist() == ["a", "b", "b_1", "b_2", "b_3"]


def test_partition(df1):
    with pytest.raises(ValueError):
        partition(df1, column="b", new_columns=["c", "d"])

    df = partition(df1, column="b", new_columns=["c", "d", "e"])
    assert df["c"].tolist() == ["2017", "2018", "2014", "2018"]
    assert df["d"].tolist() == [" ", "", " ", " "]
    assert df["e"].tolist() == ["03 01", "", "03 12", "01 01"]


def test_find(df):
    df = find(df, "d", sub="a")
    assert df["d"].tolist() == [3, 2, -1, -1]


def test_endswith(df):
    df = endswith(df, "b", new_column="res", pat="e")
    assert df["res"].tolist() == [False, False, True, True]


def test_concat(df):
    with pytest.raises(ValueError):
        concat(df, columns=["a"], new_column="res")

    df = concat(df, columns=["a", "b", "d"], new_column="res")
    assert df["res"].tolist() == [
        "1lowerpika",
        "3CAPITALSfway",
        "2this is a sentencezbruh",
        "1SwApCaSewesh",
    ]

    df = concat(df, columns=["d", "c", "a"], new_column="res", sep="/")
    assert df["res"].tolist() == ["pika/77/1", "fway/88/3", "zbruh/99/2", "wesh/11/1"]


def test_concat_integer_columns():
    """It should keep the numbers as int if possible in concat"""
    df = pd.DataFrame({"a": ["pika", "bulbi"], "b": [1, None], "c": [1.0, 2.1]})
    concat_df = concat(df.copy(), columns=["a", "b"], new_column="res")
    assert concat_df["res"].tolist() == ["pika1", "bulbi"]
    assert concat_df[["a", "b", "c"]].equals(df)

    assert concat(df, columns=["a", "c"], new_column="res")["res"].tolist() == [
        "pika1.0",
        "bulbi2.1",
    ]
    assert concat(df, columns=["b", "c"], new_column="res")["res"].tolist() == ["11.0", "2.1"]


def test_contains(df):
    df = contains(df, "b", new_column="res", pat="ca", case=False)
    assert df["res"].tolist() == [False, True, False, True]


def test_repeat(df):
    df = repeat(df, "d", times=2)
    assert df["d"].tolist() == ["pikapika", "fwayfway", "zbruhzbruh", "weshwesh"]


def test_replace_pattern(df):
    df = replace_pattern(df, "b", pat=r"[a-z]{3}$", repl="$")
    assert df["b"].tolist() == ["lo$", "CAPITALS", "this is a sente$", "SwApCaSe"]

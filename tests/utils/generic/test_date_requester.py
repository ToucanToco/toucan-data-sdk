import pandas as pd

from toucan_data_sdk.utils.generic import date_requester_generator

fixtures_base_dir = "tests/fixtures"


df = pd.DataFrame(
    {
        "date": ["2018-01-01", "2018-01-05", "2018-01-04", "2018-01-03", "2018-01-02"],
        "my_kpi": [1, 2, 3, 4, 5],
    }
)


df_2 = pd.DataFrame(
    {
        "date": ["01/01/2018", "05/01/2018", "04/01/2018", "03/01/2018", "02/01/2018"],
        "my_kpi": [1, 2, 3, 4, 5],
    }
)

df_3 = pd.DataFrame({"date": ["2018-03-01", "2017-10-01"], "my_kpi": [1, 5]})


def test_date_requester_generator():
    # mandatory only
    result = date_requester_generator(df, "date", frequency="D")
    expected_date = ["2018-01-01", "2018-01-02", "2018-01-03", "2018-01-04", "2018-01-05"]

    assert result.shape == (5, 3)
    assert list(result["DATE"]) == expected_date

    # with a different date_column_format
    result = date_requester_generator(df_2, "date", date_column_format="%d/%m/%Y", frequency="D")
    expected_date = ["2018-01-01", "2018-01-02", "2018-01-03", "2018-01-04", "2018-01-05"]

    assert result.shape == (5, 3)
    assert list(result["DATE"]) == expected_date

    # with format
    result = date_requester_generator(df, "date", frequency="D", format="%d/%m/%Y")
    expected_date = ["01/01/2018", "02/01/2018", "03/01/2018", "04/01/2018", "05/01/2018"]
    expected_granularity = ["date"] * 5

    assert result.shape == (5, 3)
    assert list(result["DATE"]) == expected_date
    assert list(result["GRANULARITY"]) == expected_granularity

    # with multi-ganularity
    result = date_requester_generator(
        df, "date", frequency="D", granularities={"day": "%d/%m/%Y", "Semaine": "%W"}
    )
    expected_date = ["01/01/2018", "02/01/2018", "03/01/2018", "04/01/2018", "05/01/2018", "01"]

    expected_granularity = ["day"] * 5 + ["Semaine"]

    assert result.shape == (6, 3)
    assert list(result["DATE"]) == expected_date
    assert list(result["GRANULARITY"]) == expected_granularity

    # with others_format
    result = date_requester_generator(
        df, "date", frequency="D", granularities={"day": "%d/%m/%Y"}, others_format={"year": "%Y"}
    )
    expected_date = ["01/01/2018", "02/01/2018", "03/01/2018", "04/01/2018", "05/01/2018"]
    expected_year = ["2018"] * 5

    assert result.shape == (5, 4)
    assert list(result["DATE"]) == expected_date
    assert "year" in result.columns
    assert list(result["year"]) == expected_year

    # with time delta
    result = date_requester_generator(df, "date", frequency="D", times_delta={"Tomorow": "+1 day"})

    expected_tomorow = ["2018-01-02", "2018-01-03", "2018-01-04", "2018-01-05", "2018-01-06"]
    assert result.shape == (5, 4)
    assert "Tomorow" in result.columns
    assert list(result["Tomorow"]) == expected_tomorow

    # with time delta and explicit format
    result = date_requester_generator(
        df, "date", frequency="D", format="%d/%m", times_delta={"Tomorow": "+1 day"}
    )

    expected_tomorow = ["02/01", "03/01", "04/01", "05/01", "06/01"]
    assert result.shape == (5, 4)
    assert "Tomorow" in result.columns
    assert list(result["Tomorow"]) == expected_tomorow

    # with multi-ganularity and others_format
    result = date_requester_generator(
        df_3,
        "date",
        frequency="M",
        granularities={"Mois": "%Y-%m", "Annee": "%Y"},
        others_format={"DYEAR": "%Y", "DMONTH": "%m"},
    )

    assert result.shape == (7, 5)
    assert list(result["DATE"]) == [
        "2017-10",
        "2017-11",
        "2017-12",
        "2018-01",
        "2018-02",
        "2017",
        "2018",
    ]
    assert list(result["GRANULARITY"]) == ["Mois"] * 5 + ["Annee"] * 2
    assert list(result["DYEAR"]) == ["2017", "2017", "2017", "2018", "2018", "2017", "2018"]
    assert list(result["DMONTH"]) == ["10", "11", "12", "01", "02", "10", "01"]


def test_date_requester_generator_locales():
    res = date_requester_generator(df, "date", frequency="D", format="%A")
    assert res.DATE.tolist() == ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    de_res = date_requester_generator(df, "date", frequency="D", format="%A", locale="de")
    assert de_res.DATE.tolist() == ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

    bad_locale_res = date_requester_generator(df, "date", frequency="D", format="%A", locale="pika")
    assert bad_locale_res.equals(res)

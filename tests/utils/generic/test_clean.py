import pandas as pd

from toucan_data_sdk.utils.generic import clean_dataframe


def test_clean_dataframe():
    """It should clean a dataframe"""
    df = pd.DataFrame(
        [
            {"DATE OF BIRTH     ": 1991.0, "name": "Eric", "age": 26, "sex": "male"},
            {"DATE OF BIRTH     ": 1980.0, "name": "Samya", "age": 37, "sex": "female"},
            {"DATE OF BIRTH     ": 1988.0, "name": "Romain", "age": 29, "sex": "male"},
            {"DATE OF BIRTH     ": 1988.0, "name": "Fred", "age": 29, "sex": "male"},
            {"DATE OF BIRTH     ": 1990.0, "name": "Virginie", "age": 27, "sex": "female"},
            {"DATE OF BIRTH     ": 1991.0, "name": "Pierre", "age": 26, "sex": "male"},
            {"DATE OF BIRTH     ": 1999.0, "name": "Erwam", "age": 18, "sex": "male"},
            {"DATE OF BIRTH     ": 2000.0, "name": "Sophie", "age": 17, "sex": "female"},
            {"DATE OF BIRTH     ": 1970.0, "name": "Aurelie", "age": 47, "sex": "female"},
            {"DATE OF BIRTH     ": 1993.0, "name": "Jeremie", "age": 24, "sex": "male"},
            {"DATE OF BIRTH     ": 1973.0, "name": "Emilie", "age": 44, "sex": "female"},
        ]
    )
    df = clean_dataframe(df, threshold=5, rename_cols={"name": "surname"})

    assert set(df.columns) == {"date-of-birth", "surname", "age", "sex"}
    assert df["date-of-birth"].dtype == "int"
    assert df["sex"].dtype == "category"

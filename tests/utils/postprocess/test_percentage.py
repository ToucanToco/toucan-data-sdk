import pandas as pd

from toucan_data_sdk.utils.postprocess import percentage


def test_percentage():
    """ It should add a column `number_percentage` to the dataframe """
    data = pd.DataFrame(
        [
            {'gender': 'male', 'sport': 'bicycle', 'number': 17},
            {'gender': 'female', 'sport': 'basketball', 'number': 17},
            {'gender': 'male', 'sport': 'basketball', 'number': 3},
            {'gender': 'female', 'sport': 'football', 'number': 7},
            {'gender': 'female', 'sport': 'running', 'number': 30},
            {'gender': 'male', 'sport': 'running', 'number': 20},
            {'gender': 'male', 'sport': 'football', 'number': 21},
            {'gender': 'female', 'sport': 'bicycle', 'number': 17},
        ]
    )

    # ~~~ without group_cols ~~~
    kwargs = {'new_column': 'number_percentage', 'column': 'number'}
    res = percentage(data, **kwargs)
    assert res['number_percentage'].tolist()[0] == 1700 / 132
    assert res['number_percentage'].tolist()[2] == 300 / 132
    assert res['number_percentage'].tolist()[4] == 3000 / 132

    # ~~~ with group_cols ~~~
    kwargs = {'new_column': 'number_percentage', 'column': 'number', 'group_cols': ['sport']}
    res = percentage(data, **kwargs)
    expected_col = [50, 85, 15, 25, 60, 40, 75, 50]
    assert res['number_percentage'].tolist() == expected_col

    # ~~~ without new_columns ~~~
    kwargs = {'column': 'number', 'group_cols': ['sport']}
    res = percentage(data, **kwargs)
    expected_col = [50, 85, 15, 25, 60, 40, 75, 50]
    assert res['number'].tolist() == expected_col

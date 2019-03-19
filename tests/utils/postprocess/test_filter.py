import pandas as pd
from toucan_data_sdk.utils.postprocess import drop_duplicates, query


def test_query():
    """ It should return a filtered data dict """
    data = pd.DataFrame([{'value': 30}, {'value': 10}, {'value': 20}])
    config = {'query': 'value > 15'}
    filtered_data = pd.DataFrame([{'value': 30}, {'value': 20}], index=[0, 2])

    df = query(data, **config)
    assert df.equals(filtered_data)


def test_drop_duplicates():
    """It should drop duplicates"""
    df = pd.DataFrame({'a': [1, 2, 3, 1], 'b': [0, 0, 1, 1], 'c': [3, 3, 2, 2], 'd': [0, 1, 1, 0]})
    assert drop_duplicates(df, ['a']).shape == (3, 4)
    assert drop_duplicates(df, ['b', 'c']).shape == (2, 4)
    assert drop_duplicates(df, None).shape == (4, 4)

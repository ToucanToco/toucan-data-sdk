import pandas as pd
from toucan_data_sdk.utils.postprocess import query_df


def test_query_df():
    """ It should return a filtered data dict """
    data = pd.DataFrame([{'value': 30}, {'value': 10}, {'value': 20}])
    config = {'query': 'value > 15'}
    filtered_data = pd.DataFrame([{'value': 30}, {'value': 20}], index=[0, 2])

    df = query_df(data, **config)
    assert df.equals(filtered_data)

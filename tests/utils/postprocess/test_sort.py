import pandas as pd
from toucan_data_sdk.utils.postprocess import sort


def test_sort_values():
    """ It should sort dataframe """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 1, 'value': 300},
        {'variable': 'toto', 'Category': 1, 'value': 100},
        {'variable': 'toto', 'Category': 2, 'value': 250},
        {'variable': 'toto', 'Category': 2, 'value': 450}
    ])

    expected = [450, 250, 300, 100]
    output = sort(data, ['Category', 'value'], order='desc')
    assert output['value'].tolist() == expected

    expected = [100, 300, 250, 450]
    output = sort(data, ['Category', 'value'])
    assert output['value'].tolist() == expected

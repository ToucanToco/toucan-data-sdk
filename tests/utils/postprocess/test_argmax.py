import pandas as pd
from toucan_data_sdk.utils.postprocess import argmax


def test_argmax():
    """ It should return result for argmax """
    data = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450}])

    kwargs = {'column': 'year'}
    res = argmax(data, **kwargs)
    res = res.reset_index(drop=True)
    assert len(res) == 1
    assert res['year'][0] == 2016
    assert res['value'][0] == 450

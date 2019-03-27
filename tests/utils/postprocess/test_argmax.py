import pandas as pd
from toucan_data_sdk.utils.postprocess import argmax, argmin


def test_argmax():
    """ It should return result for argmax """
    data = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450}])

    kwargs = {'column': 'year'}
    res = argmax(data, **kwargs)
    assert len(res) == 1
    assert res['year'][0] == 2016
    assert res['value'][0] == 450


def test_argmin():
    """ It should return result for argmin """
    data = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450}])

    kwargs = {'column': 'year'}
    res = argmin(data, **kwargs)
    assert len(res) == 1
    assert res['year'][0] == 2014
    assert res['value'][0] == 300


def test_argmax_with_groups():
    """ It should return result for argmax """
    data = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450},
        {'variable': 'toto', 'wave': 'wave2', 'year': 2014, 'value': 500},
        {'variable': 'toto', 'wave': 'wave2', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave2', 'year': 2016, 'value': 100}
    ])

    kwargs = {'column': 'value', 'groups': ['variable', 'wave']}
    res = argmax(data, **kwargs)
    assert len(res) == 2
    assert res['wave'][0] == 'wave1'
    assert res['year'][0] == 2016
    assert res['value'][0] == 450
    assert res['wave'][1] == 'wave2'
    assert res['year'][1] == 2014
    assert res['value'][1] == 500
    assert len(res.columns) == 4


def test_argmin_with_groups():
    """ It should return result for argmin """
    data = pd.DataFrame([
        {'variable': 'toto', 'wave': 'wave1', 'year': 2014, 'value': 300},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave1', 'year': 2016, 'value': 450},
        {'variable': 'toto', 'wave': 'wave2', 'year': 2014, 'value': 500},
        {'variable': 'toto', 'wave': 'wave2', 'year': 2015, 'value': 250},
        {'variable': 'toto', 'wave': 'wave2', 'year': 2016, 'value': 100}
    ])

    kwargs = {'column': 'value', 'groups': ['variable', 'wave']}
    res = argmin(data, **kwargs)
    assert len(res) == 2
    assert res['wave'][0] == 'wave1'
    assert res['year'][0] == 2015
    assert res['value'][0] == 250
    assert res['wave'][1] == 'wave2'
    assert res['year'][1] == 2016
    assert res['value'][1] == 100
    assert len(res.columns) == 4

import pandas as pd
import pytest
from numpy import inf, nan, testing

from toucan_data_sdk.utils.postprocess import waterfall


@pytest.fixture
def sample_data():
    return [
        {'ord': 1, 'category_name': 'Clap', 'category_id': 'clap', 'product_id': 'super clap',
         'date': 't1', 'played': 12},
        {'ord': 10, 'category_name': 'Clap', 'category_id': 'clap', 'product_id': 'clap clap',
         'date': 't1', 'played': 1},
        {'ord': 1, 'category_name': 'Snare', 'category_id': 'snare', 'product_id': 'tac',
         'date': 't1', 'played': 1},
        {'ord': 1, 'category_name': 'Clap', 'category_id': 'clap', 'product_id': 'super clap',
         'date': 't2', 'played': 10},
        {'ord': 1, 'category_name': 'Snare', 'category_id': 'snare', 'product_id': 'tac',
         'date': 't2', 'played': 100},
        {'ord': 1, 'category_name': 'Tom', 'category_id': 'tom', 'product_id': 'bom',
         'date': 't2', 'played': 1}
    ]


def test_waterfall(sample_data):
    """ It should return value for waterfall """
    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'insideGroup': {'id': 'product_id', 'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    expected = [
        {'variation': nan, 'label': 'Trimestre 1', 'value': 14.0,
         'groups': 'Trimestre 1', 'type': nan, 'order': nan},
        {'variation': -0.23076923076923078, 'label': 'Clap', 'value': -3.0,
         'groups': 'clap', 'type': 'parent', 'order': nan},
        {'variation': -0.16666666666666666, 'label': 'super clap', 'value': -2.0,
         'groups': 'clap', 'type': 'child', 'order': 1.0},
        {'variation': -1.000000, 'label': 'clap clap', 'value': -1.0,
         'groups': 'clap', 'type': 'child', 'order': 10.0},
        {'variation': 99.0, 'label': 'Snare', 'value': 99.0,
         'groups': 'snare', 'type': 'parent', 'order': nan},
        {'variation': 99.0, 'label': 'tac', 'value': 99.0,
         'groups': 'snare', 'type': 'child', 'order': 1.0},
        {'variation': inf, 'label': 'Tom', 'value': 1.0,
         'groups': 'tom', 'type': 'parent', 'order': nan},
        {'variation': inf, 'label': 'bom', 'value': 1.0,
         'groups': 'tom', 'type': 'child', 'order': 1.0},
        {'variation': nan, 'label': 'Trimester 2', 'value': 111.0,
         'groups': 'Trimester 2', 'type': nan, 'order': nan}
    ]
    df = pd.DataFrame(sample_data)

    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        testing.assert_equal(wa[i], expected[i])


def test_waterfall_upperGroup_groupsOrder(sample_data):
    for line in sample_data:
        line['category_order'] = len(line['category_name'])
        del line['ord']

    kwargs = {
        'upperGroup': {
            'id': 'category_id',
            'label': 'category_name',
            'groupsOrder': 'category_order'
        },
        'insideGroup': {
            'id': 'product_id'
        },
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    expected = [
        {'variation': nan, 'label': 'Trimestre 1', 'value': 14.0, 'groups': 'Trimestre 1',
         'type': nan, 'order': nan},
        {'variation': inf, 'label': 'Tom', 'value': 1.0, 'groups': 'tom', 'type': 'parent',
         'order': 3.0},
        {'variation': inf, 'label': 'bom', 'value': 1.0, 'groups': 'tom', 'type': 'child',
         'order': nan},
        {'variation': -0.23076923076923078, 'label': 'Clap', 'value': -3.0, 'groups': 'clap',
         'type': 'parent', 'order': 4.0},
        {'variation': -1.0, 'label': 'clap clap', 'value': -1.0, 'groups': 'clap',
         'type': 'child', 'order': nan},
        {'variation': -0.16666666666666666, 'label': 'super clap', 'value': -2.0,
         'groups': 'clap', 'type': 'child', 'order': nan},
        {'variation': 99.0, 'label': 'Snare', 'value': 99.0, 'groups': 'snare',
         'type': 'parent', 'order': 5.0},
        {'variation': 99.0, 'label': 'tac', 'value': 99.0, 'groups': 'snare', 'type': 'child',
         'order': nan},
        {'variation': nan, 'label': 'Trimester 2', 'value': 111.0, 'groups': 'Trimester 2',
         'type': nan, 'order': nan}
    ]

    df = pd.DataFrame(sample_data)
    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        testing.assert_equal(wa[i], expected[i])


def test_waterfall_no_value_start():
    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'insideGroup': {'id': 'product_id', 'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    data = [
        {'ord': 1, 'category_name': 'Clap', 'category_id': 'clap',
         'product_id': 'super clap', 'date': 't2', 'played': 10},
        {'ord': 1, 'category_name': 'Snare', 'category_id': 'snare',
         'product_id': 'tac', 'date': 't2', 'played': 100},
        {'ord': 1, 'category_name': 'Tom', 'category_id': 'tom',
         'product_id': 'bom', 'date': 't2', 'played': 1}
    ]

    expected = [
        {'variation': nan, 'label': 'Trimestre 1', 'value': 0, 'groups': 'Trimestre 1',
         'type': nan, 'order': nan},
        {'variation': inf, 'label': 'Clap', 'value': 10, 'groups': 'clap', 'type': 'parent',
         'order': nan},
        {'variation': inf, 'label': 'super clap', 'value': 10, 'groups': 'clap',
         'type': 'child', 'order': 1.0},
        {'variation': inf, 'label': 'Snare', 'value': 100.0, 'groups': 'snare',
         'type': 'parent', 'order': nan},
        {'variation': inf, 'label': 'tac', 'value': 100.0, 'groups': 'snare', 'type': 'child',
         'order': 1.0},
        {'variation': inf, 'label': 'Tom', 'value': 1.0, 'groups': 'tom', 'type': 'parent',
         'order': nan},
        {'variation': inf, 'label': 'bom', 'value': 1.0, 'groups': 'tom', 'type': 'child',
         'order': 1.0},
        {'variation': nan, 'label': 'Trimester 2', 'value': 111.0, 'groups': 'Trimester 2',
         'type': nan, 'order': nan}
    ]
    df = pd.DataFrame(data)
    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        testing.assert_equal(wa[i], expected[i])


def test_waterfall_null():
    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'insideGroup': {'id': 'product_id', 'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    data = None
    df = pd.DataFrame(data)
    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa == []


def test_waterfall_not_implemented(sample_data):
    """ It should raise Error for not implemented features """
    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'insideGroup': {'id': 'product_id', 'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
        'breakdown': ['id']
    }
    df = pd.DataFrame(sample_data)
    with pytest.raises(NotImplementedError) as exc_info:
        waterfall(df, **kwargs)
    assert str(exc_info.value) == 'We will add breakdown support ' \
                                  'on your request, please contact the devs'

    kwargs = {
        'upperGroup': {'id': 'category_id', 'label': 'category_name'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }


def test_waterfall_upperGroup_only(sample_data):
    kwargs = {
        'upperGroup': {
            'id': 'product_id',
            'groupsOrder': 'ord'},
        'date': 'date',
        'value': 'played',
        'start': {'label': 'Trimestre 1', 'id': 't1'},
        'end': {'label': 'Trimester 2', 'id': 't2'},
    }

    expected = [
        {'variation': nan, 'label': 'Trimestre 1', 'value': 14.0, 'groups': 'Trimestre 1',
         'type': nan, 'order': nan},
        {'variation': inf, 'label': 'bom', 'value': 1.0, 'groups': 'bom', 'type': 'parent',
         'order': 1},
        {'variation': -0.16666666666666666, 'label': 'super clap', 'value': -2.0,
         'groups': 'super clap', 'type': 'parent', 'order': 1},
        {'variation': 99.0, 'label': 'tac', 'value': 99.0, 'groups': 'tac', 'type': 'parent',
         'order': 1},
        {'variation': -1.000000, 'label': 'clap clap', 'value': -1.0,
         'groups': 'clap clap', 'type': 'parent', 'order': 10},
        {'variation': nan, 'label': 'Trimester 2', 'value': 111.0, 'groups': 'Trimester 2',
         'type': nan, 'order': nan}
    ]

    df = pd.DataFrame(sample_data)

    df = waterfall(df, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        testing.assert_equal(wa[i], expected[i])

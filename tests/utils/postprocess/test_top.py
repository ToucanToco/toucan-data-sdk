import pandas as pd
from toucan_data_sdk.utils.postprocess import top, top_group
from collections import OrderedDict


def test_top():
    """ It should return result for top """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 1, 'value': 100},
        {'variable': 'toto', 'Category': 1, 'value': 200},
        {'variable': 'toto', 'Category': 1, 'value': 300},
        {'variable': 'lala', 'Category': 1, 'value': 100},
        {'variable': 'lala', 'Category': 1, 'value': 150},
        {'variable': 'lala', 'Category': 1, 'value': 250},
        {'variable': 'lala', 'Category': 2, 'value': 350},
        {'variable': 'lala', 'Category': 2, 'value': 450}
    ])

    # ~~~ without group ~~~
    expected = [
        {'variable': 'lala', 'Category': 2, 'value': 450},
        {'variable': 'lala', 'Category': 2, 'value': 350},
        {'variable': 'toto', 'Category': 1, 'value': 300}
    ]

    kwargs = {
        "value": 'value',
        "limit": 3,
        "order": "desc"
    }
    df = top(data, **kwargs).reset_index(drop=True)
    assert pd.DataFrame(expected).equals(df)

    # ~~~ with group ~~~
    expected = [
        {'variable': 'lala', 'Category': 1, 'value': 150},
        {'variable': 'lala', 'Category': 1, 'value': 100},
        {'variable': 'lala', 'Category': 2, 'value': 450},
        {'variable': 'lala', 'Category': 2, 'value': 350},
        {'variable': 'toto', 'Category': 1, 'value': 200},
        {'variable': 'toto', 'Category': 1, 'value': 100}
    ]
    kwargs = {
        "group": ['variable', "Category"],
        "value": 'value',
        "limit": -2,
        "order": "desc"
    }
    df = top(data, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        assert wa[i] == expected[i]

    kwargs = {
        "group": ['variable', "Category"],
        "value": 'value',
        "limit": '-2',
        "order": "desc"
    }
    df = top(data, **kwargs)
    wa = [{k: v for k, v in zip(df.columns, row)} for row in df.values]
    assert wa[0].keys() == expected[0].keys()
    for i in range(len(expected)):
        assert wa[i] == expected[i]


def test_top_group():
    """ It should return result for top_group """
    data = pd.DataFrame({
        'Label': ['G1', 'G2', 'G3', 'G4', 'G5', 'G3', 'G3'],
        'Categories': ['C1', 'C2', 'C1', 'C2', 'C1', 'C2', 'C3'],
        'Valeurs': [6, 1, 9, 4, 8, 2, 5],
        'Periode': ['mois', 'mois', 'mois', 'semaine', 'semaine', 'semaine', 'semaine']
    })

    # ~~~ with filters ~~~
    expected = pd.DataFrame(OrderedDict({
        'Periode': ['mois', 'mois', 'semaine', 'semaine', 'semaine'],
        'Label': ['G3', 'G1', 'G5', 'G3', 'G3'],
        'Categories': ['C1', 'C1', 'C1', 'C2', 'C3'],
        'Valeurs': [9, 6, 8, 2, 5]
    }))

    kwargs = {
        "group": ["Periode"],
        "value": 'Valeurs',
        "aggregate_by": ["Label"],
        "limit": 2,
        "order": "desc"

    }

    df = top_group(data, **kwargs).reset_index(drop=True)
    assert pd.DataFrame(expected).equals(df)

    # ~~~ without groups ~~~
    expected = pd.DataFrame(OrderedDict({
        'Label': ['G3', 'G3', 'G3', 'G5'],
        'Categories': ['C1', 'C2', 'C3', 'C1'],
        'Periode': ['mois', 'semaine', 'semaine', 'semaine'],
        'Valeurs': [9, 2, 5, 8]
    }))

    kwargs = {
        "group": None,
        "value": 'Valeurs',
        "aggregate_by": ["Label"],
        "limit": 2,
        "order": "desc"

    }

    df = top_group(data, **kwargs).reset_index(drop=True)
    assert pd.DataFrame(expected).equals(df)

    # ~~~ with group and function = mean ~~~
    expected = pd.DataFrame(OrderedDict({
        'Periode': ['mois', 'mois', 'semaine', 'semaine'],
        'Label': ['G3', 'G1', 'G5', 'G4'],
        'Categories': ['C1', 'C1', 'C1', 'C2'],
        'Valeurs': [9, 6, 8, 4]
    }))

    kwargs = {
        "group": ["Periode"],
        "value": 'Valeurs',
        "aggregate_by": ["Label"],
        "limit": 2,
        "function": "mean",
        "order": "desc"

    }

    df = top_group(data, **kwargs).reset_index(drop=True)
    assert pd.DataFrame(expected).equals(df)

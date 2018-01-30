import pandas as pd
from toucan_data_sdk.utils.postprocess import top


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

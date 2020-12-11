import pandas as pd

from toucan_data_sdk.utils.postprocess.linear_regression import predict_linear


def test_predict_linear():
    """
    check that predict_linear correctly predict values & return confidence intervall
    """
    test_df = pd.DataFrame(
        {
            'date': [
                '01-01-2020',
                '02-01-2020',
                '03-01-2020',
                '04-01-2020',
                '05-01-2020',
                '01-01-2021',
                '02-01-2021',
                '03-01-2021',
            ],
            'value': [1.0, 4.6, 11, 13.2, 15, None, None, None],
            'plop': ['bla', 'bla', 'bla', 'bouh', 'buzz', 'bah', 'bog', 'yeah'],
        }
    )
    result = predict_linear(test_df, variable_column='date', target_column='value')
    assert result.columns.tolist() == [
        'date',
        'value',
        'value_is_prediction',
        'value_lower_bound',
        'value_higher_bound',
    ]
    assert len(result) == 8
    assert result['date'].tolist() == [
        '01-01-2020',
        '02-01-2020',
        '03-01-2020',
        '04-01-2020',
        '05-01-2020',
        '01-01-2021',
        '02-01-2021',
        '03-01-2021',
    ]
    test_df = pd.DataFrame(
        {
            'date': [
                '01-2020',
                '02-2020',
                '03-2020',
                '04-2020',
                '05-2020',
                '01-2021',
                '02-2021',
                '03-2021',
            ],
            'value': [2, 13, 9, 10, 9, None, None, None],
            'plop': ['bla', 'bla', 'bla', 'bouh', 'buzz', 'bah', 'bog', 'yeah'],
        }
    )
    result = predict_linear(test_df, variable_column='date', target_column='value')
    assert result.columns.tolist() == [
        'date',
        'value',
        'value_is_prediction',
        'value_lower_bound',
        'value_higher_bound',
    ]
    assert len(result) == 8
    assert result['date'].tolist() == [
        '01-2020',
        '02-2020',
        '03-2020',
        '04-2020',
        '05-2020',
        '01-2021',
        '02-2021',
        '03-2021',
    ]

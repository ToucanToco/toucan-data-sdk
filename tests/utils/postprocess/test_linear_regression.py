import pandas as pd

from toucan_data_sdk.utils.postprocess.linear_regression import predict_linear


def test_predict_linear():
    """
    check that predict_linear correctly predict values & return confidence intervall
    """
    test_df = pd.DataFrame(
        {
            'date': ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug'],
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
    assert result['date'].tolist() == ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug']

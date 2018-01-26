import pandas as pd

from toucan_data_sdk.utils.postprocess import (
    add, subtract, multiply, divide
)


def test_math_operations():
    """ It should return result for basic math operations """
    data = pd.DataFrame([{'value1': 10, 'value2': 20},
                         {'value1': 17, 'value2': 5}])

    kwargs = {'new_column': 'result', 'column_1': 'value1', 'column_2': 'value2'}

    res = add(data, **kwargs)
    expected_col = [30, 22]
    assert res['result'].tolist() == expected_col

    res = subtract(data, **kwargs)
    expected_col = [-10, 12]
    assert res['result'].tolist() == expected_col

    res = multiply(data, **kwargs)
    expected_col = [200, 85]
    assert res['result'].tolist() == expected_col

    res = divide(data, **kwargs)
    expected_col = [.5, 3.4]
    assert res['result'].tolist() == expected_col

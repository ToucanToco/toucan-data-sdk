import pandas as pd
from toucan_data_sdk.utils.postprocess import sort
import pytest


def test_sort_values_invalid_order_parameter():
    """ It should sort dataframe """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 2, 'value': 300},
        {'variable': 'toto', 'Category': 3, 'value': 100},
        {'variable': 'toto', 'Category': 4, 'value': 250},
        {'variable': 'toto', 'Category': 1, 'value': 450}
    ])

    with pytest.raises(AssertionError):
        sort(data, 'Category', order='whatever')


def test_sort_values_invalid_parameters_length():
    """ It should sort dataframe """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 2, 'value': 300},
        {'variable': 'toto', 'Category': 3, 'value': 100},
        {'variable': 'toto', 'Category': 4, 'value': 250},
        {'variable': 'toto', 'Category': 1, 'value': 450}
    ])

    with pytest.raises(AssertionError):
        sort(data, ["variable", 'Category'], order=['asc'])


def test_sort_values_simple():
    """ It should sort dataframe """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 2, 'value': 300},
        {'variable': 'toto', 'Category': 3, 'value': 100},
        {'variable': 'toto', 'Category': 4, 'value': 250},
        {'variable': 'toto', 'Category': 1, 'value': 450}
    ])

    expected = [450, 300, 100, 250]
    output = sort(data, 'Category', order='asc')
    assert output['value'].tolist() == expected


def test_sort_values_simple_no_order():
    """ It should sort dataframe """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 2, 'value': 300},
        {'variable': 'toto', 'Category': 3, 'value': 100},
        {'variable': 'toto', 'Category': 4, 'value': 250},
        {'variable': 'toto', 'Category': 1, 'value': 450}
    ])

    expected = [450, 300, 100, 250]
    output = sort(data, 'Category')
    assert output['value'].tolist() == expected


def test_sort_values_multiple_column_order_desc():
    """ It should sort dataframe """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 1, 'value': 300},
        {'variable': 'toto', 'Category': 2, 'value': 100},
        {'variable': 'tata', 'Category': 2, 'value': 250},
        {'variable': 'tata', 'Category': 1, 'value': 450}
    ])

    expected = [100, 300, 250, 450]
    output = sort(data, ['variable', 'Category'], order='desc')
    assert output['value'].tolist() == expected


def test_sort_values_multiple_columns():
    """ It should sort dataframe """
    data = pd.DataFrame([
        {'variable': 'toto', 'Category': 1, 'value': 300},
        {'variable': 'toto', 'Category': 2, 'value': 100},
        {'variable': 'tata', 'Category': 2, 'value': 250},
        {'variable': 'tata', 'Category': 1, 'value': 450}
    ])

    expected = [250, 450, 100, 300]
    output = sort(data, ['variable', 'Category'], order=['asc', 'desc'])
    assert output['value'].tolist() == expected

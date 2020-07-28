from datetime import date, timedelta

import pandas as pd
import pytest

from toucan_data_sdk.utils.postprocess import categories_from_dates

from .test_filter_by_date import assert_frame_equal_noindex

BEFORE_YESTERDAY = (date.today() - timedelta(days=2)).strftime('%Y-%m-%d')
YESTERDAY = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
TODAY = date.today().strftime('%Y-%m-%d')
TOMORROW = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')


@pytest.fixture
def sample_data():
    return [
        {'date': '2018-01-28', 'value': 0},
        {'date': '2018-01-28', 'value': 1},
        {'date': '2018-01-29', 'value': 2},
        {'date': '2018-01-30', 'value': 3},
        {'date': '2018-01-31', 'value': 4},
        {'date': '2018-02-01', 'value': 5},
        {'date': '2018-02-02', 'value': 6},
        {'date': YESTERDAY, 'value': 7},
        {'date': TODAY, 'value': 8},
        {'date': TOMORROW, 'value': 9},
        {'date': BEFORE_YESTERDAY, 'value': 10},
    ]


def test_categories_from_dates_invalid_calls(sample_data):
    """It should forbid invalid start/stop/atdate combinations"""
    df = pd.DataFrame(sample_data)
    with pytest.raises(TypeError):
        # range_steps is empty
        categories_from_dates(df, 'date', 'my_categories', range_steps=[])
    with pytest.raises(TypeError):
        # category_names should have length 2
        categories_from_dates(
            df, 'date', 'my_categories', range_steps=['2018-01-01'], category_names=['A']
        )
    with pytest.raises(ValueError):
        # bad date format
        categories_from_dates(
            df, 'date', 'my_categories', range_steps=['2018-01-01'], date_format='%m %Y'
        )
    with pytest.raises(ValueError):
        # bad date format
        categories_from_dates(
            df, 'date', 'my_categories', range_steps=['01 2018'], date_format='%m %Y'
        )
    with pytest.raises(ValueError):
        # bad offset syntax (missing parenthesis)
        categories_from_dates(
            df, 'date', 'my_categories', range_steps=['2018-01-01 + 1day'], date_format='%m %Y'
        )


def test_categories_from_dates(sample_data):
    """It should create a new column 'my_categories'"""
    df = pd.DataFrame(sample_data)
    df = categories_from_dates(
        df, 'date', 'my_categories', range_steps=['2018-01-31', '2018-02-03']
    )
    expected = df.copy()
    expected['my_categories'] = [
        'Category 1',
        'Category 1',
        'Category 1',
        'Category 1',
        'Category 2',
        'Category 2',
        'Category 2',
        'Category 3',
        'Category 3',
        'Category 3',
        'Category 3',
    ]
    assert_frame_equal_noindex(df, expected)


def test_categories_from_dates_with_offset(sample_data):
    """It should create a new column 'my_categories'"""
    df = pd.DataFrame(sample_data)
    expected = df.copy()
    expected['my_categories'] = [
        'Category 1',
        'Category 1',
        'Category 1',
        'Category 1',
        'Category 1',
        'Category 1',
        'Category 1',
        'Category 2',
        'Category 3',
        'Category 3',
        'Category 2',
    ]
    df = categories_from_dates(df, 'date', 'my_categories', range_steps=['(TODAY)-10days', 'TODAY'])
    assert_frame_equal_noindex(df, expected)


def test_categories_from_dates_with_category_names(sample_data):
    """It should create a new column 'my_categories'"""
    df = pd.DataFrame(sample_data)
    expected = df.copy()
    expected['my_categories'] = [
        'Old',
        'Old',
        'Old',
        'Old',
        'Old',
        'Old',
        'Old',
        'Recent',
        'Recent',
        'Futur',
        'Recent',
    ]
    df = categories_from_dates(
        df,
        'date',
        'my_categories',
        range_steps=['(TODAY)-10days', '(TODAY)+1days'],
        category_names=['Old', 'Recent', 'Futur'],
    )
    assert_frame_equal_noindex(df, expected)

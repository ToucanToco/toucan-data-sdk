from datetime import date, timedelta

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from toucan_data_sdk.utils.postprocess import filter_by_date
from toucan_data_sdk.utils.postprocess.filter_by_date import parse_date


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


def assert_frame_equal_noindex(left, right):
    """compare dataframes but ignore index values.

    This is useful to compare filtered out dataframes with a manually
    built one.
    """
    assert_frame_equal(left.reset_index(drop=True), right.reset_index(drop=True))


def test_filter_date_invalid_calls(sample_data):
    """It should forbid invalid start/stop/atdate combinations"""
    df = pd.DataFrame(sample_data)
    with pytest.raises(TypeError):
        # no filter specification
        filter_by_date(df, 'date')
    with pytest.raises(TypeError):
        # start, stop and atdate can't be all specified
        filter_by_date(df, 'date', start='2018-01-01', stop='2018-01-01', atdate='2018-01-01')
    with pytest.raises(TypeError):
        # start and atdate are mutually exclusive
        filter_by_date(df, 'date', start='2018-01-01', atdate='2018-01-01')
    with pytest.raises(TypeError):
        # stop and atdate are mutually exclusive
        filter_by_date(df, 'date', stop='2018-01-01', atdate='2018-01-01')
    with pytest.raises(ValueError):
        # bad date format
        filter_by_date(df, 'date', start='2018-01-01', date_fmt='%m %Y')
    with pytest.raises(ValueError):
        # bad date format
        filter_by_date(df, 'date', start='01 2018', date_fmt='%m %Y')
    with pytest.raises(ValueError):
        # bad offset syntax (missing parenthesis)
        filter_by_date(df, 'date', start='2018-01-01 + 1day', date_fmt='%m %Y')


def test_filter_by_date_atdate(sample_data):
    """It should filter rows on a specific date"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', atdate='2018-01-28')
    expected = pd.DataFrame([
        {'date': '2018-01-28', 'value': 0},
        {'date': '2018-01-28', 'value': 1},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_start_only(sample_data):
    """It should filter rows after a specific date"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', start='2018-01-30')
    expected = pd.DataFrame([
        {'date': '2018-01-30', 'value': 3},
        {'date': '2018-01-31', 'value': 4},
        {'date': '2018-02-01', 'value': 5},
        {'date': '2018-02-02', 'value': 6},
        {'date': YESTERDAY, 'value': 7},
        {'date': TODAY, 'value': 8},
        {'date': TOMORROW, 'value': 9},
        {'date': BEFORE_YESTERDAY, 'value': 10},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_start_only_with_offset(sample_data):
    """It should filter rows after a specific date with offset"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', start='(2018-01-30) + 2days')
    expected = pd.DataFrame([
        {'date': '2018-02-01', 'value': 5},
        {'date': '2018-02-02', 'value': 6},
        {'date': YESTERDAY, 'value': 7},
        {'date': TODAY, 'value': 8},
        {'date': TOMORROW, 'value': 9},
        {'date': BEFORE_YESTERDAY, 'value': 10},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_stop_only(sample_data):
    """It should keep rows before a specific date"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', stop='2018-01-30')
    expected = pd.DataFrame([
        {'date': '2018-01-28', 'value': 0},
        {'date': '2018-01-28', 'value': 1},
        {'date': '2018-01-29', 'value': 2},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_stop_only_with_offset(sample_data):
    """It should keep rows before a specific date with offset"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', stop='(2018-01-30) - 1d')
    expected = pd.DataFrame([
        {'date': '2018-01-28', 'value': 0},
        {'date': '2018-01-28', 'value': 1},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_range(sample_data):
    """It should keep rows on a specific range"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', start='2018-01-28', stop='2018-02-02')
    expected = pd.DataFrame([
        {'date': '2018-01-28', 'value': 0},
        {'date': '2018-01-28', 'value': 1},
        {'date': '2018-01-29', 'value': 2},
        {'date': '2018-01-30', 'value': 3},
        {'date': '2018-01-31', 'value': 4},
        {'date': '2018-02-01', 'value': 5},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_range_with_offsets(sample_data):
    """It should keep rows on a specific range with offsets"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', start='(2018-01-28)+1d', stop='(2018-02-02)-2d')
    expected = pd.DataFrame([
        {'date': '2018-01-29', 'value': 2},
        {'date': '2018-01-30', 'value': 3},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_start_symbolic_today(sample_data):
    """It should understand 'TODAY' as a valid start date"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', atdate='TODAY')
    expected = pd.DataFrame([
        {'date': TODAY, 'value': 8},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_start_symbolic_today_and_offset(sample_data):
    """It should understand 'TODAY' with offset as a valid start date"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', start='(TODAY) + 1d')
    expected = pd.DataFrame([
        {'date': TOMORROW, 'value': 9},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_start_symbolic_yesterday(sample_data):
    """It should understand 'YESTERDAY' as a valid start date"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', atdate='YESTERDAY')
    expected = pd.DataFrame([
        {'date': YESTERDAY, 'value': 7},
    ])
    assert_frame_equal_noindex(df, expected)


def test_filter_by_date_start_symbolic_tomorrow(sample_data):
    """It should understand 'TOMORROW' as a valid start date"""
    df = pd.DataFrame(sample_data)
    df = filter_by_date(df, 'date', atdate='TOMORROW')
    expected = pd.DataFrame([
        {'date': TOMORROW, 'value': 9},
    ])
    assert_frame_equal_noindex(df, expected)


def test_date_fmt():
    """It should take date_fmt into account"""
    df = pd.DataFrame([
        {'date': '01 2018', 'value': 1},
        {'date': '03 2018', 'value': 2},
        {'date': '03 2018', 'value': 3}
    ])
    df = filter_by_date(df, date_col='date', date_fmt='%m %Y', start='(02 2018)+10d')
    expected = pd.DataFrame([
        {'date': '03 2018', 'value': 2},
        {'date': '03 2018', 'value': 3}
    ])
    assert_frame_equal_noindex(df, expected)


def test_parse_date():
    """It should be able to parse dates."""
    assert parse_date('2018-01-02', '%Y-%m-%d') == date(2018, 1, 2)
    assert parse_date('2018 01', '%Y %m') == date(2018, 1, 1)
    assert parse_date('(2018-01-02)', '%Y-%m-%d') == date(2018, 1, 2)
    assert parse_date('(2018-01-02)+1d', '%Y-%m-%d') == date(2018, 1, 3)
    assert parse_date('(2018-01-02) + 1d', '%Y-%m-%d') == date(2018, 1, 3)
    assert parse_date('(2018-01-02)-1d', '%Y-%m-%d') == date(2018, 1, 1)
    assert parse_date('(2018-01-02) - 1d', '%Y-%m-%d') == date(2018, 1, 1)
    assert parse_date('TODAY', '%Y-%m-%d') == date.today()
    yesterday = date.today() - timedelta(days=1)
    tomorrow = date.today() + timedelta(days=1)
    assert parse_date('(TODAY) + 1day', '%Y-%m-%d') == tomorrow
    assert parse_date('(TODAY) - 1day', '%Y-%m-%d') == yesterday

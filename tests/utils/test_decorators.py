import pandas as pd
import pytest

from toucan_data_sdk.utils.decorators import _logger as catch_logger
from toucan_data_sdk.utils.decorators import domain, log, log_message, log_shapes, log_time


def test_log_time(mocker):
    logger = mocker.MagicMock()

    @log_time(logger)
    def foo():
        pass

    foo()
    logger.info.assert_called_once()
    args = logger.info.call_args[0]
    assert 'foo' in args[0]

    logger.info.side_effect = ZeroDivisionError
    mock_warning = mocker.patch.object(catch_logger, 'warning')
    foo()
    mock_warning.assert_called_once()
    args = mock_warning.call_args[0]
    assert 'Exception raised in decorator' in args[0]


def test_log_shapes(mocker):
    logger = mocker.MagicMock()

    @log_shapes(logger)
    def foo(df):
        pass

    df = pd.DataFrame({'values': [1, 2, 3]})
    foo(df)
    logger.info.assert_called_once()
    args = logger.info.call_args[0]
    assert 'foo' in args[0]
    assert repr(df.shape) in args[0]


def test_log_message(mocker):
    logger = mocker.MagicMock()

    @log_message(logger, "yolo")
    def foo():
        pass

    foo()
    logger.info.assert_called_once()
    args = logger.info.call_args[0]
    assert 'foo' in args[0]
    assert 'yolo' in args[0]


def test_log(mocker):
    mylogger = mocker.NonCallableMock()
    default_log_info = mocker.spy(catch_logger, 'info')

    # Default logger
    @log
    def a_random_function():
        pass

    a_random_function()

    mylogger.assert_not_called()
    assert [call[0][0] for call in default_log_info.call_args_list] == [
        'a_random_function - Starting...',
        'a_random_function - Done... (took 0.00s)',
    ]
    default_log_info.reset_mock()

    # Custom logger
    @log(mylogger)
    def a_random_function():
        pass

    a_random_function()

    default_log_info.assert_not_called()
    assert [call[0][0] for call in mylogger.info.call_args_list] == [
        'a_random_function - Starting...',
        'a_random_function - Done... (took 0.00s)',
    ]
    mylogger.reset_mock()

    @log(start_message='Hello !', logger=mylogger, end_message='Bye !')
    def a_random_function():
        pass

    a_random_function()

    default_log_info.assert_not_called()
    assert [call[0][0] for call in mylogger.info.call_args_list] == [
        'a_random_function - Hello !',
        'a_random_function - Bye ! (took 0.00s)',
    ]


def test_domain():
    @domain('domain1')
    def process_domain1(df):
        return df + df

    dfs = {'domain1': pd.DataFrame({'x': [1, 2, 3]})}
    dfs = process_domain1(dfs)
    assert list(dfs['domain1'].x) == [2, 4, 6]

    with pytest.raises(TypeError):
        process_domain1(42)
